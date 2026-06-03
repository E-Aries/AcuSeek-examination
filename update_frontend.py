# -*- coding: utf-8 -*-
import os

os.chdir(r"D:\\codex\\examination")

def replace_script(file, new_script):
    with open(file, "r", encoding="utf-8-sig") as f:
        c = f.read()
    start = c.find("<script setup>")
    end = c.find("</script>", start)
    c = c[:start] + "<script setup>\n" + new_script + "\n</script>" + c[end + 8:]
    with open(file, "w", encoding="utf-8") as f:
        f.write(c)
    print(f"  {file}: updated")

# ===== Dashboard.vue =====
replace_script("src/views/Dashboard.vue", r"""
import { ref, computed, onMounted } from "vue";
import VChart from "vue-echarts";
import "echarts";
import { api } from "../api.js";

const stats = ref([]);
const recentExams = ref([]);
const todos = ref([]);

onMounted(async () => {
  try {
    const [qStats, rStats, examRes] = await Promise.all([
      api.questions.stats(),
      api.results.stats(),
      api.exams.list()
    ]);
    const totalQs = (qStats.items || []).reduce((s, i) => s + i.count, 0);
    stats.value = [
      { label: "题库总数", value: String(totalQs), icon: "Notebook", color: "var(--c-primary)", bg: "var(--c-primary-lighter)", trend: 0 },
      { label: "考核场次", value: String(rStats.exams_count || 0), icon: "EditPen", color: "var(--c-accent)", bg: "var(--c-accent-bg)", trend: 0 },
      { label: "参考人次", value: String(rStats.total_candidates || 0), icon: "UserFilled", color: "var(--c-info)", bg: "var(--c-info-bg)", trend: 0 },
      { label: "平均通过率", value: (rStats.pass_rate || 0) + "%", icon: "CircleCheck", color: "var(--c-success)", bg: "var(--c-success-bg)", trend: 0 },
    ];
    recentExams.value = (examRes.items || []).slice(0, 5).map(e => ({
      name: e.name, type: e.type, candidates: "-", avgScore: "-", date: e.status
    }));
    todos.value = [
      { text: "待批改试卷 " + (rStats.pending || 0) + " 份", meta: "需手动评分", urgent: (rStats.pending || 0) > 0 },
      { text: "确认本月考核安排", meta: "建议提前一周准备", urgent: false },
    ];
  } catch(e) { console.error(e); }
});

const examChartOption = computed(() => ({
  grid: { left: 40, right: 16, top: 20, bottom: 24 },
  xAxis: { type: "category", data: ["1月","2月","3月","4月","5月","6月"], axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: "#9CA3AF", fontSize: 11 } },
  yAxis: { type: "value", splitLine: { lineStyle: { color: "#F0EFEC" } }, axisLabel: { color: "#9CA3AF", fontSize: 11 } },
  series: [{ type: "bar", data: [8,12,15,10,18,14], barWidth: 28, borderRadius: [4,4,0,0], itemStyle: { color: "var(--c-primary)" } }],
  tooltip: { trigger: "axis" },
}));

const passChartOption = computed(() => ({
  grid: { left: 50, right: 30, top: 20, bottom: 24 },
  xAxis: { type: "category", data: ["售后流程","产品知识","故障处理","服务规范","安全合规"], axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: "#9CA3AF", fontSize: 11 } },
  yAxis: { type: "value", max: 100, splitLine: { lineStyle: { color: "#F0EFEC" } }, axisLabel: { color: "#9CA3AF", fontSize: 11, formatter: "{value}%" } },
  series: [{ type: "bar", data: [92,85,78,88,95], barWidth: 24, borderRadius: [4,4,0,0], itemStyle: { color: (p) => [ "var(--c-primary)","var(--c-info)","var(--c-warning)","var(--c-primary-light)","var(--c-success)" ][p.dataIndex] }, label: { show: true, position: "top", formatter: "{c}%", color: "#6B7280", fontSize: 11, fontWeight: 600 } }],
  tooltip: { trigger: "axis", formatter: (p) => p[0].name + "<br/>通过率：" + p[0].value + "%" },
}));
""")

