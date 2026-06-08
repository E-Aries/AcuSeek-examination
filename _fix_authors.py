import os

author = "\u8fbe\u54a9 | \u8f7b\u5219"
h_py = "# Author: " + author + "\n\n"
h_vue = "<!-- Author: " + author + " -->\n\n"
h_js = "// Author: " + author + "\n\n"

for root, dirs, files in os.walk(r"D:\codex\examination\backend"):
    for f in files:
        if not f.endswith(".py"): continue
        p = os.path.join(root, f)
        raw = open(p, "rb").read()
        if raw[:3] == b"\xef\xbb\xbf": raw = raw[3:]
        c = raw.decode("utf-8")
        for old in ['# Author: \u8fbe\u54a9\n# \u8f7b\u5219\n\n', '# Author: \u8fbe\u54a9 | \u8f7b\u5219\n\n']:
            if c.startswith(old): c = c[len(old):]
        c = h_py + c
        open(p, "wb").write(c.encode("utf-8"))

for root, dirs, files in os.walk(r"D:\codex\examination\src"):
    for f in files:
        if f.endswith(".vue"): h = h_vue
        elif f.endswith(".js"): h = h_js
        else: continue
        p = os.path.join(root, f)
        raw = open(p, "rb").read()
        if raw[:3] == b"\xef\xbb\xbf": raw = raw[3:]
        c = raw.decode("utf-8")
        for old in ['<!-- Author: \u8fbe\u54a9 | \u8f7b\u5219 -->\n\n', '// Author: \u8fbe\u54a9 | \u8f7b\u5219\n\n',
                    '# Author: \u8fbe\u54a9 | \u8f7b\u5219\n\n']:
            if c.startswith(old): c = c[len(old):]
        c = h + c
        open(p, "wb").write(c.encode("utf-8"))

raw = open(r"D:\codex\examination\src\main.js", "rb").read()
c = open(r"D:\codex\examination\src\main.js", "r", encoding="utf-8").read()
n = "\ufeff"
print("Has FEFF:", n in c)
print("Has BOM sequence:", b"\xef\xbb\xbf" in raw)
print("Header correct:", c.startswith(h_js))
print("First line:", repr(c.split("\n")[0]))