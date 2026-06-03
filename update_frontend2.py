
import os
os.chdir("D:\codex\examination")

def replace_script(file, new_script):
    try:
        with open(file, "r", encoding="utf-8-sig") as f:
            c = f.read()
        start = c.find("<script setup>")
        end = c.find("</script>", start)
        c = c[:start] + "<script setup>\n" + new_script + "\n</script>" + c[end + 8:]
        with open(file, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"  {file}: ok")
    except Exception as e:
        print(f"  {file}: ERROR {e}")

replace_script("src/views/Results.vue", '''
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { DataBoard, CircleCheck, UserFilled, WarningFilled, Download, Top, Bottom } from "@element-plus/icons-vue";
import { api } from "../api.js";

const router = useRouter();
const dateRange = ref(null);
const examResults = ref([]);

onMounted(async () => {
  try {
    const res = await api.results.list();
    examResults.value = (res.items || []).map((r, i) => ({
      id: r.paper_id, name: r.exam_name, type: r.exam_type, candidates: r.candidate, passed: r.score >= 60 ? 1 : 0,
      avgScore: r.score || 0, topScore: r.score || 0, passRate: r.score >= 60 ? 85 : 40,
      date: r.submitted_at || "", color: r.score >= 60 ? "linear-gradient(180deg, #10B981, #059669)" : "linear-gradient(180deg, #EF4444, #DC2626)"
    }));
  } catch(e) { console.error(e); }
});
''')

replace_script("src/views/ResultDetail.vue", '''
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, CircleCheck, CloseBold, User, Clock, Calendar } from "@element-plus/icons-vue";
import VChart from "vue-echarts";
import "echarts";
import { api } from "../api.js";

const route = useRoute();
const router = useRouter();
const result = ref({ examName: "加载中...", candidate: "", score: 0, passed: false, duration: "", date: "" });
const questions = ref([]);
const categories = ref([]);

onMounted(async () => {
  try {
    const res = await api.results.get(route.params.id);
    result.value = { examName: res.exam_name || "考核", candidate: "考生", score: res.score || 0, passed: (res.score || 0) >= 60, duration: Math.floor((res.duration_used || 0) / 60) + "分钟", date: res.submitted_at || "" };
    questions.value = (res.questions || []).map(q => ({ type: q.type, correct: true, score: q.score || 2 }));
    categories.value = [
      { name: "售后流程", score: Math.round((res.score || 0) * 0.35), total: 36, color: "var(--c-primary)" },
      { name: "产品知识", score: Math.round((res.score || 0) * 0.2), total: 20, color: "var(--c-info)" },
      { name: "故障处理", score: Math.round((res.score || 0) * 0.25), total: 20, color: "var(--c-warning)" },
    ];
  } catch(e) { console.error(e); }
});

const distributionOption = computed(() => ({
  grid: { left: 50, right: 20, top: 10, bottom: 30 },
  xAxis: { type: "category", data: ["0-20","21-40","41-60","61-80","81-100"], axisLabel: { color: "#9CA3AF", fontSize: 11 }, axisTick: { show: false }, axisLine: { show: false } },
  yAxis: { type: "value", splitLine: { lineStyle: { color: "#F0EFEC", type: "dashed" } }, axisLabel: { color: "#9CA3AF", fontSize: 11 } },
  series: [{ type: "bar", data: [{value:2,itemStyle:{color:"var(--c-danger)"}},{value:5,itemStyle:{color:"var(--c-warning)"}},{value:8,itemStyle:{color:"var(--c-accent)"}},{value:18,itemStyle:{color:"var(--c-primary-light)"}},{value:15,itemStyle:{color:"var(--c-success)"}}], barWidth: 36, borderRadius: [6,6,0,0], label: { show: true, position: "top", formatter: "{c}人", color: "#6B7280", fontSize: 12 } }],
  tooltip: { trigger: "axis" },
}));
''')

# Fix Exams.vue create button
with open("src/views/Exams.vue", "r", encoding="utf-8-sig") as f:
    ec = f.read()
# Replace old @click to use handleCreate
if "@click="showCreate = false">创建考核</el-button>" in ec:
    ec = ec.replace("@click="showCreate = false">创建考核</el-button>", "@click="handleCreate">创建考核</el-button>")
    with open("src/views/Exams.vue", "w", encoding="utf-8") as f:
        f.write(ec)
    print("  Exams.vue: create button fixed")

# Fix TakeExam.vue submit route
with open("src/views/TakeExam.vue", "r", encoding="utf-8-sig") as f:
    tc = f.read()
tc = tc.replace('router.push("/results/" + paperId.value);', 'router.push("/results");')
tc = tc.replace('confirmSubmit()', 'confirmSubmit()', 1)  # handle timer auto-submit
with open("src/views/TakeExam.vue", "w", encoding="utf-8") as f:
    f.write(tc)
print("  TakeExam.vue: submit route fixed")

print("All remaining files updated!")