# ===== Questions.vue =====
replace_script("src/views/Questions.vue", r"""
import { ref, computed, onMounted } from "vue";
import { Plus, Upload, Download, Search, Delete } from "@element-plus/icons-vue";
import { api } from "../api.js";
import { ElMessage, ElMessageBox } from "element-plus";

const search = ref("");
const filterType = ref("");
const filterCategory = ref("");
const currentPage = ref(1);
const showDialog = ref(false);
const questions = ref([]);
const editingId = ref(null);

onMounted(async () => {
  try {
    const qRes = await api.questions.list({size: 100});
    questions.value = (qRes.items || []).map(q => ({ ...q, difficulty: q.difficulty || 1, options: q.options || [], used: q.used_count || 0, lastUsed: "" }));
  } catch(e) { console.error(e); }
});

const newQuestion = ref({ type: "单选", category: "", content: "", options: [{ label: "A", text: "", correct: false }, { label: "B", text: "", correct: false }], difficulty: 1, explanation: "", answer: "" });

const filteredQuestions = computed(() => {
  let list = questions.value;
  if (filterType.value) list = list.filter(q => q.type === filterType.value);
  if (filterCategory.value) list = list.filter(q => q.category === filterCategory.value);
  if (search.value) list = list.filter(q => q.content.includes(search.value));
  return list;
});

function typeTag(type) { return { "单选": "", "多选": "success", "判断": "warning", "填空": "info", "简答": "danger" }[type] || ""; }

async function saveQuestion() {
  const q = { ...newQuestion.value };
  if (["单选", "判断"].includes(q.type)) q.answer = q.options.find(o => o.correct)?.label || "";
  else if (q.type === "多选") q.answer = JSON.stringify(q.options.filter(o => o.correct).map(o => o.label));
  try {
    if (editingId.value) { await api.questions.update(editingId.value, q); ElMessage.success("更新成功"); }
    else { await api.questions.create(q); ElMessage.success("创建成功"); }
    showDialog.value = false;
    editingId.value = null;
    const qRes = await api.questions.list({size: 100});
    questions.value = (qRes.items || []).map(q2 => ({ ...q2, difficulty: q2.difficulty || 1, options: q2.options || [] }));
  } catch(e) { ElMessage.error("操作失败"); }
}

async function deleteQuestion(id) {
  try {
    await ElMessageBox.confirm("确定删除此题？", "确认");
    await api.questions.delete(id);
    questions.value = questions.value.filter(q => q.id !== id);
    ElMessage.success("删除成功");
  } catch(e) {}
}

function handleImport() {
  const input = document.createElement("input");
  input.type = "file"; input.accept = ".xlsx,.csv";
  input.onchange = async (ev) => {
    const file = ev.target.files[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("/api/questions/import", { method: "POST", headers: { "Authorization": "Bearer " + localStorage.getItem("token") }, body: form });
      const data = await res.json();
      ElMessage.success(data.message);
      const qRes = await api.questions.list({size: 100});
      questions.value = (qRes.items || []).map(q2 => ({ ...q2, difficulty: q2.difficulty || 1, options: q2.options || [] }));
    } catch(e) { ElMessage.error("导入失败"); }
  };
  input.click();
}

function handleExport() {
  const csv = ["题型,分类,题目内容,选项,答案,难度,分值"];
  questions.value.forEach(q => {
    csv.push(q.type + "," + q.category + ",\"" + q.content + "\",\"" + JSON.stringify(q.options || []) + "\"," + (q.answer || "") + "," + (q.difficulty || 1) + "," + (q.score || 2));
  });
  const blob = new Blob([csv.join("\n")], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "题库模板.csv"; a.click();
}

function editQuestion(row) {
  editingId.value = row.id;
  newQuestion.value = { ...newQuestion.value, ...row, options: row.options || [] };
  showDialog.value = true;
}
""")

