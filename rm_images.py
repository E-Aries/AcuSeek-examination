import re
with open(r"D:\codex\examination\README.md", "r", encoding="utf-8") as f:
    c = f.read()
c = re.sub(r"!\[.*?\]\(screenshots/[^)]+\)\n?", "", c)
c = re.sub(r'<img\s+[^>]*src="screenshots/[^"]+"[^>]*/>\n?', "", c)
c = re.sub(r"\n{3,}", "\n\n", c)
with open(r"D:\codex\examination\README.md", "w", encoding="utf-8") as f:
    f.write(c)
print("Done")