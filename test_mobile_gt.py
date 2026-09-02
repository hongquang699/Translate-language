import sys
import urllib.request
import urllib.parse
import re
import html

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

text = "Hello world! This is an automated translation test."
url = f"https://translate.google.com/m?sl=auto&tl=vi&q={urllib.parse.quote(text)}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36"})
with urllib.request.urlopen(req) as resp:
    page = resp.read().decode("utf-8")

pattern = re.compile(r'class="(?:result-container|t0)">(.*?)</div>', re.DOTALL)
match = pattern.search(page)
if match:
    raw_res = match.group(1)
    clean_res = html.unescape(re.sub(r'<[^>]+>', '', raw_res))
    print("SUCCESS:")
    print(clean_res)
else:
    print("FAILED TO MATCH")
