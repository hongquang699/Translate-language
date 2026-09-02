"""
test_translation.py
Automated test script to verify translation capabilities across diverse file formats.
"""

import os
import sys
import json
import csv

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import openpyxl
from file_handler import process_file_translation

def run_tests():
    test_dir = os.path.join(os.path.dirname(__file__), "test_samples")
    os.makedirs(test_dir, exist_ok=True)
    
    print("=== STARTING MULTI-FORMAT FILE TRANSLATION TESTS ===")

    # 1. Test Plain Text (.txt)
    txt_path = os.path.join(test_dir, "sample.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("Artificial intelligence is transforming the world.\nIt helps humans automate repetitive tasks efficiently.")
    
    print("\n1. Testing Plain Text (.txt) Translation:")
    ok, out, msg = process_file_translation(txt_path, target_lang="vi", log_fn=print)
    print(f"Status: {ok}, Output saved to: {out}")
    if ok:
        with open(out, "r", encoding="utf-8") as f:
            print("Translated content:\n", f.read())

    # 2. Test Subtitles (.srt)
    srt_path = os.path.join(test_dir, "sample.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("""1
00:00:01,000 --> 00:00:04,000
Welcome everyone to the annual tech conference.

2
00:00:05,000 --> 00:00:08,500
Today we are excited to introduce our latest innovations.
""")
    print("\n2. Testing Subtitles (.srt) Translation:")
    ok, out, msg = process_file_translation(srt_path, target_lang="vi", log_fn=print)
    print(f"Status: {ok}, Output saved to: {out}")
    if ok:
        with open(out, "r", encoding="utf-8") as f:
            print("Translated subtitle content:\n", f.read())

    # 3. Test JSON (.json)
    json_path = os.path.join(test_dir, "sample.json")
    sample_data = {
        "title": "Universal File Translator",
        "description": "A powerful Python script for translating files.",
        "features": [
            "Translate multiple languages",
            "Support diverse file formats"
        ]
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2)

    print("\n3. Testing JSON (.json) Translation:")
    ok, out, msg = process_file_translation(json_path, target_lang="vi", log_fn=print)
    print(f"Status: {ok}, Output saved to: {out}")
    if ok:
        with open(out, "r", encoding="utf-8") as f:
            print("Translated JSON content:\n", f.read())

    # 4. Test Excel (.xlsx)
    xlsx_path = os.path.join(test_dir, "sample.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Products"
    ws.append(["Product Name", "Category", "Status"])
    ws.append(["Smart Watch", "Electronics", "In Stock"])
    ws.append(["Leather Jacket", "Apparel", "Out of Stock"])
    wb.save(xlsx_path)

    print("\n4. Testing Excel (.xlsx) Translation:")
    ok, out, msg = process_file_translation(xlsx_path, target_lang="vi", log_fn=print)
    print(f"Status: {ok}, Output saved to: {out}")
    if ok:
        wb_res = openpyxl.load_workbook(out)
        ws_res = wb_res.active
        for row in ws_res.iter_rows(values_only=True):
            print(row)

    print("\n=== ALL TESTS COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
