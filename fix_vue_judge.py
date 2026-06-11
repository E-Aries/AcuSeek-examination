with open(r"D:\codex\examination\src\views\TakeExam.vue", "r", encoding="utf-8") as f:
    c = f.read()

# Fix 1: selectOption - add judge text matching fallback
old1 = "    const correct = value === q.answer;\n    const qid = String(q.id);\n    practiceFeedback.value[qid] = { correct, correctAnswer: q.answer, userAnswer: value, explanation: q.explanation || \"\" };"
new1 = "    let correct = value === q.answer;\n    if (!correct && q.type === \"\u5224\u65ad\") {\n      const opt = q.options ? q.options.find(o => o.label === value) : null;\n      if (opt && (opt.text || opt.label) === q.answer) correct = true;\n    }\n    const qid = String(q.id);\n    practiceFeedback.value[qid] = { correct, correctAnswer: q.answer, userAnswer: value, explanation: q.explanation || \"\" };"
c = c.replace(old1, new1)

# Fix 2: isPracticeCorrect - add judge text matching for highlighting
old2 = "  const opt = q.options ? q.options.find(o => o.label === label) : null;\n    if (!opt) return false;\n    return opt.text || opt.label;\n  }\n\nfunction isPracticeCorrect(label) {"
new2 = "  const opt = q.options ? q.options.find(o => o.label === label) : null;\n    if (!opt) return false;\n    return opt.text || opt.label;\n  }\n\nfunction isPracticeCorrect(label) {\n  if (!practiceMode.value) return false;\n  const q = currentQuestion.value;\n  if (!q) return false;\n  const qid = String(q.id);\n  const fb = practiceFeedback.value[qid];\n  if (!fb) return false;\n  if (q.type === \"\u591a\u9009\") {\n    const ca = Array.isArray(fb.correctAnswer) ? fb.correctAnswer : (fb.correctAnswer || \"\").startsWith(\"[\") ? JSON.parse(fb.correctAnswer) : [fb.correctAnswer];\n    return fb.userAnswer && Array.isArray(fb.userAnswer) && fb.userAnswer.includes(label) && ca.includes(label);\n  }\n  if (q.type === \"\u5224\u65ad\" && fb.correctAnswer !== label) {\n    const opt = q.options ? q.options.find(o => o.label === label) : null;\n    if (opt && (opt.text || opt.label) === fb.correctAnswer) return true;\n  }\n  return fb.correctAnswer === label;\n}\n\nfunction isPracticeWrong(label) {"
c = c.replace(old2, new2)

with open(r"D:\codex\examination\src\views\TakeExam.vue", "w", encoding="utf-8") as f:
    f.write(c)

# Verify
with open(r"D:\codex\examination\src\views\TakeExam.vue", "r", encoding="utf-8") as f:
    c2 = f.read()
print("selectedOpt in file:", "(opt.text || opt.label) === q.answer" in c2)