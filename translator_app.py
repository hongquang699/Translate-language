"""
translator_app.py
Universal File & Text Translator (Phần Mềm Dịch Thuật Đa Năng)
Dual UI Language Support: English (🇬🇧) & Tiếng Việt (🇻🇳).
"""

import os
import sys
import threading
import argparse
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Ensure UTF-8 console output on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from translator_engine import get_all_languages, translate_text, POPULAR_LANGUAGES_EN, POPULAR_LANGUAGES_VI
from file_handler import process_file_translation, SUPPORTED_EXTENSIONS, ALL_EXTENSIONS


# ==========================================
# BILINGUAL UI DICTIONARY (EN & VI)
# ==========================================
UI_TEXTS = {
    "en": {
        "app_title": "Universal File & Text Translator",
        "header_title": "🌐 UNIVERSAL FILE & TEXT TRANSLATOR",
        "header_sub": "Translate Word (.docx), Excel (.xlsx), PowerPoint (.pptx), PDF, Subtitles (.srt, .vtt), Text (.txt, .md, .json, .csv)...",
        "ui_lang_label": "UI Language / Ngôn ngữ:",
        "tab_file": "  📁 File Translator  ",
        "tab_text": "  📝 Paste & Translate Text  ",
        "tab_help": "  ℹ️ Help & Formats  ",
        "box_file": " 1. Select or Paste File Path ",
        "btn_browse": "📂 Browse File...",
        "btn_paste_path": "📋 Paste Path",
        "hint_file": "Tip: You can select a file or directly paste a file path from your clipboard (Ctrl+V).",
        "box_lang": " 2. Language Selection ",
        "lbl_src_lang": "Source Language (Original):",
        "auto_detect": "Auto Detect",
        "lbl_dst_lang": "Target Language (Translate to):",
        "box_save": " 3. Output Destination ",
        "radio_same": "Save in the same folder as original file (e.g. document_vi.docx)",
        "radio_custom": "Save in custom directory:",
        "btn_browse_dir": "Browse...",
        "btn_start_file": "🚀 START TRANSLATION",
        "btn_translating": "⏳ TRANSLATING...",
        "btn_open_folder": "📂 Open Output Folder",
        "box_log": " Activity Log ",
        "log_ready": "Ready to translate. Please select or paste a file path...",
        "log_start": "--- TRANSLATION STARTED: {filename} ---",
        "log_langs": "Languages: {src} -> {dst}",
        "log_finish": "[FINISHED] Saved to: {path}\n",
        "log_failed": "[FAILED] {msg}\n",
        "lbl_from": "From:",
        "lbl_to": "To:",
        "btn_translate_now": "✨ Translate Now",
        "translating_text": "⏳ Translating text, please wait...",
        "box_input_text": " Original Text (Paste content here) ",
        "btn_paste_clip": "📋 Paste from Clipboard",
        "btn_clear": "🗑️ Clear",
        "box_output_text": " Translated Result ",
        "btn_copy_res": "📄 Copy to Clipboard",
        "btn_save_txt": "💾 Save to .txt File",
        "msg_clipboard_err": "Could not read clipboard data.",
        "msg_no_output_folder": "No output file has been created yet.",
        "msg_copied": "Translation copied to clipboard!",
        "msg_no_copy": "No translation content to copy.",
        "msg_no_save": "No content to save.",
        "msg_saved_at": "File saved at:\n{path}",
        "msg_in_progress": "A translation is already in progress. Please wait!",
        "msg_invalid_file": "Please select or paste a valid file path!",
        "msg_invalid_dir": "Specified custom output directory is invalid!",
        "msg_trans_success": "Translation complete!\n\nOutput file:\n{path}",
        "msg_trans_empty_text": "Please enter or paste text to translate.",
        "help_guide": """========================================================================
         USER GUIDE - UNIVERSAL FILE & TEXT TRANSLATOR
========================================================================

1. SUPPORTED FILE FORMATS:
   • Microsoft Word (.docx): Translates document content, preserving images, tables, layout, and formatting.
   • Microsoft Excel (.xlsx): Translates cell values across all worksheets while preserving formulas and structure.
   • Microsoft PowerPoint (.pptx): Translates text boxes and shapes across all presentation slides.
   • PDF Documents (.pdf): Extracts and translates text page-by-page, outputting clean translated text.
   • Video Subtitles (.srt, .vtt): Translates dialogue lines while preserving 100% of timestamp codes.
   • Structured Data (.json, .csv, .xml, .html): Translates textual content while maintaining syntax and data hierarchy.
   • Plain Text (.txt, .md, .rtf, .log, .tex): Translates full document with automatic paragraph chunking.

2. HOW TO USE:
   • Step 1: Click '📂 Browse File...' or Paste (Ctrl+V) the file path into the input field.
   • Step 2: Choose your source language (or leave as 'Auto Detect') and target language.
   • Step 3: Click '🚀 START TRANSLATION'. Monitor progress in the Activity Log.
   • Step 4: When finished, click '📂 Open Output Folder' to view your translated file.

3. OVER 130+ SUPPORTED LANGUAGES:
   • English, Vietnamese, Chinese (Simplified & Traditional), Japanese, Korean, French,
     German, Spanish, Russian, Thai, Lao, Khmer, Arabic, Portuguese, Italian, Hindi, etc.

4. AUTOMATIC CHUNKING & RETRY LOGIC:
   • Long files and paragraphs are automatically segmented into safe chunks (< 3500 chars).
   • Built-in retry mechanism with exponential backoff ensures reliability under unstable network conditions."""
    },

    "vi": {
        "app_title": "Phần Mềm Dịch Thuật Đa Năng - Universal Translator",
        "header_title": "🌐 PHẦN MỀM DỊCH THUẬT ĐA NĂNG",
        "header_sub": "Dịch Word (.docx), Excel (.xlsx), PowerPoint (.pptx), PDF, Phụ đề (.srt, .vtt), Văn bản (.txt, .md, .json, .csv)...",
        "ui_lang_label": "Ngôn ngữ giao diện / UI Language:",
        "tab_file": "  📁 Dịch Tệp Tin (File)  ",
        "tab_text": "  📝 Dán & Dịch Văn Bản  ",
        "tab_help": "  ℹ️ Hướng Dẫn & Định Dạng  ",
        "box_file": " 1. Chọn hoặc Dán đường dẫn Tệp Tin ",
        "btn_browse": "📂 Duyệt File...",
        "btn_paste_path": "📋 Dán Path",
        "hint_file": "Mẹo: Bạn có thể chọn 1 tệp hoặc dán trực tiếp đường dẫn file từ Clipboard (Ctrl+V).",
        "box_lang": " 2. Lựa Chọn Ngôn Ngữ ",
        "lbl_src_lang": "Ngôn ngữ nguồn (Gốc):",
        "auto_detect": "Tự động phát hiện",
        "lbl_dst_lang": "Ngôn ngữ đích (Muốn dịch sang):",
        "box_save": " 3. Thư Mục Lưu Tệp Kết Quả ",
        "radio_same": "Lưu cùng thư mục với tệp gốc (ví dụ: baocao_vi.docx)",
        "radio_custom": "Lưu vào thư mục chỉ định:",
        "btn_browse_dir": "Duyệt...",
        "btn_start_file": "🚀 BẮT ĐẦU DỊCH TỆP",
        "btn_translating": "⏳ ĐANG DỊCH TỆP...",
        "btn_open_folder": "📂 Mở Thư Mục Kết Quả",
        "box_log": " Nhật Ký Tiến Trình ",
        "log_ready": "Sẵn sàng dịch. Vui lòng chọn hoặc dán đường dẫn tệp tin...",
        "log_start": "--- BẮT ĐẦU DỊCH: {filename} ---",
        "log_langs": "Ngôn ngữ: {src} -> {dst}",
        "log_finish": "[HOÀN THÀNH] Tệp đã lưu tại: {path}\n",
        "log_failed": "[THẤT BẠI] {msg}\n",
        "lbl_from": "Từ:",
        "lbl_to": "Sang:",
        "btn_translate_now": "✨ Dịch Ngay",
        "translating_text": "⏳ Đang dịch văn bản, vui lòng chờ...",
        "box_input_text": " Văn Bản Gốc (Dán nội dung vào đây) ",
        "btn_paste_clip": "📋 Dán từ Clipboard",
        "btn_clear": "🗑️ Xóa",
        "box_output_text": " Bản Dịch Kết Quả ",
        "btn_copy_res": "📄 Sao chép kết quả",
        "btn_save_txt": "💾 Lưu ra tệp .txt",
        "msg_clipboard_err": "Không thể lấy dữ liệu từ Clipboard.",
        "msg_no_output_folder": "Chưa có tệp kết quả nào được tạo.",
        "msg_copied": "Đã sao chép nội dung bản dịch vào Clipboard!",
        "msg_no_copy": "Chưa có nội dung bản dịch để sao chép.",
        "msg_no_save": "Chưa có nội dung để lưu.",
        "msg_saved_at": "Đã lưu tệp tại:\n{path}",
        "msg_in_progress": "Hệ thống đang dịch một tệp khác. Vui lòng chờ hoàn tất!",
        "msg_invalid_file": "Vui lòng chọn hoặc dán đường dẫn tệp tin hợp lệ!",
        "msg_invalid_dir": "Thư mục lưu tệp chỉ định không hợp lệ!",
        "msg_trans_success": "Dịch tệp thành công!\n\nTệp kết quả:\n{path}",
        "msg_trans_empty_text": "Vui lòng nhập hoặc dán văn bản cần dịch vào ô bên trái.",
        "help_guide": """========================================================================
       HƯỚNG DẪN SỬ DỤNG PHẦN MỀM DỊCH THUẬT ĐA NĂNG
========================================================================

1. CÁC ĐỊNH DẠNG TỆP ĐƯỢC HỖ TRỢ:
   • Microsoft Word (.docx): Dịch toàn bộ văn bản, giữ nguyên hình ảnh, bảng biểu, căn lề và định dạng.
   • Microsoft Excel (.xlsx): Dịch nội dung các ô trong toàn bộ các Sheet mà không làm hỏng công thức.
   • Microsoft PowerPoint (.pptx): Dịch nội dung văn bản trên tất cả các Slide.
   • Tài liệu PDF (.pdf): Trích xuất văn bản từng trang và dịch hoàn chỉnh, xuất ra tệp văn bản.
   • Phụ đề Video (.srt, .vtt): Dịch lời thoại phim/video, giữ nguyên 100% mốc thời gian (timestamps).
   • Dữ liệu cấu trúc (.json, .csv, .xml, .html): Dịch các giá trị hiển thị, giữ nguyên cấu trúc code.
   • Văn bản thuần (.txt, .md, .rtf, .log, .tex): Dịch văn bản dài tự động chia nhỏ theo đoạn văn.

2. CÁCH SỬ DỤNG:
   • Bước 1: Nhấn '📂 Duyệt File...' để chọn tệp, hoặc Dán trực tiếp đường dẫn file vào ô.
   • Bước 2: Chọn ngôn ngữ nguồn (hoặc để 'Tự động phát hiện') và ngôn ngữ đích bạn muốn dịch sang.
   • Bước 3: Nhấn '🚀 BẮT ĐẦU DỊCH TỆP'. Quá trình dịch sẽ hiển thị chi tiết trong ô Nhật ký.
   • Bước 4: Sau khi hoàn thành, nhấn '📂 Mở Thư Mục Kết Quả' để xem ngay tệp đã dịch.

3. HƠN 130+ NGÔN NGỮ ĐƯỢC HỖ TRỢ:
   • Tiếng Việt, Tiếng Anh, Tiếng Trung (Giản thể & Phồn thể), Tiếng Nhật, Tiếng Hàn, Tiếng Pháp,
     Tiếng Đức, Tiếng Tây Ban Nha, Tiếng Nga, Tiếng Thái, Tiếng Lào, Tiếng Khmer, Tiếng Ả Rập,...

4. TÍNH NĂNG TỰ ĐỘNG CHUNK & RETRY:
   • Phần mềm tự động chia nhỏ văn bản dài thành các đoạn an toàn tránh lỗi quá tải API.
   • Có cơ chế tự động thử lại (retry) khi mạng chập chờn."""
    }
}


