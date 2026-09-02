"""
file_handler.py
Module for handling diverse file formats:
- Plain text: .txt, .md, .log, .rtf, .tex
- Subtitles: .srt, .vtt
- Structured data: .csv, .json, .xml, .html
- Microsoft Office: .docx (Word), .xlsx (Excel), .pptx (PowerPoint)
- PDF Documents: .pdf
"""

import os
import io
import csv
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Callable, Optional, Tuple, List
from bs4 import BeautifulSoup
import openpyxl
import pypdf

from translator_engine import translate_text

# Supported formats categorized
SUPPORTED_EXTENSIONS = {
    "Documents / Plain Text": [".txt", ".md", ".rtf", ".log", ".tex"],
    "Video Subtitles": [".srt", ".vtt"],
    "Structured Data": [".csv", ".json", ".xml", ".html", ".htm"],
    "Microsoft Office": [".docx", ".xlsx", ".pptx"],
    "PDF Documents": [".pdf"],
}

ALL_EXTENSIONS = [ext for sublist in SUPPORTED_EXTENSIONS.values() for ext in sublist]


def get_output_filepath(input_path: str, target_lang: str, custom_output_dir: Optional[str] = None) -> str:
    """
    Generates output file path with language suffix, e.g., 'report_en.docx'
    """
    dir_name, base_name = os.path.split(input_path)
    file_root, file_ext = os.path.splitext(base_name)
    
    output_dir = custom_output_dir if custom_output_dir and os.path.exists(custom_output_dir) else dir_name
    new_filename = f"{file_root}_{target_lang}{file_ext}"
    return os.path.join(output_dir, new_filename)


def read_text_file(filepath: str) -> str:
    """Reads a text file with automatic encoding fallback."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "gb18030", "shift_jis"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def write_text_file(filepath: str, content: str) -> None:
    """Writes content to a file with UTF-8 encoding."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


# ==========================================
# 1. PLAIN TEXT (.txt, .md, ...)
# ==========================================
def translate_plain_text_file(
    input_path: str,
    output_path: str,
    target_lang: str,
    source_lang: str,
    log_fn: Optional[Callable[[str], None]] = None
) -> None:
    text = read_text_file(input_path)
    if log_fn:
        log_fn(f"Translating text content ({len(text)} characters)...")
    translated = translate_text(text, target_lang=target_lang, source_lang=source_lang)
    write_text_file(output_path, translated)


# ==========================================
# 2. SUBTITLES (.srt, .vtt)
# ==========================================
def translate_subtitle_file(
    input_path: str,
    output_path: str,
    target_lang: str,
    source_lang: str,
    log_fn: Optional[Callable[[str], None]] = None
) -> None:
    text = read_text_file(input_path)
    lines = text.splitlines()
    translated_lines = []
    
    # Regex to detect SRT/VTT timestamps
    time_pattern = re.compile(r'^\s*(\d{1,2}:)?\d{2}:\d{2}[,\.]\d{3}\s*-->\s*(\d{1,2}:)?\d{2}:\d{2}[,\.]\d{3}')

    dialogue_buffer = []
    dialogue_indices = []

    for i, line in enumerate(lines):
        trimmed = line.strip()
        if not trimmed:
            translated_lines.append(line)
        elif trimmed.isdigit():  # Subtitle index number
            translated_lines.append(line)
        elif time_pattern.match(trimmed) or trimmed.startswith("WEBVTT") or trimmed.startswith("NOTE"):
            translated_lines.append(line)
        else:
            # Subtitle dialogue text to translate
            dialogue_buffer.append(trimmed)
            dialogue_indices.append(len(translated_lines))
            translated_lines.append("")  # Placeholder

    if log_fn:
        log_fn(f"Found {len(dialogue_buffer)} subtitle dialogue lines to translate...")

    if dialogue_buffer:
        # Group lines with a separator to batch translate efficiently
        batch_size = 50
        for b_start in range(0, len(dialogue_buffer), batch_size):
            batch = dialogue_buffer[b_start:b_start + batch_size]
            joined_text = "\n[SEP]\n".join(batch)
            translated_joined = translate_text(joined_text, target_lang=target_lang, source_lang=source_lang)
            translated_items = [item.strip() for item in translated_joined.split("[SEP]")]
            
            if len(translated_items) != len(batch):
                # Fallback item-by-item if separator was lost
                translated_items = [translate_text(item, target_lang=target_lang, source_lang=source_lang) for item in batch]
            
            for offset, t_text in enumerate(translated_items):
                target_idx = dialogue_indices[b_start + offset]
                translated_lines[target_idx] = t_text
            
            if log_fn:
                log_fn(f"Translated {min(b_start + batch_size, len(dialogue_buffer))}/{len(dialogue_buffer)} lines...")

    write_text_file(output_path, "\n".join(translated_lines))


