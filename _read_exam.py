import re
content = open(r"D:\codex\examination\src\views\Exams.vue", "r", encoding="utf-8").read()

# Find the create dialog
i = content.find('showCreate" title=')
j = content.find("</el-dialog>", i) + 13
if i > 0 and j > i:
    length = j - i
    print(f"Create dialog: {i} to {j} ({length} chars)")
    print(content[i:j])