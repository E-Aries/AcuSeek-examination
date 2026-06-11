with open(r"D:\codex\examination\src\views\TakeExam.vue", "r", encoding="utf-8") as f:
    c = f.read()

old = '''  if (practiceMode.value) {
    const q = questions.value[currentIndex.value];
    const qid = String(q.id);
    const correct = value === q.answer;
    practiceFeedback.value[qid] = { correct, correctAnswer: q.answer, userAnswer: value, explanation: q.explanation || "" };
  }'''

new = '''  if (practiceMode.value) {
    const q = questions.value[currentIndex.value];
    const qid = String(q.id);
    let correct = value === q.answer;
    if (!correct && q.type === "\u5224\u65ad") {
      const selectedOpt = q.options ? q.options.find(o => o.label === value) : null;
      if (selectedOpt && (selectedOpt.text || selectedOpt.label) === q.answer) correct = true;
    }
    practiceFeedback.value[qid] = { correct, correctAnswer: q.answer, userAnswer: value, explanation: q.explanation || "" };
  }'''

c = c.replace(old, new)
with open(r"D:\codex\examination\src\views\TakeExam.vue", "w", encoding="utf-8") as f:
    f.write(c)

print("Fixed:", "opt_map" not in c and "(selectedOpt.text || selectedOpt.label) === q.answer" in c)