# ==========================================
# 3. CSV (.csv)
# ==========================================
def translate_csv_file(
    input_path: str,
    output_path: str,
    target_lang: str,
    source_lang: str,
    log_fn: Optional[Callable[[str], None]] = None
) -> None:
    raw_content = read_text_file(input_path)
    reader = csv.reader(io.StringIO(raw_content))
    rows = list(reader)
    
    translated_rows = []
    total_cells = sum(len(row) for row in rows)
    if log_fn:
        log_fn(f"Translating CSV spreadsheet ({len(rows)} rows, {total_cells} cells)...")

    for r_idx, row in enumerate(rows):
        translated_row = []
        for cell in row:
            if cell.strip() and not cell.strip().replace(".", "", 1).replace("-", "", 1).isdigit():
                t_cell = translate_text(cell, target_lang=target_lang, source_lang=source_lang)
                translated_row.append(t_cell)
            else:
                translated_row.append(cell)
        translated_rows.append(translated_row)
        if log_fn and (r_idx + 1) % 10 == 0:
            log_fn(f"Processed {r_idx + 1}/{len(rows)} rows...")

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(translated_rows)


# ==========================================
# 4. JSON (.json)
# ==========================================
def translate_json_file(
    input_path: str,
    output_path: str,
    target_lang: str,
    source_lang: str,
    log_fn: Optional[Callable[[str], None]] = None
) -> None:
    raw_content = read_text_file(input_path)
    data = json.loads(raw_content)

    def translate_obj(obj):
        if isinstance(obj, dict):
            return {k: translate_obj(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [translate_obj(elem) for elem in obj]
        elif isinstance(obj, str) and obj.strip():
            return translate_text(obj, target_lang=target_lang, source_lang=source_lang)
        return obj

    if log_fn:
        log_fn("Traversing and translating JSON string values...")
    translated_data = translate_obj(data)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)


# ==========================================
# 5. HTML / XML
# ==========================================
def translate_html_xml_file(
    input_path: str,
    output_path: str,
    target_lang: str,
    source_lang: str,
    is_xml: bool = False,
    log_fn: Optional[Callable[[str], None]] = None
) -> None:
    content = read_text_file(input_path)
    parser = "xml" if is_xml else "html.parser"
    soup = BeautifulSoup(content, parser)

    nodes = []
    for element in soup.find_all(text=True):
        if element.parent and element.parent.name in ["script", "style", "code"]:
            continue
        text_str = str(element).strip()
        if text_str and not text_str.isdigit():
            nodes.append(element)

    if log_fn:
        log_fn(f"Translating {len(nodes)} text nodes in {'XML' if is_xml else 'HTML'} file...")

    for idx, element in enumerate(nodes):
        orig = str(element).strip()
        translated = translate_text(orig, target_lang=target_lang, source_lang=source_lang)
        element.replace_with(translated)
        if log_fn and (idx + 1) % 20 == 0:
            log_fn(f"Translated {idx + 1}/{len(nodes)} elements...")

    write_text_file(output_path, str(soup))


# ==========================================
# 6. WORD (.docx)
# ==========================================
def translate_docx_file(
    input_path: str,
    output_path: str,
    target_lang: str,
    source_lang: str,
    log_fn: Optional[Callable[[str], None]] = None
) -> None:
    """
    Translates Word .docx file by extracting XML and updating <w:t> tags,
    preserving 100% of images, tables, layout, and document styles.
    """
    if log_fn:
        log_fn("Analyzing Word (.docx) document structure...")

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    ET.register_namespace("w", ns["w"])

    with zipfile.ZipFile(input_path, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                buffer = zin.read(item.filename)
                if item.filename.startswith("word/") and item.filename.endswith(".xml"):
                    try:
                        root = ET.fromstring(buffer)
                        text_elements = root.findall(".//w:t", ns)
                        if text_elements:
                            if log_fn:
                                log_fn(f"Translating {item.filename}: found {len(text_elements)} text segments...")
                            
                            for p_elem in root.findall(".//w:p", ns):
                                p_texts = p_elem.findall(".//w:t", ns)
                                full_p_text = "".join([t.text for t in p_texts if t.text])
                                if full_p_text.strip():
                                    translated_p = translate_text(full_p_text, target_lang=target_lang, source_lang=source_lang)
                                    if p_texts:
                                        p_texts[0].text = translated_p
                                        for extra_t in p_texts[1:]:
                                            extra_t.text = ""
                        
                        buffer = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                    except Exception as e:
                        if log_fn:
                            log_fn(f"[Warning] XML error in {item.filename}: {e}")
                
                zout.writestr(item, buffer)


# ==========================================
# 7. POWERPOINT (.pptx)
# ==========================================
def translate_pptx_file(
    input_path: str,
    output_path: str,
    target_lang: str,
    source_lang: str,
    log_fn: Optional[Callable[[str], None]] = None
) -> None:
    """
    Translates PowerPoint .pptx slides by parsing slide XML and updating <a:t> tags.
    """
    if log_fn:
        log_fn("Analyzing PowerPoint (.pptx) presentation structure...")

    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    ET.register_namespace("a", ns["a"])

    with zipfile.ZipFile(input_path, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                buffer = zin.read(item.filename)
                if item.filename.startswith("ppt/slides/slide") and item.filename.endswith(".xml"):
                    try:
                        root = ET.fromstring(buffer)
                        for p_elem in root.findall(".//a:p", ns):
                            p_texts = p_elem.findall(".//a:t", ns)
                            full_p_text = "".join([t.text for t in p_texts if t.text])
                            if full_p_text.strip():
                                translated_p = translate_text(full_p_text, target_lang=target_lang, source_lang=source_lang)
                                if p_texts:
                                    p_texts[0].text = translated_p
                                    for extra_t in p_texts[1:]:
                                        extra_t.text = ""
                        
                        buffer = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                    except Exception as e:
                        if log_fn:
                            log_fn(f"[Warning] Slide XML error in {item.filename}: {e}")
                
                zout.writestr(item, buffer)


# ==========================================
# 8. EXCEL (.xlsx)
# ==========================================
def translate_xlsx_file(
    input_path: str,
    output_path: str,
    target_lang: str,
    source_lang: str,
    log_fn: Optional[Callable[[str], None]] = None
) -> None:
    """
    Translates Excel .xlsx spreadsheet while preserving sheets and structure.
    """
    if log_fn:
        log_fn("Loading Excel (.xlsx) workbook...")

    wb = openpyxl.load_workbook(input_path)
    total_sheets = len(wb.sheetnames)

    for s_idx, sheetname in enumerate(wb.sheetnames):
        ws = wb[sheetname]
        if log_fn:
            log_fn(f"Translating Sheet {s_idx + 1}/{total_sheets}: '{sheetname}'...")

        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.strip():
                    if cell.value.startswith("="):
                        continue
                    if cell.value.strip().replace(".", "", 1).replace("-", "", 1).isdigit():
                        continue
                    cell.value = translate_text(cell.value, target_lang=target_lang, source_lang=source_lang)

    wb.save(output_path)


# ==========================================
# 9. PDF (.pdf)
# ==========================================
def translate_pdf_file(
    input_path: str,
    output_path: str,
    target_lang: str,
    source_lang: str,
    log_fn: Optional[Callable[[str], None]] = None
) -> str:
    """
    Extracts and translates PDF document content page-by-page.
    Outputs translated text document (.txt).
    """
    if log_fn:
        log_fn("Reading PDF document...")

    reader = pypdf.PdfReader(input_path)
    num_pages = len(reader.pages)
    if log_fn:
        log_fn(f"Found {num_pages} pages in PDF document...")

    translated_pages = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        if page_text.strip():
            if log_fn:
                log_fn(f"Translating page {i + 1}/{num_pages}...")
            t_text = translate_text(page_text, target_lang=target_lang, source_lang=source_lang)
            translated_pages.append(f"--- [PAGE {i + 1}] ---\n\n{t_text}\n")
        else:
            translated_pages.append(f"--- [PAGE {i + 1}] (Blank or Scanned image page) ---\n")

    if output_path.lower().endswith(".pdf"):
        output_path = output_path[:-4] + ".txt"

    full_content = "\n\n".join(translated_pages)
    write_text_file(output_path, full_content)
    return output_path


# ==========================================
# MAIN DISPATCHER
# ==========================================
def process_file_translation(
    input_path: str,
    target_lang: str,
    source_lang: str = "auto",
    custom_output_dir: Optional[str] = None,
    log_fn: Optional[Callable[[str], None]] = None
) -> Tuple[bool, str, str]:
    """
    Detects file extension and routes to appropriate translator function.
    Returns (success: bool, output_file_path: str, status_message: str).
    """
    if not os.path.exists(input_path):
        return False, "", f"File does not exist: {input_path}"

    ext = os.path.splitext(input_path)[1].lower()
    output_path = get_output_filepath(input_path, target_lang, custom_output_dir)

    try:
        if ext in [".txt", ".md", ".rtf", ".log", ".tex"]:
            translate_plain_text_file(input_path, output_path, target_lang, source_lang, log_fn)
        elif ext in [".srt", ".vtt"]:
            translate_subtitle_file(input_path, output_path, target_lang, source_lang, log_fn)
        elif ext == ".csv":
            translate_csv_file(input_path, output_path, target_lang, source_lang, log_fn)
        elif ext == ".json":
            translate_json_file(input_path, output_path, target_lang, source_lang, log_fn)
        elif ext in [".html", ".htm"]:
            translate_html_xml_file(input_path, output_path, target_lang, source_lang, is_xml=False, log_fn=log_fn)
        elif ext == ".xml":
            translate_html_xml_file(input_path, output_path, target_lang, source_lang, is_xml=True, log_fn=log_fn)
        elif ext == ".docx":
            translate_docx_file(input_path, output_path, target_lang, source_lang, log_fn)
        elif ext == ".pptx":
            translate_pptx_file(input_path, output_path, target_lang, source_lang, log_fn)
        elif ext == ".xlsx":
            translate_xlsx_file(input_path, output_path, target_lang, source_lang, log_fn)
        elif ext == ".pdf":
            output_path = translate_pdf_file(input_path, output_path, target_lang, source_lang, log_fn)
        else:
            if log_fn:
                log_fn(f"Extension {ext} not explicitly defined, translating as plain text...")
            translate_plain_text_file(input_path, output_path, target_lang, source_lang, log_fn)

        return True, output_path, f"Completed successfully! Result saved to:\n{output_path}"
    except Exception as e:
        return False, "", f"Error translating file {os.path.basename(input_path)}: {str(e)}"
