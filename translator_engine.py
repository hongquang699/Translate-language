"""
translator_engine.py
Core module managing translation engine, long text chunking,
bilingual (EN/VI) language mappings, and retry logic for Google Translate.
"""

import os
import time
import re
from typing import List, Dict, Tuple, Optional, Callable
from deep_translator import GoogleTranslator

def _load_env_safely():
    """Safely loads variables from local .env file if present without leaking secrets."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except Exception:
            pass

_load_env_safely()

# Popular languages mapping in English
POPULAR_LANGUAGES_EN = {
    "en": "English",
    "vi": "Vietnamese",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "th": "Thai",
    "lo": "Lao",
    "km": "Khmer",
    "id": "Indonesian",
    "ms": "Malay",
    "it": "Italian",
    "pt": "Portuguese",
    "ar": "Arabic",
    "hi": "Hindi",
    "tr": "Turkish",
}

# Popular languages mapping in Vietnamese
POPULAR_LANGUAGES_VI = {
    "vi": "Tiếng Việt (Vietnamese)",
    "en": "Tiếng Anh (English)",
    "zh-CN": "Tiếng Trung Giản thể (Chinese Simp.)",
    "zh-TW": "Tiếng Trung Phồn thể (Chinese Trad.)",
    "ja": "Tiếng Nhật (Japanese)",
    "ko": "Tiếng Hàn (Korean)",
    "fr": "Tiếng Pháp (French)",
    "de": "Tiếng Đức (German)",
    "es": "Tiếng Tây Ban Nha (Spanish)",
    "ru": "Tiếng Nga (Russian)",
    "th": "Tiếng Thái (Thai)",
    "lo": "Tiếng Lào (Lao)",
    "km": "Tiếng Khmer (Khmer)",
    "id": "Tiếng Indonesia",
    "ms": "Tiếng Mã Lai (Malay)",
    "it": "Tiếng Ý (Italian)",
    "pt": "Tiếng Bồ Đào Nha (Portuguese)",
    "ar": "Tiếng Ả Rập (Arabic)",
    "hi": "Tiếng Hindi (Ấn Độ)",
    "tr": "Tiếng Thổ Nhĩ Kỳ (Turkish)",
}


def get_all_languages(ui_lang: str = "en") -> List[Tuple[str, str]]:
    """
    Returns a list of (Display Name, Language Code).
    Supports English ("en") or Vietnamese ("vi") display names.
    """
    try:
        raw_langs = GoogleTranslator().get_supported_languages(as_dict=True)
    except Exception:
        raw_langs = {
            "english": "en", "vietnamese": "vi", "chinese (simplified)": "zh-CN",
            "chinese (traditional)": "zh-TW", "japanese": "ja", "korean": "ko",
            "french": "fr", "german": "de", "spanish": "es", "russian": "ru",
            "thai": "th", "indonesian": "id", "italian": "it", "portuguese": "pt"
        }

    lang_list = []
    added_codes = set()
    pop_map = POPULAR_LANGUAGES_VI if ui_lang == "vi" else POPULAR_LANGUAGES_EN

    # Add popular languages first
    for code, display_name in pop_map.items():
        lang_list.append((display_name, code))
        added_codes.add(code.lower())

    # Add remaining languages from deep_translator
    other_langs = []
    for name, code in raw_langs.items():
        if code.lower() not in added_codes:
            formatted_name = name.title() + f" ({code})"
            other_langs.append((formatted_name, code))
            added_codes.add(code.lower())

    other_langs.sort(key=lambda x: x[0])
    return lang_list + other_langs


def split_text_into_chunks(text: str, max_chars: int = 3500) -> List[str]:
    """
    Splits long text into safe chunks (< max_chars)
    breaking at paragraph or sentence boundaries to preserve context.
    """
    if not text or len(text) <= max_chars:
        return [text] if text else []

    chunks = []
    paragraphs = text.split("\n")
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) + 1 <= max_chars:
            current_chunk.append(para)
            current_len += len(para) + 1
        else:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_len = 0

            # If single paragraph is longer than max_chars, split by sentence
            if len(para) > max_chars:
                sentences = re.split(r'(?<=[.!?。！？\n]) +', para)
                sub_chunk = []
                sub_len = 0
                for sent in sentences:
                    if sub_len + len(sent) + 1 <= max_chars:
                        sub_chunk.append(sent)
                        sub_len += len(sent) + 1
                    else:
                        if sub_chunk:
                            chunks.append(" ".join(sub_chunk))
                            sub_chunk = []
                            sub_len = 0
                        if len(sent) > max_chars:
                            for i in range(0, len(sent), max_chars):
                                chunks.append(sent[i:i + max_chars])
                        else:
                            sub_chunk.append(sent)
                            sub_len = len(sent)
                if sub_chunk:
                    chunks.append(" ".join(sub_chunk))
            else:
                current_chunk.append(para)
                current_len = len(para)

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def translate_text(
    text: str,
    target_lang: str = "en",
    source_lang: str = "auto",
    max_retries: int = 3,
    delay_between_chunks: float = 0.2,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> str:
    """
    Translates any input text into the target language.
    Handles chunking, errors, and retries automatically.
    """
    if not text or not text.strip():
        return text

    if source_lang == target_lang and source_lang != "auto":
        return text

    chunks = split_text_into_chunks(text, max_chars=3500)
    translated_chunks = []
    total_chunks = len(chunks)

    translator = GoogleTranslator(source=source_lang, target=target_lang)

    for idx, chunk in enumerate(chunks):
        if not chunk.strip():
            translated_chunks.append(chunk)
            continue

        success = False
        last_error = None
        for attempt in range(max_retries):
            try:
                translated_part = translator.translate(chunk)
                translated_chunks.append(translated_part or "")
                success = True
                break
            except Exception as e:
                last_error = e
                time.sleep(1.0 * (attempt + 1))

        if not success:
            translated_chunks.append(chunk)
            print(f"[Warning] Failed to translate chunk {idx + 1}/{total_chunks}: {last_error}")

        if progress_callback:
            progress_callback(idx + 1, total_chunks)

        if delay_between_chunks > 0 and idx < total_chunks - 1:
            time.sleep(delay_between_chunks)

    return "\n".join(translated_chunks)