# ===== Exams.vue =====
replace_script("src/views/Exams.vue", r"""
import { ref, reactive, computed, onMounted } from "vue";
import { Plus, Search, Clock, Document, UserFilled, ArrowRight, CaretRight } from "@element-plus/icons-vue";
import { api } from "../api.js";
import { ElMessage } from "element-plus";

const search = ref("");
const filterStatus = ref("");
const showCreate = ref(false);
const exams = ref([]);

onMounted(async () => {
  try {
    const res = await api.exams.list();
    exams.value = (res.items || []).map(e => ({ ...e, questionCount: e.question_count, candidates: 0, date: e.status === "未开始" ? "待定" : "进行中" }));
  } catch(e) { console.error(e); }
});

const createForm = reactive({ name: "", type: "正式", duration: 60, questionCount: 30, passScore: 60, strategy: "random", categories: [], distribution: {} });

async function handleCreate() {
  try {
    await api.exams.create({ name: createForm.name, type: createForm.type, duration: createForm.duration, question_count: createForm.questionCount, pass_score: createForm.passScore, strategy: createForm.strategy, categories: createForm.categories, distribution: createForm.distribution });
    ElMessage.success("创建成功");
    showCreate.value = false;
    const res = await api.exams.list();
    exams.value = (res.items || []).map(e => ({ ...e, questionCount: e.question_count, candidates: 0, date: e.status }));
  } catch(e) { ElMessage.error("创建失败"); }
}

const filteredExams = computed(() => {
  let list = exams.value;
  if (filterStatus.value) list = list.filter(e => e.status === filterStatus.value);
  if (search.value) list = list.filter(e => e.name.includes(search.value));
  return list;
});
""")

# ===== TakeExam.vue =====
replace_script("src/views/TakeExam.vue", r"""
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, ArrowRight, Timer, Check } from "@element-plus/icons-vue";
import { api } from "../api.js";
import { ElMessage } from "element-plus";

const route = useRoute();
const router = useRouter();
const currentIndex = ref(0);
const answers = ref({});
const showSubmitConfirm = ref(false);
const questions = ref([]);
const examName = ref("加载中...");
const paperId = ref(null);
const remaining = ref(0);
let timer = null;

onMounted(async () => {
  try {
    const res = await api.exams.start(route.params.id);
    paperId.value = res.paper_id;
    questions.value = (res.questions || []).slice(0, 10); // limit for demo
    remaining.value = 3600;
    examName.value = "考试进行中";
    timer = setInterval(() => { if (remaining.value > 0) remaining.value--; else confirmSubmit(); }, 1000);
  } catch(e) { ElMessage.error("加载失败"); }
});

onUnmounted(() => { clearInterval(timer); });

const currentQuestion = computed(() => questions.value[currentIndex.value] || {});
const qTypeTag = computed(() => ({ "单选": "", "多选": "success", "判断": "warning", "填空": "info", "简答": "danger" }[currentQuestion.value.type] || ""));
const progressPercent = computed(() => ((currentIndex.value + 1) / questions.value.length) * 100);
const answeredCount = computed(() => questions.value.filter((_, i) => isAnswered(i)).length);
const formattedTime = computed(() => { const m = Math.floor(remaining.value / 60); const s = remaining.value % 60; return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0"); });

function isAnswered(i) {
  const q = questions.value[i];
  const ans = answers.value[i];
  if (!ans) return false;
  if (q.type === "填空" || q.type === "简答") return ans.trim() !== "";
  if (q.type === "多选") return Array.isArray(ans) && ans.length > 0;
  return !!ans;
}

function selectOption(value) { answers.value[currentIndex.value] = value; }
function toggleMulti(value) {
  const arr = answers.value[currentIndex.value] || [];
  answers.value[currentIndex.value] = arr.includes(value) ? arr.filter(v => v !== value) : [...arr, value];
}

function goToQuestion(i) { currentIndex.value = i; }
function prevQuestion() { if (currentIndex.value > 0) currentIndex.value--; }
function nextQuestion() { if (currentIndex.value < questions.value.length - 1) currentIndex.value++; }
function handleSubmit() { showSubmitConfirm.value = true; }

async function confirmSubmit() {
  clearInterval(timer);
  try {
    const res = await api.answers.submit(paperId.value, { questions: questions.value, answers: Object.fromEntries(Object.entries(answers.value).map(([k, v]) => [String(questions.value[k]?.id), v])), duration_used: 3600 - remaining.value });
    ElMessage.success("交卷成功！得分：" + (res.score || 0));
    router.push("/results/" + paperId.value);
  } catch(e) { ElMessage.error("交卷失败"); }
}

function handleQuit() { router.push("/exams"); }
""")

print("All 6 files updated!")
