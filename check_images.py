import re, os

with open(r"D:\codex\examination\README.md", "r", encoding="utf-8") as f:
    content = f.read()

refs = set()
for m in re.finditer(r"""screenshots/([^"'()\s]+)""", content):
    refs.add(m.group(1))

files = set(os.listdir(r"D:\codex\examination\screenshots"))

missing = refs - files
print(f"README 引用了 {len(refs)} 张")
print(f"目录里有 {len(files)} 个文件")
if missing:
    print(f"引用了但不存在：{missing}")
else:
    print("所有引用一一对应，全部正确")