# === ExamDetail.vue: add manual flag to gradeDetails ===
path1 = r"D:\codex\examination\src\views\ExamDetail.vue"
c1 = open(path1, "r", encoding="utf-8").read()

old1 = "correct: q.correct === true\n      };"
new1 = "correct: q.correct === true,\n        manual: !q.autoGraded\n      };"

c1 = c1.replace(old1, new1)
open(path1, "w", encoding="utf-8").write(c1)
print("ExamDetail: manual flag added")

# === ResultDetail.vue: add manualGraded, show badge ===
path2 = r"D:\codex\examination\src\views\ResultDetail.vue"
c2 = open(path2, "r", encoding="utf-8").read()

old2 = "manualScore: mGrade ? mGrade.score : null,"
new2 = "manualScore: mGrade ? mGrade.score : null,\n        manualGraded: mGrade ? mGrade.manual : false,"

c2 = c2.replace(old2, new2)
print("ResultDetail: manualGraded added")

# Add (手工判分) badge to collapsed score
old3 = "{{ q.manualScore !== null ? q.manualScore : (q.correct === true ? q.score : 0) }}/{{ q.score }}"
new3 = "{{ q.manualScore !== null ? q.manualScore : (q.correct === true ? q.score : 0) }}/{{ q.score }}<span v-if=\"q.manualGraded\" class=\"manual-badge\">\u624b\u5de5\u8bc4\u5206</span>"

c2 = c2.replace(old3, new3)
print("ResultDetail: collapsed badge added")

# Add badge to expanded score section
old4 = "{{ q.manualScore !== null ? q.manualScore : (q.correct === true ? q.score : 0) }} / {{ q.score }}"
new4 = "{{ q.manualScore !== null ? q.manualScore : (q.correct === true ? q.score : 0) }} / {{ q.score }}<span v-if=\"q.manualGraded\" style=\"font-size:11px;font-weight:400;margin-left:6px;padding:1px 6px;border-radius:3px;background:rgba(245,158,11,0.15);color:#D97706\">\u624b\u5de5\u8bc4\u5206</span>"

c2 = c2.replace(old4, new4)
print("ResultDetail: expanded badge added")

# Add CSS for manual-badge
old_css = ".rd-score-status { font-size: 12px; font-weight: 500; opacity: 0.7; }"
new_css = ".rd-score-status { font-size: 12px; font-weight: 500; opacity: 0.7; }\n.manual-badge { font-size: 11px; font-weight: 500; margin-left: 6px; padding: 1px 6px; border-radius: 3px; background: rgba(245,158,11,0.15); color: #D97706; }"

c2 = c2.replace(old_css, new_css)
print("ResultDetail: CSS added")

open(path2, "w", encoding="utf-8").write(c2)
print("Done")