class ModernTranslatorGUI:
    def __init__(self, root: tk.Tk, default_ui_lang: str = "vi"):
        self.root = root
        self.current_ui_lang = default_ui_lang  # "vi" or "en"
        self.root.geometry("880x700")
        self.root.minsize(800, 620)

        # Color palette & styles
        self.bg_color = "#f4f6f9"
        self.primary_color = "#1e88e5"
        self.accent_color = "#43a047"
        self.root.configure(bg=self.bg_color)

        self.last_output_path = ""
        self.is_translating = False

        self._load_language_lists()
        self._setup_styles()
        self._build_ui()
        self._apply_ui_language(self.current_ui_lang)

    def _t(self, key: str, **kwargs) -> str:
        """Helper to get localized string."""
        raw = UI_TEXTS[self.current_ui_lang].get(key, UI_TEXTS["en"].get(key, key))
        return raw.format(**kwargs) if kwargs else raw

    def _load_language_lists(self):
        """Loads language options according to current UI language."""
        self.languages = get_all_languages(ui_lang=self.current_ui_lang)
        self.lang_display_names = [item[0] for item in self.languages]
        self.lang_code_map = {item[0]: item[1] for item in self.languages}
        self.lang_code_to_name = {item[1]: item[0] for item in self.languages}

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[16, 8], background="#e0e0e0")
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", self.primary_color)])

        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#1565c0", background=self.bg_color)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground="#616161", background=self.bg_color)

        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background=self.primary_color, foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#1565c0")])

    def _build_ui(self):
        # Set Window Icon if available
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "app_icon.ico")
        logo_path = os.path.join(base_dir, "app_logo.png")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # Header banner with Logo and Language Switcher
        header_frame = tk.Frame(self.root, bg=self.bg_color, pady=8)
        header_frame.pack(fill="x", padx=15)

        # Top Right Language Switcher
        top_right_frame = tk.Frame(header_frame, bg=self.bg_color)
        top_right_frame.pack(side="right", anchor="ne", pady=2)

        self.lbl_ui_switcher = tk.Label(top_right_frame, text="Ngôn ngữ / Language:", font=("Segoe UI", 9, "bold"), bg=self.bg_color, fg="#424242")
        self.lbl_ui_switcher.pack(side="left", padx=(0, 6))

        self.btn_lang_vi = tk.Button(
            top_right_frame, text="🇻🇳 Tiếng Việt", font=("Segoe UI", 9, "bold"),
            bg="#ffffff", fg="#d32f2f", relief="solid", bd=1, padx=8, pady=2, cursor="hand2",
            command=lambda: self.switch_ui_language("vi")
        )
        self.btn_lang_vi.pack(side="left", padx=2)

        self.btn_lang_en = tk.Button(
            top_right_frame, text="🇬🇧 English", font=("Segoe UI", 9),
            bg="#ffffff", fg="#1565c0", relief="solid", bd=1, padx=8, pady=2, cursor="hand2",
            command=lambda: self.switch_ui_language("en")
        )
        self.btn_lang_en.pack(side="left", padx=2)

        # Header Titles and Logo (Left)
        title_box = tk.Frame(header_frame, bg=self.bg_color)
        title_box.pack(side="left", fill="x", expand=True)

        if os.path.exists(logo_path):
            try:
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path).resize((48, 48), Image.LANCZOS)
                self.logo_tk = ImageTk.PhotoImage(logo_img)
                lbl_logo = tk.Label(title_box, image=self.logo_tk, bg=self.bg_color)
                lbl_logo.pack(side="left", padx=(0, 10))
            except Exception:
                pass

        text_title_box = tk.Frame(title_box, bg=self.bg_color)
        text_title_box.pack(side="left", fill="x", expand=True)

        self.lbl_header_title = ttk.Label(text_title_box, text="", style="Header.TLabel")
        self.lbl_header_title.pack(anchor="w")

        self.lbl_header_sub = ttk.Label(text_title_box, text="", style="SubHeader.TLabel")
        self.lbl_header_sub.pack(anchor="w")

        # Tabs container
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Tab 1: File Translator
        self.tab_file = tk.Frame(self.notebook, bg="#ffffff", padx=15, pady=15)
        self.notebook.add(self.tab_file, text="  📁 File Translator  ")
        self._build_file_tab()

        # Tab 2: Quick Text Translator
        self.tab_text = tk.Frame(self.notebook, bg="#ffffff", padx=15, pady=15)
        self.notebook.add(self.tab_text, text="  📝 Paste & Translate Text  ")
        self._build_text_tab()

        # Tab 3: Help & Formats
        self.tab_help = tk.Frame(self.notebook, bg="#ffffff", padx=15, pady=15)
        self.notebook.add(self.tab_help, text="  ℹ️ Help & Formats  ")
        self._build_help_tab()

    # ==========================================
    # TAB 1: FILE TRANSLATOR
    # ==========================================
    def _build_file_tab(self):
        # 1. File selector box
        self.box_file = tk.LabelFrame(
            self.tab_file,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#1565c0",
            padx=10,
            pady=10
        )
        self.box_file.pack(fill="x", pady=(0, 10))

        row1 = tk.Frame(self.box_file, bg="#ffffff")
        row1.pack(fill="x", pady=2)

        self.entry_file_path = tk.Entry(row1, font=("Segoe UI", 10), bg="#fafafa", relief="solid", bd=1)
        self.entry_file_path.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 8))

        self.btn_browse = ttk.Button(row1, text="", command=self._browse_file)
        self.btn_browse.pack(side="left", padx=(0, 4))

        self.btn_paste_path = ttk.Button(row1, text="", command=self._paste_file_path)
        self.btn_paste_path.pack(side="left")

        self.lbl_hint_file = tk.Label(
            self.box_file,
            text="",
            font=("Segoe UI", 8, "italic"),
            bg="#ffffff",
            fg="#757575"
        )
        self.lbl_hint_file.pack(anchor="w", pady=(4, 0))

        # 2. Language selection box
        self.box_lang = tk.LabelFrame(
            self.tab_file,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#1565c0",
            padx=10,
            pady=10
        )
        self.box_lang.pack(fill="x", pady=(0, 10))

        lang_row = tk.Frame(self.box_lang, bg="#ffffff")
        lang_row.pack(fill="x")

        # Source language
        frame_src = tk.Frame(lang_row, bg="#ffffff")
        frame_src.pack(side="left", fill="x", expand=True)
        self.lbl_src_lang = tk.Label(frame_src, text="", font=("Segoe UI", 9, "bold"), bg="#ffffff")
        self.lbl_src_lang.pack(anchor="w")

        self.src_lang_var = tk.StringVar(value="auto")
        self.combo_src_lang = ttk.Combobox(frame_src, state="readonly", font=("Segoe UI", 9))
        self.combo_src_lang.pack(fill="x", pady=(4, 0))

        # Swap button
        btn_swap = tk.Button(lang_row, text="⇄", font=("Segoe UI", 12, "bold"), bg="#e0e0e0", relief="flat", command=self._swap_languages, cursor="hand2")
        btn_swap.pack(side="left", padx=15, pady=(15, 0))

        # Target language
        frame_dst = tk.Frame(lang_row, bg="#ffffff")
        frame_dst.pack(side="left", fill="x", expand=True)
        self.lbl_dst_lang = tk.Label(frame_dst, text="", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#d32f2f")
        self.lbl_dst_lang.pack(anchor="w")

        self.dst_lang_var = tk.StringVar(value="vi")
        self.combo_dst_lang = ttk.Combobox(frame_dst, state="readonly", font=("Segoe UI", 9))
        self.combo_dst_lang.pack(fill="x", pady=(4, 0))

        # 3. Output destination box
        self.box_save = tk.LabelFrame(
            self.tab_file,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#1565c0",
            padx=10,
            pady=8
        )
        self.box_save.pack(fill="x", pady=(0, 10))

        self.save_mode = tk.StringVar(value="same")
        self.radio_same = tk.Radiobutton(
            self.box_save,
            text="",
            variable=self.save_mode,
            value="same",
            bg="#ffffff",
            font=("Segoe UI", 9)
        )
        self.radio_same.pack(anchor="w")

        row_custom = tk.Frame(self.box_save, bg="#ffffff")
        row_custom.pack(fill="x", pady=(2, 0))
        self.radio_custom = tk.Radiobutton(
            row_custom,
            text="",
            variable=self.save_mode,
            value="custom",
            bg="#ffffff",
            font=("Segoe UI", 9)
        )
        self.radio_custom.pack(side="left")

        self.entry_custom_dir = tk.Entry(row_custom, font=("Segoe UI", 9), bg="#fafafa", relief="solid", bd=1)
        self.entry_custom_dir.pack(side="left", fill="x", expand=True, padx=6)

        self.btn_browse_dir = ttk.Button(row_custom, text="", command=self._browse_output_dir)
        self.btn_browse_dir.pack(side="left")

        # Action buttons
        action_frame = tk.Frame(self.tab_file, bg="#ffffff")
        action_frame.pack(fill="x", pady=(0, 10))

        self.btn_start_file = tk.Button(
            action_frame,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg=self.primary_color,
            fg="#ffffff",
            activebackground="#1565c0",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._start_file_translation_thread
        )
        self.btn_start_file.pack(side="left")

        self.btn_open_result = tk.Button(
            action_frame,
            text="",
            font=("Segoe UI", 10),
            bg="#eeeeee",
            relief="flat",
            padx=12,
            pady=8,
            state="disabled",
            command=self._open_output_folder
        )
        self.btn_open_result.pack(side="left", padx=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.tab_file, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(0, 5))

        # Log Console
        self.box_log = tk.LabelFrame(self.tab_file, text="", font=("Segoe UI", 9, "bold"), bg="#ffffff", padx=5, pady=5)
        self.box_log.pack(fill="both", expand=True)

        self.txt_log = scrolledtext.ScrolledText(self.box_log, height=6, font=("Consolas", 9), bg="#1e1e1e", fg="#4af626", relief="solid", bd=1)
        self.txt_log.pack(fill="both", expand=True)

    # ==========================================
    # TAB 2: QUICK TEXT TRANSLATOR
    # ==========================================
    def _build_text_tab(self):
        top_bar = tk.Frame(self.tab_text, bg="#ffffff", pady=4)
        top_bar.pack(fill="x", pady=(0, 8))

        self.lbl_from = tk.Label(top_bar, text="", font=("Segoe UI", 9, "bold"), bg="#ffffff")
        self.lbl_from.pack(side="left", padx=(0, 4))
        
        self.txt_src_var = tk.StringVar(value="auto")
        self.combo_txt_src = ttk.Combobox(top_bar, state="readonly", width=25, font=("Segoe UI", 9))
        self.combo_txt_src.pack(side="left", padx=(0, 10))

        btn_txt_swap = tk.Button(top_bar, text="⇄", font=("Segoe UI", 10, "bold"), bg="#e0e0e0", relief="flat", command=self._swap_text_languages)
        btn_txt_swap.pack(side="left", padx=(0, 10))

        self.lbl_to = tk.Label(top_bar, text="", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#d32f2f")
        self.lbl_to.pack(side="left", padx=(0, 4))

        self.txt_dst_var = tk.StringVar(value="vi")
        self.combo_txt_dst = ttk.Combobox(top_bar, state="readonly", width=25, font=("Segoe UI", 9))
        self.combo_txt_dst.pack(side="left", padx=(0, 15))

        self.btn_translate_now = tk.Button(top_bar, text="", font=("Segoe UI", 9, "bold"), bg=self.primary_color, fg="#ffffff", relief="flat", padx=12, pady=3, command=self._start_quick_text_translation)
        self.btn_translate_now.pack(side="left")

        # Two text panels
        text_container = tk.Frame(self.tab_text, bg="#ffffff")
        text_container.pack(fill="both", expand=True)

        # Input text panel
        self.left_frame = tk.LabelFrame(text_container, text="", font=("Segoe UI", 9, "bold"), bg="#ffffff", padx=6, pady=6)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.input_text_box = scrolledtext.ScrolledText(self.left_frame, font=("Segoe UI", 10), wrap="word", relief="solid", bd=1)
        self.input_text_box.pack(fill="both", expand=True, pady=(0, 6))

        left_btn_bar = tk.Frame(self.left_frame, bg="#ffffff")
        left_btn_bar.pack(fill="x")
        self.btn_paste_clip = ttk.Button(left_btn_bar, text="", command=self._paste_into_textbox)
        self.btn_paste_clip.pack(side="left")
        self.btn_clear = ttk.Button(left_btn_bar, text="", command=lambda: self.input_text_box.delete("1.0", tk.END))
        self.btn_clear.pack(side="left", padx=5)

        # Output translated text panel
        self.right_frame = tk.LabelFrame(text_container, text="", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#2e7d32", padx=6, pady=6)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.output_text_box = scrolledtext.ScrolledText(self.right_frame, font=("Segoe UI", 10), wrap="word", relief="solid", bd=1)
        self.output_text_box.pack(fill="both", expand=True, pady=(0, 6))

        right_btn_bar = tk.Frame(self.right_frame, bg="#ffffff")
        right_btn_bar.pack(fill="x")
        self.btn_copy_res = ttk.Button(right_btn_bar, text="", command=self._copy_result_text)
        self.btn_copy_res.pack(side="left")
        self.btn_save_txt = ttk.Button(right_btn_bar, text="", command=self._save_result_to_file)
        self.btn_save_txt.pack(side="left", padx=5)

    # ==========================================
    # TAB 3: HELP & FORMATS
    # ==========================================
    def _build_help_tab(self):
        self.info_scroll = scrolledtext.ScrolledText(self.tab_help, font=("Segoe UI", 10), wrap="word", bg="#fafafa", relief="flat")
        self.info_scroll.pack(fill="both", expand=True)

    # ==========================================
    # DYNAMIC LANGUAGE SWITCHING ENGINE
    # ==========================================
    def switch_ui_language(self, new_lang: str):
        """Switches the UI between 'vi' and 'en' immediately."""
        if self.current_ui_lang == new_lang:
            return
        self.current_ui_lang = new_lang
        self._load_language_lists()
        self._apply_ui_language(new_lang)

    def _apply_ui_language(self, lang: str):
        """Refreshes all UI text elements with current language."""
        # Update switcher buttons highlight
        if lang == "vi":
            self.btn_lang_vi.configure(font=("Segoe UI", 9, "bold"), bg="#ffebee", fg="#c62828")
            self.btn_lang_en.configure(font=("Segoe UI", 9), bg="#ffffff", fg="#616161")
        else:
            self.btn_lang_en.configure(font=("Segoe UI", 9, "bold"), bg="#e3f2fd", fg="#1565c0")
            self.btn_lang_vi.configure(font=("Segoe UI", 9), bg="#ffffff", fg="#616161")

        # Window & Header
        self.root.title(self._t("app_title"))
        self.lbl_header_title.configure(text=self._t("header_title"))
        self.lbl_header_sub.configure(text=self._t("header_sub"))
        self.lbl_ui_switcher.configure(text=self._t("ui_lang_label"))

        # Notebook tabs
        self.notebook.tab(0, text=self._t("tab_file"))
        self.notebook.tab(1, text=self._t("tab_text"))
        self.notebook.tab(2, text=self._t("tab_help"))

        # Tab 1: File
        self.box_file.configure(text=self._t("box_file"))
        self.btn_browse.configure(text=self._t("btn_browse"))
        self.btn_paste_path.configure(text=self._t("btn_paste_path"))
        self.lbl_hint_file.configure(text=self._t("hint_file"))

        self.box_lang.configure(text=self._t("box_lang"))
        self.lbl_src_lang.configure(text=self._t("lbl_src_lang"))
        self.lbl_dst_lang.configure(text=self._t("lbl_dst_lang"))

        # Preserve selected codes across language switch
        cur_src_code = self.src_lang_var.get()
        cur_dst_code = self.dst_lang_var.get()

        auto_label = self._t("auto_detect")
        src_options = [auto_label] + self.lang_display_names
        self.combo_src_lang["values"] = src_options
        self.combo_dst_lang["values"] = self.lang_display_names

        # Set dropdown display values matching codes
        if cur_src_code == "auto" or cur_src_code == "":
            self.combo_src_lang.set(auto_label)
        else:
            self.combo_src_lang.set(self.lang_code_to_name.get(cur_src_code, auto_label))

        self.combo_dst_lang.set(self.lang_code_to_name.get(cur_dst_code, self.lang_display_names[0]))

        self.box_save.configure(text=self._t("box_save"))
        self.radio_same.configure(text=self._t("radio_same"))
        self.radio_custom.configure(text=self._t("radio_custom"))
        self.btn_browse_dir.configure(text=self._t("btn_browse_dir"))

        if not self.is_translating:
            self.btn_start_file.configure(text=self._t("btn_start_file"))
        else:
            self.btn_start_file.configure(text=self._t("btn_translating"))
        self.btn_open_result.configure(text=self._t("btn_open_folder"))
        self.box_log.configure(text=self._t("box_log"))

        # Tab 2: Text
        self.lbl_from.configure(text=self._t("lbl_from"))
        self.lbl_to.configure(text=self._t("lbl_to"))
        self.btn_translate_now.configure(text=self._t("btn_translate_now"))
        
        self.combo_txt_src["values"] = src_options
        self.combo_txt_dst["values"] = self.lang_display_names
        
        cur_txt_src_code = self.txt_src_var.get()
        cur_txt_dst_code = self.txt_dst_var.get()
        if cur_txt_src_code == "auto" or cur_txt_src_code == "":
            self.combo_txt_src.set(auto_label)
        else:
            self.combo_txt_src.set(self.lang_code_to_name.get(cur_txt_src_code, auto_label))
        self.combo_txt_dst.set(self.lang_code_to_name.get(cur_txt_dst_code, self.lang_display_names[0]))

        self.left_frame.configure(text=self._t("box_input_text"))
        self.btn_paste_clip.configure(text=self._t("btn_paste_clip"))
        self.btn_clear.configure(text=self._t("btn_clear"))

        self.right_frame.configure(text=self._t("box_output_text"))
        self.btn_copy_res.configure(text=self._t("btn_copy_res"))
        self.btn_save_txt.configure(text=self._t("btn_save_txt"))

        # Tab 3: Help
        self.info_scroll.configure(state="normal")
        self.info_scroll.delete("1.0", tk.END)
        self.info_scroll.insert("1.0", self._t("help_guide"))
        self.info_scroll.configure(state="disabled")

    # ==========================================
    # LOG & UI HELPERS
    # ==========================================
    def _log(self, message: str):
        self.txt_log.insert(tk.END, f"{message}\n")
        self.txt_log.see(tk.END)

    def _browse_file(self):
        filetypes = [
            ("All Supported Files", "*.docx;*.xlsx;*.pptx;*.pdf;*.txt;*.md;*.srt;*.vtt;*.json;*.csv;*.xml;*.html"),
            ("Microsoft Word (*.docx)", "*.docx"),
            ("Microsoft Excel (*.xlsx)", "*.xlsx"),
            ("Microsoft PowerPoint (*.pptx)", "*.pptx"),
            ("PDF Documents (*.pdf)", "*.pdf"),
            ("Video Subtitles (*.srt, *.vtt)", "*.srt;*.vtt"),
            ("Text & Data (*.txt, *.md, *.json, *.csv)", "*.txt;*.md;*.json;*.csv"),
            ("All Files (*.*)", "*.*")
        ]
        chosen = filedialog.askopenfilename(title="Select File", filetypes=filetypes)
        if chosen:
            self.entry_file_path.delete(0, tk.END)
            self.entry_file_path.insert(0, chosen)
            self._log(f"Selected file: {os.path.basename(chosen)}")

    def _paste_file_path(self):
        try:
            clipboard_text = self.root.clipboard_get().strip().strip('"').strip("'")
            if os.path.exists(clipboard_text):
                self.entry_file_path.delete(0, tk.END)
                self.entry_file_path.insert(0, clipboard_text)
                self._log(f"Pasted: {os.path.basename(clipboard_text)}")
            else:
                self.entry_file_path.delete(0, tk.END)
                self.entry_file_path.insert(0, clipboard_text)
                self._log(f"Pasted: {clipboard_text}")
        except Exception:
            messagebox.showwarning("Clipboard", self._t("msg_clipboard_err"))

    def _browse_output_dir(self):
        chosen = filedialog.askdirectory(title="Select Output Directory")
        if chosen:
            self.entry_custom_dir.delete(0, tk.END)
            self.entry_custom_dir.insert(0, chosen)
            self.save_mode.set("custom")

    def _get_selected_codes(self, src_combo, dst_combo) -> tuple:
        src_val = src_combo.get()
        dst_val = dst_combo.get()
        auto_str = self._t("auto_detect")
        src_code = "auto" if (src_val == auto_str or "Auto Detect" in src_val or "Tự động" in src_val) else self.lang_code_map.get(src_val, "auto")
        dst_code = self.lang_code_map.get(dst_val, "vi" if self.current_ui_lang == "vi" else "en")
        return src_code, dst_code

    def _swap_languages(self):
        src_code, dst_code = self._get_selected_codes(self.combo_src_lang, self.combo_dst_lang)
        if src_code != "auto":
            self.src_lang_var.set(dst_code)
            self.dst_lang_var.set(src_code)
            self.combo_src_lang.set(self.lang_code_to_name.get(dst_code, ""))
            self.combo_dst_lang.set(self.lang_code_to_name.get(src_code, ""))

    def _swap_text_languages(self):
        src_code, dst_code = self._get_selected_codes(self.combo_txt_src, self.combo_txt_dst)
        if src_code != "auto":
            self.txt_src_var.set(dst_code)
            self.txt_dst_var.set(src_code)
            self.combo_txt_src.set(self.lang_code_to_name.get(dst_code, ""))
            self.combo_txt_dst.set(self.lang_code_to_name.get(src_code, ""))

        in_text = self.input_text_box.get("1.0", tk.END).strip()
        out_text = self.output_text_box.get("1.0", tk.END).strip()
        if out_text:
            self.input_text_box.delete("1.0", tk.END)
            self.input_text_box.insert("1.0", out_text)
            self.output_text_box.delete("1.0", tk.END)
            if in_text:
                self.output_text_box.insert("1.0", in_text)

    def _open_output_folder(self):
        if self.last_output_path and os.path.exists(self.last_output_path):
            folder = os.path.dirname(self.last_output_path)
            if sys.platform.startswith("win"):
                os.startfile(folder)
            else:
                subprocess.Popen(["xdg-open", folder])
        else:
            messagebox.showinfo("Notice", self._t("msg_no_output_folder"))

    def _paste_into_textbox(self):
        try:
            content = self.root.clipboard_get()
            self.input_text_box.insert(tk.INSERT, content)
        except Exception:
            pass

    def _copy_result_text(self):
        res = self.output_text_box.get("1.0", tk.END).strip()
        if res:
            self.root.clipboard_clear()
            self.root.clipboard_append(res)
            messagebox.showinfo("Success", self._t("msg_copied"))
        else:
            messagebox.showwarning("Notice", self._t("msg_no_copy"))

    def _save_result_to_file(self):
        res = self.output_text_box.get("1.0", tk.END).strip()
        if not res:
            messagebox.showwarning("Notice", self._t("msg_no_save"))
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File (*.txt)", "*.txt"), ("All Files (*.*)", "*.*")])
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(res)
            messagebox.showinfo("Success", self._t("msg_saved_at", path=save_path))

    # ==========================================
    # ASYNC FILE TRANSLATION THREAD
    # ==========================================
    def _start_file_translation_thread(self):
        if self.is_translating:
            messagebox.showwarning("Notice", self._t("msg_in_progress"))
            return

        file_path = self.entry_file_path.get().strip().strip('"').strip("'")
        if not file_path or not os.path.isfile(file_path):
            messagebox.showerror("Error", self._t("msg_invalid_file"))
            return

        src_code, dst_code = self._get_selected_codes(self.combo_src_lang, self.combo_dst_lang)
        self.src_lang_var.set(src_code)
        self.dst_lang_var.set(dst_code)

        custom_dir = None
        if self.save_mode.get() == "custom":
            custom_dir = self.entry_custom_dir.get().strip()
            if not custom_dir or not os.path.isdir(custom_dir):
                messagebox.showerror("Error", self._t("msg_invalid_dir"))
                return

        self.is_translating = True
        self.btn_start_file.configure(state="disabled", text=self._t("btn_translating"))
        self.progress_bar.start(10)
        self.btn_open_result.configure(state="disabled")

        self._log(self._t("log_start", filename=os.path.basename(file_path)))
        self._log(self._t("log_langs", src=src_code, dst=dst_code))

        def worker():
            success, out_path, msg = process_file_translation(
                input_path=file_path,
                target_lang=dst_code,
                source_lang=src_code,
                custom_output_dir=custom_dir,
                log_fn=lambda log_msg: self.root.after(0, self._log, f"  [+] {log_msg}")
            )

            def on_finish():
                self.is_translating = False
                self.progress_bar.stop()
                self.btn_start_file.configure(state="normal", text=self._t("btn_start_file"))

                if success:
                    self.last_output_path = out_path
                    self.btn_open_result.configure(state="normal")
                    self._log(self._t("log_finish", path=out_path))
                    messagebox.showinfo("Success", self._t("msg_trans_success", path=out_path))
                else:
                    self._log(self._t("log_failed", msg=msg))
                    messagebox.showerror("Error", msg)

            self.root.after(0, on_finish)

        threading.Thread(target=worker, daemon=True).start()

    # ==========================================
    # ASYNC TEXT TRANSLATION THREAD
    # ==========================================
    def _start_quick_text_translation(self):
        input_text = self.input_text_box.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Notice", self._t("msg_trans_empty_text"))
            return

        src_code, dst_code = self._get_selected_codes(self.combo_txt_src, self.combo_txt_dst)
        self.txt_src_var.set(src_code)
        self.txt_dst_var.set(dst_code)

        self.output_text_box.delete("1.0", tk.END)
        self.output_text_box.insert("1.0", self._t("translating_text"))

        def worker():
            try:
                translated = translate_text(input_text, target_lang=dst_code, source_lang=src_code)
                def on_done():
                    self.output_text_box.delete("1.0", tk.END)
                    self.output_text_box.insert("1.0", translated)
                self.root.after(0, on_done)
            except Exception as e:
                def on_err():
                    self.output_text_box.delete("1.0", tk.END)
                    self.output_text_box.insert("1.0", f"Error: {str(e)}")
                self.root.after(0, on_err)

        threading.Thread(target=worker, daemon=True).start()


# ==========================================
# COMMAND-LINE INTERFACE (CLI)
# ==========================================
def run_cli():
    parser = argparse.ArgumentParser(description="Universal File & Text Translator")
    parser.add_argument("-f", "--file", help="Path to input file to translate")
    parser.add_argument("-t", "--target", default="vi", help="Target language code (default: vi)")
    parser.add_argument("-s", "--source", default="auto", help="Source language code (default: auto)")
    parser.add_argument("-o", "--output-dir", help="Optional custom output directory")
    parser.add_argument("-m", "--text", help="Direct text string to translate")
    parser.add_argument("--lang", choices=["vi", "en"], default="vi", help="UI language mode: vi (Vietnamese) or en (English)")

    args = parser.parse_args()

    if args.text:
        print(f"Translating: '{args.text}' to '{args.target}'...")
        res = translate_text(args.text, target_lang=args.target, source_lang=args.source)
        print("Result:")
        print(res)
        return

    if args.file:
        if not os.path.isfile(args.file):
            print(f"Error: File not found: '{args.file}'")
            sys.exit(1)

        print(f"Translating file: {args.file}")
        print(f"Languages: {args.source} -> {args.target}")
        success, out_path, msg = process_file_translation(
            input_path=args.file,
            target_lang=args.target,
            source_lang=args.source,
            custom_output_dir=args.output_dir,
            log_fn=lambda log_text: print(f"  [+] {log_text}")
        )
        if success:
            print(f"[COMPLETED] Output saved to: {out_path}")
        else:
            print(f"[FAILED] {msg}")
        return

    # Launch GUI with default UI language (defaults to 'vi', switchable to 'en')
    root = tk.Tk()
    app = ModernTranslatorGUI(root, default_ui_lang=args.lang)
    root.mainloop()


if __name__ == "__main__":
    run_cli()
