import re
path = r"D:\codex\examination\src\main.js"
content = open(path, "r", encoding="utf-8").read()
content = content.replace("\ufeff", "")
content = content.replace('from "vue"', 'from "/node_modules/vue/dist/vue.esm-bundler.js"')
open(path, "w", encoding="utf-8").write(content)
print("main.js fixed")
# Verify
c = open(path, "r", encoding="utf-8").read()
print("FEFF:", "\ufeff" in c)
print("resolved:", "/node_modules/vue/dist/vue.esm-bundler.js" in c)