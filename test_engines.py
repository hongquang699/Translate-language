import sys
import urllib.request
import urllib.parse
import json
import re
import html

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_engine_1(text, src, tl):
    url = f"https://translate.google.com/m?sl={src}&tl={tl}&q={urllib.parse.quote(text)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        page = resp.read().decode("utf-8")
    m = re.search(r'class="(?:result-container|t0)">(.*?)</div>', page, re.DOTALL)
    if m:
        return html.unescape(re.sub(r'<[^>]+>', '', m.group(1)))
    raise Exception("Regex match failed")

def test_engine_2(text, src, tl):
    pair = f"{'en' if src == 'auto' else src}|{tl}"
    url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair={pair}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["responseData"]["translatedText"]

print("Engine 1 (Google Mobile):", test_engine_1("Hello world", "auto", "vi"))
print("Engine 2 (MyMemory):", test_engine_2("Good morning", "auto", "vi"))
