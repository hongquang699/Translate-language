# 🌐 Universal File & Text Translator (Phần Mềm Dịch Thuật Đa Năng)

A powerful, all-in-one translation tool supporting **over 130+ languages** with dual UI language mode (English 🇬🇧 & Tiếng Việt 🇻🇳), available as a **Windows Desktop App (.exe)** and an **Android Mobile App (.apk)**.

---

## 📦 Ready-to-use Application Packages / Bản Cài Đặt Sẵn

| Platform | File Location | Description |
|---|---|---|
| **🪟 Windows App** | [`release/UniversalTranslator.exe`](file:///c:/Users/HOA%20BINH/Translate/release/UniversalTranslator.exe) | Standalone Windows application (No Python setup required). Just double-click to run! |
| **📱 Android APK** | [`release/UniversalTranslator.apk`](file:///c:/Users/HOA%20BINH/Translate/release/UniversalTranslator.apk) | Android application package for phones and tablets. |

---

## 🌟 Key Features / Tính Năng Nổi Bật

1. **🌐 Dual UI Language Mode (2 Chế độ ngôn ngữ giao diện):**
   - Switch between **🇻🇳 Tiếng Việt** and **🇬🇧 English** with a single click.
2. **📁 Diverse File Format Support (Hỗ trợ đa dạng tệp tin):**
   - **Microsoft Office:** Word (`.docx`), Excel (`.xlsx`), PowerPoint (`.pptx`) — *preserves original styles, tables, slides, and formatting*.
   - **PDF Documents:** (`.pdf`) extracts and translates page-by-page.
   - **Video Subtitles:** (`.srt`, `.vtt`) — *translates dialogues while strictly keeping timestamp codes and numbering intact*.
   - **Text & Code/Data:** (`.txt`, `.md`, `.json`, `.csv`, `.xml`, `.html`, `.log`, `.tex`, `.rtf`).
3. **🌍 Rich Language Selection (130+ Languages):**
   - English, Vietnamese, Chinese (Simplified & Traditional), Japanese, Korean, French, German, Spanish, Russian, Thai, Lao, Khmer, Arabic, Portuguese, Italian, Hindi, etc.
   - **Auto Detect** source language capability and quick language swap button (`⇄`).
4. **⚡ Smart Chunking & Asynchronous Processing:**
   - Automatically segments large files/paragraphs into safe chunks (< 3500 chars) to prevent API rate/payload limits.
   - Auto-retry with exponential backoff for unstable network connections.

---

## 🚀 How to Run & Install

### 1. On Windows (2 Options):
- **Option A (Direct EXE):** Double-click [`release/UniversalTranslator.exe`](file:///c:/Users/HOA%20BINH/Translate/release/UniversalTranslator.exe).
- **Option B (Python Script):** Double-click [`run_translator.bat`](file:///c:/Users/HOA%20BINH/Translate/run_translator.bat) or run `python translator_app.py`.

### 2. On Android:
- Copy [`release/UniversalTranslator.apk`](file:///c:/Users/HOA%20BINH/Translate/release/UniversalTranslator.apk) to your Android device and install it directly.

---

## 🔄 GitHub Synchronization (Đồng Bộ Mã Nguồn)
- **1-Click Push:** Double-click [`push_to_github.bat`](file:///c:/Users/HOA%20BINH/Translate/push_to_github.bat) to automatically stage, commit, and push all files to [`hongquang699/Translate-language`](https://github.com/hongquang699/Translate-language).
- **Command Line:** Run `python github_service.py "Your commit message"`
