<template>
  <div class="exam-detail">
    <!-- Header -->
    <div class="detail-header">
      <div class="detail-header-left">
        <el-button text :icon="ArrowLeft" @click="$router.push('/exams')" class="back-btn">返回</el-button>
        <div>
          <div class="detail-type-badge">
            <span class="exam-type-badge" :class="exam.type">{{ exam.type }}</span>
            <el-tag :type="exam.status === '进行中' ? 'danger' : exam.status === '未开始' ? 'info' : ''" size="small" effect="light" round>{{ exam.status }}</el-tag>
          </div>
          <h1 class="detail-title">{{ exam.name }}</h1>
        </div>
      </div>
      <div class="detail-header-right">
      <el-button :icon="Edit" @click="openEditDialog" text>编辑</el-button>
      <el-button :icon="Delete" @click="confirmDelete" type="danger" text>删除</el-button>
        <el-button v-if="exam.status === '未开始'" type="primary" :icon="CaretRight" @click="publishExam">发布考核</el-button>
        <el-button v-if="exam.status === '进行中'" type="warning" :icon="Close" @click="closeExam">结束考核</el-button>
        <el-button v-if="exam.status === '已结束'" type="primary" :icon="CaretRight" @click="publishExam">重新发布</el-button>
        <el-button text :icon="Share" @click="copyShareLink">分享</el-button>
      </div>
    </div>

    <!-- Stats -->
    <div class="detail-stats">
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ exam.duration }}</span>
        <span class="detail-stat-label">考试时长（分钟）</span>
      </div>
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ paperQuestions.length || exam.question_count }}</span>
        <span class="detail-stat-label">题目数量</span>
      </div>
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ detail.total_candidates }}</span>
        <span class="detail-stat-label">参考人数</span>
      </div>
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ detail.pass_rate }}%</span>
        <span class="detail-stat-label">通过率</span>
      </div>
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ detail.avg_score }}</span>
        <span class="detail-stat-label">平均分</span>
      </div>
    </div>

    <!-- Tabs: Candidates, Scores, Config -->
    <el-card shadow="never" class="detail-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane name="paper">
          <template #label>
            <span>组卷管理 <span style="font-size:12px;color:var(--c-text-tertiary);margin-left:4px">({{ paperQuestions.length }}题 / {{ paperTotalScore }}分)</span></span>
          </template>
          <div class="toolbar-inline">

            <div style="display:flex;gap:8px">
              <el-button size="small" :icon="Refresh" @click="generatePaper" :loading="generating">
                生成试卷
              </el-button>

            </div>
          </div>
          <el-table :data="paperQuestions" stripe style="width:100%" class="detail-table" v-loading="generating">
            <el-table-column type="index" label="#" width="40" align="right" />
            <el-table-column label="题目" min-width="300">
              <template #default="{ row }">
                <div class="question-cell">
                  <el-tag :type="typeTag(row.type)" size="small" effect="plain" class="q-type">{{ row.type }}</el-tag>
                  <span class="q-text">{{ row.content }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="分类" width="90" prop="category" />
            <el-table-column label="难度" width="80" align="center">
              <template #default="{ row }">
                <el-rate v-model="row.difficulty" :max="3" disabled :colors="['var(--c-success)','var(--c-warning)','var(--c-danger)']" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="分值" width="60" align="right" prop="score" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="考生成绩" name="scores">
          <div class="toolbar-inline">
            <el-input v-model="candidateSearch" placeholder="搜索考生姓名..." clearable :prefix-icon="Search" class="search-sm" />
            <el-tag v-if="pendingCount > 0" type="warning" effect="plain">
              待批改 {{ pendingCount }} 份
            </el-tag>
            <span v-else style="color:var(--c-text-tertiary);font-size:13px">共 {{ candidates.length }} 人</span>
          <el-button :icon="Download" size="small" text type="primary" @click="exportCandidates">导出</el-button>
          </div>
          <el-table :data="filteredCandidates" stripe style="width:100%" class="detail-table" v-loading="loading">
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="department" label="部门" width="140" />
            <el-table-column label="成绩" width="90" align="right">
              <template #default="{ row }">
                <span v-if="row.score !== null" :style="{ color: row.score >= (exam.pass_score || 60) ? 'var(--c-success)' : 'var(--c-danger)', fontWeight: 600 }">{{ row.score }}</span>
                <span v-else style="color:var(--c-text-tertiary)">-</span>
              </template>
            </el-table-column>
            <el-table-column <el-table-column label="结果" width="90">
              <template #default="{ row }">
                <span v-if="row.status === '已完成'" :style="gradeTagStyle(row.score, row.total_score)">{{ getGrade(row.score, row.total_score).label }}</span>
                <span v-else-if="row.status === '待批改'" style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;background:#FEF3C7;color:#D97706">待批改</span>
                <span v-else style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;background:#F3F4F6;color:#9CA3AF">进行中</span>
              </template>
            </el-table-column>            <el-table-column label="用时" width="80" align="right">
              <template #default="{ row }">
                <span v-if="row.duration_used">{{ Math.floor(row.duration_used / 60) }}分</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="提交时间" width="160">
              <template #default="{ row }">
                <span v-if="row.submitted_at">{{ row.submitted_at.slice(0, 16) }}</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === '待批改'" text type="warning" size="small" @click="openGradeDialog(row)">批改</el-button>
                <el-button v-else-if="row.status === '已完成'" text type="primary" size="small" @click="$router.push('/results/' + row.paper_id)">详情</el-button>
                <el-button v-if="exam.type !== '模拟' && row.status === '已完成' && (row.score < (exam.pass_score || 60))" text type="danger" size="small" @click="handleRetake(row)">补考</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="试卷配置" name="config">
          <div class="config-section">
            <div class="config-grid">
              <div class="config-item">
                <span class="config-label">组卷策略</span>
                <span class="config-value">{{ exam.strategy === 'random' ? '随机组卷' : '手动组卷' }}</span>
              </div>
              <div class="config-item">
                <span class="config-label">及格线</span>
                <span class="config-value">{{ exam.pass_score || 60 }} 分</span>
              </div>
              <div class="config-item">
                <span class="config-label">题目分类</span>
                <span class="config-value">{{ examCategories }}</span>
              </div>
              <div class="config-item">
                <span class="config-label">考试状态</span>
                <span class="config-value">
                  <el-tag :type="exam.status === '进行中' ? 'danger' : exam.status === '未开始' ? 'info' : ''" size="small" effect="light" round>{{ exam.status }}</el-tag>
                </span>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Grade Dialog -->
    <el-dialog v-model="showGradeDialog" title="逐题批改" width="700px" :close-on-click-modal="false">
      <div class="grade-form">
        <div class="grade-header">
          <span>考生：<strong>{{ gradingPaper.name }}</strong></span>
          <span style="color:var(--c-text-tertiary);font-size:13px">总分：{{ gradeTotalScore }} / {{ gradeMaxScore }}</span>
        </div>
        <div v-loading="gradeLoading" class="grade-questions">
          <div v-for="(q, i) in gradeQuestions" :key="i" class="grade-q-item" :class="{ 'grade-auto': q.autoGraded, 'grade-manual': !q.autoGraded }">
            <div class="grade-q-header">
              <span class="grade-q-num">第 {{ i + 1 }} 题</span>
              <el-tag :type="qTypeTag(q.type)" size="small" effect="plain">{{ q.type }}</el-tag>
              <span class="grade-q-score">{{ q.score }} 分</span>
              <el-tag v-if="q.autoGraded" :type="q.correct ? 'success' : 'danger'" size="small" effect="light" round>
                {{ q.correct ? "正确" : "错误" }}
              </el-tag>
            </div>
            <div class="grade-q-content">{{ q.content }}</div>
            <div v-if="q.userAnswer !== undefined && q.userAnswer !== null" class="grade-answer">
              <span class="grade-answer-label">考生答案：</span>
              <span class="grade-answer-text">{{ formatAnswer(q.userAnswer) }}</span>
            </div>
            <div v-if="q.correctAnswer" class="grade-correct">
              <span class="grade-correct-label">正确答案：</span>
              <span class="grade-correct-text">{{ q.correctAnswer }}</span>
            </div>
            <div v-if="!q.autoGraded" class="grade-input">
              <span class="grade-input-label">给分：</span>
              <el-input-number v-model="q.manualScore" :min="0" :max="q.score" :step="1" size="small" style="width:120px" @change="recalcGradeTotal" />
              <span style="margin-left:4px;color:var(--c-text-tertiary);font-size:12px">/ {{ q.score }} 分</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showGradeDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmGrade" :loading="gradeSubmitting">
          确认批改（{{ gradeTotalScore }} 分）
        </el-button>
      </template>
    </el-dialog>
    <!-- Edit Dialog -->
    <el-dialog v-model="showEditDialog" title="编辑考核" width="600px" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="考核名称">
          <el-input v-model="editForm.name" placeholder="请输入考核名称" />
        </el-form-item>
        <el-form-item label="考核类型">
          <el-radio-group v-model="editForm.type">
            <el-radio value="正式">正式考核</el-radio>
            <el-radio value="练习">练习模式</el-radio>
            <el-radio value="模拟">模拟考试</el-radio>
          </el-radio-group>
        </el-form-item>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
          <el-form-item label="考试时长（分钟）">
            <el-input-number v-model="editForm.duration" :min="5" :max="180" :step="5" style="width:100%" />
          </el-form-item>
          <el-form-item label="题目数量">
            <el-input-number v-model="editForm.questionCount" :min="5" :max="100" style="width:100%" @change="editOnQCountChange" />
          </el-form-item>
        </div>
        <el-form-item label="组卷方式">
          <el-radio-group v-model="editForm.strategy">
            <el-radio value="random">随机组卷</el-radio>
          </el-radio-group>
        </el-form-item>
                <el-form-item v-if="editForm.strategy === &#39;random&#39;" label="题型分布">
          <div class="dist-config">
            <div v-for="(dist, key) in editForm.distribution" :key="key" class="dist-row">
              <span class="dist-label">{{ key }}</span>
              <el-slider v-model="dist.count" :min="0" :max="30" :marks="{ 0: &#39;0&#39;, 10: &#39;10&#39;, 20: &#39;20&#39;, 30: &#39;30&#39; }" show-input size="small" @change="editSyncDistTotal" />
            </div>
          </div>
          <div v-if="editFormDistTotal > 0" class="dist-total">合计 <strong>{{ editFormDistTotal }}</strong> 题</div>
        </el-form-item>
        <el-form-item label="关联分类">
          <el-select v-model="editForm.categories" multiple placeholder="选择分类" style="width:100%">
            <el-option v-for="c in categoryList" :key="c.id" :label="c.name" :value="c.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ArrowLeft, CaretRight, Share, Close, Search, Edit, Delete, Download } from "@element-plus/icons-vue"
import { api } from "../api.js";
import { ElMessage, ElMessageBox } from "element-plus"

const router = useRouter()
const route = useRoute();
const activeTab = ref("scores");
const candidateSearch = ref("");
const loading = ref(false);
const showGradeDialog = ref(false);
const showEditDialog = ref(false)
const paperQuestions = ref([])
const generating = ref(false)
const paperTotalScore = computed(() => paperQuestions.value.reduce((s, q) => s + (q.score || 2), 0))
const showAddQuestions = ref(false)
const questionSearch = ref("")
const availableQuestions = ref([])
const addBtnDisabled = computed(() => {
  try { return addTableRef.value ? (addTableRef.value.getSelectionRows() || []).length === 0 : true; } catch(e) { return true; }
});
const selectedAddCount = computed(() => {
  try { return addTableRef.value ? (addTableRef.value.getSelectionRows() || []).length : 0; } catch(e) { return 0; }
});
const editForm = reactive({ name: "", type: "正式", duration: 60, questionCount: 30, passScore: 60, strategy: "random", categories: [], distribution: {} });

const gradingPaper = ref({});
const gradeScore = ref(0);
const gradeQuestions = ref([]);
const gradeLoading = ref(false);
const gradeSubmitting = ref(false);
const gradeTotalScore = ref(0);
const gradeMaxScore = ref(0);

const exam = ref({});
const detail = ref({});
const allCandidates = ref([]);

const examCategories = computed(() => {
  const cats = exam.value.categories;
  if (!cats || !Array.isArray(cats) || cats.length === 0) return "全部";
  return cats.join("、");
});

const candidates = computed(() => allCandidates.value);
const pendingCount = computed(() => allCandidates.value.filter(c => c.status === "待批改").length);

const filteredCandidates = computed(() => {
  if (!candidateSearch.value) return allCandidates.value;
  return allCandidates.value.filter(c => c.name.includes(candidateSearch.value));
});

function typeTag(type) { return { "单选": "", "多选": "success", "判断": "warning", "填空": "info", "简答": "danger" }[type] || ""; }

async function generatePaper() {
  generating.value = true;
  try {
    const res = await api.exams.generate(route.params.id);
    paperQuestions.value = res.items || [];
    ElMessage.success("试卷已生成");
  } catch(e) {
    ElMessage.error("生成失败");
  } finally {
    generating.value = false;
  }
}

async function handleRetake(row) {
  try {
    await ElMessageBox.confirm("确定允许 " + row.name + " 补考？该考生的成绩记录将被清除。", "确认补考");
    await api.exams.retake(route.params.id, row.user_id);
    ElMessage.success("已允许补考，考生可以重新考试");
    await loadCandidates();
  } catch(e) { if (e !== "cancel") ElMessage.error("操作失败"); }
}

async function gradeTagStyle(score, total) {
  if (!total || score === null || score === undefined) return { backgroundColor: "#F3F4F6", color: "#9CA3AF", borderRadius: "4px", padding: "2px 8px", fontSize: "12px", fontWeight: 600, display: "inline-block" };
  var pct = score / total;
  if (pct >= 0.95) return { backgroundColor: "#FEF3C7", color: "#D97706", borderRadius: "4px", padding: "2px 8px", fontSize: "12px", fontWeight: 600, display: "inline-block" };
  if (pct >= 0.80) return { backgroundColor: "#DBEAFE", color: "#2563EB", borderRadius: "4px", padding: "2px 8px", fontSize: "12px", fontWeight: 600, display: "inline-block" };
  if (pct >= 0.60) return { backgroundColor: "#D1FAE5", color: "#059669", borderRadius: "4px", padding: "2px 8px", fontSize: "12px", fontWeight: 600, display: "inline-block" };
  return { backgroundColor: "#FEE2E2", color: "#DC2626", borderRadius: "4px", padding: "2px 8px", fontSize: "12px", fontWeight: 600, display: "inline-block" };
}

function getGrade(score, total) {
  if (!total || score === null || score === undefined) return { label: "-", type: "info" };
  var pct = score / total;
  if (pct >= 0.95) return { label: "优秀", type: "warning" };
  if (pct >= 0.80) return { label: "良好", type: "primary" };
  if (pct >= 0.60) return { label: "通过", type: "success" };
  return { label: "未通过", type: "danger" };
}

async function loadCandidates() {
  try {
    const papersRes = await api.exams.papers(route.params.id);
    allCandidates.value = (papersRes.items || []).map(p => ({
      paper_id: p.paper_id, name: p.name, department: p.department || "",
      score: p.score, status: p.status, user_id: p.user_id,
      duration_used: p.duration_used, submitted_at: p.submitted_at,
      total_score: p.total_score
    }));
  } catch(e) {}
}

async function loadPaper() {
  try {
    const res = await api.exams.questions(route.params.id);
    paperQuestions.value = res.items || [];
  } catch(e) {}
}

onMounted(async () => {
  loading.value = true;
  try {
    const [examRes, detailRes, papersRes] = await Promise.all([
      api.exams.get(route.params.id),
      api.exams.detail(route.params.id),
      api.exams.papers(route.params.id)
    ]);
    exam.value = examRes;
    detail.value = detailRes;
    allCandidates.value = (papersRes.items || []).map(p => ({
      paper_id: p.paper_id, name: p.name, department: p.department || "",
      score: p.score, status: p.status, user_id: p.user_id,
      duration_used: p.duration_used, submitted_at: p.submitted_at,
      total_score: p.total_score
    }));
  } catch(e) { ElMessage.error("加载考试数据失败"); }
  loadPaper();
  loading.value = false;
});

async function publishExam() {
  try {
    const res = await api.exams.updateStatus(route.params.id, "进行中");
    exam.value.status = "进行中";
    ElMessage.success(res.message);
  } catch(e) { ElMessage.error("发布失败"); }
}

async function closeExam() {
  try {
    const res = await api.exams.updateStatus(route.params.id, "已结束");
    exam.value.status = "已结束";
    ElMessage.success(res.message);
  } catch(e) { ElMessage.error("关闭失败"); }
}

function qTypeTag(type) { return { "单选": "", "多选": "success", "判断": "warning", "填空": "info", "简答": "danger" }[type] || ""; }

function formatAnswer(ans) {
  if (ans === null || ans === undefined) return "未作答";
  if (Array.isArray(ans)) return ans.join(", ");
  return String(ans);
}

function autoGrade(type, userAns, correctAns, options) {
  if (userAns === undefined || userAns === null) return false;
  if (type === "简答") return null;
  if (type === "判断") {
    if (options && options.length) {
      var optMap = {};
      options.forEach(function(o) { optMap[o.label] = o.text; });
      var userAnsText = optMap[String(userAns).trim()] || String(userAns).trim();
      return userAnsText === String(correctAns).trim();
    }
    return String(userAns).trim() === String(correctAns).trim();
  }
  if (type === "单选") return String(userAns).trim() === String(correctAns).trim();
  if (type === "多选") {
    const ua = new Set(Array.isArray(userAns) ? userAns.map(String) : [String(userAns)]);
    try {
      var ca;
      if (correctAns.startsWith("[")) {
        ca = new Set(JSON.parse(correctAns).map(String));
      } else {
        ca = new Set(correctAns.split(",").map(function(s) { return s.trim(); }).filter(function(s) { return s; }));
      }
      return ua.size === ca.size && [...ua].every(v => ca.has(v));
    } catch(e) { return false; }
  }
  if (type === "填空") return String(userAns || "").trim() === String(correctAns).trim();
  return false;
}

async function openGradeDialog(row) {
  gradingPaper.value = row;
  showGradeDialog.value = true;
  gradeLoading.value = true;
  gradeQuestions.value = [];
  try {
    const [paperRes, qRes] = await Promise.all([
      api.exams.paper(row.paper_id),
      api.questions.list({ size: 999 })
    ]);
    const allQs = qRes.items || [];
    const qMap = {};
    allQs.forEach(function(q) { qMap[q.id] = q; });
    const questions = paperRes.questions || [];
    const answers = paperRes.answers || {};
    const qs = [];
    questions.forEach(pq => {
      const qid = String(pq.id);
      const userAns = answers[qid];
      const fullQ = qMap[pq.id] || {};
      const correctAns = fullQ.answer || "";
      const isAuto = pq.type !== "简答";
      const correct = autoGrade(pq.type, userAns, correctAns, fullQ.options);
      qs.push({
        ...pq,
        userAnswer: userAns,
        correctAnswer: correctAns,
        autoGraded: isAuto,
        correct: correct === true,
        manualScore: correct === true ? pq.score : (correct === false ? 0 : Math.round((pq.score || 2) * 0.5))
      });
    });
    gradeQuestions.value = qs;
    recalcGradeTotal();
  } catch(e) {
    ElMessage.error("加载试卷失败");
  } finally {
    gradeLoading.value = false;
  }
}

function recalcGradeTotal() {
  let total = 0;
  gradeQuestions.value.forEach(q => {
    if (q.autoGraded) {
      total += q.correct ? (q.score || 2) : 0;
    } else {
      total += (q.manualScore || 0);
    }
  });
  gradeTotalScore.value = total;
  gradeMaxScore.value = gradeQuestions.value.reduce((s, q) => s + (q.score || 2), 0);
}

async function confirmGrade() {
  gradeSubmitting.value = true;
  try {
    var gradeDetails = {};
    gradeQuestions.value.forEach(function(q) {
      gradeDetails[String(q.id)] = {
        score: q.autoGraded ? (q.correct ? q.score : 0) : (q.manualScore || 0),
        maxScore: q.score,
        correct: q.correct === true,
        manual: !q.autoGraded
      };
    });
    await api.answers.grade(gradingPaper.value.paper_id, { score: gradeTotalScore.value, details: gradeDetails });
    ElMessage.success("批改完成，得分：" + gradeTotalScore.value);
    showGradeDialog.value = false;
    const papersRes = await api.exams.papers(route.params.id);
    allCandidates.value = (papersRes.items || []).map(p => ({
      paper_id: p.paper_id, name: p.name, department: p.department || "",
      score: p.score, status: p.status, user_id: p.user_id,
      duration_used: p.duration_used, submitted_at: p.submitted_at,
      total_score: p.total_score
    }));
  } catch(e) { ElMessage.error("批改失败"); }
  gradeSubmitting.value = false;
}

function exportCandidates() {
  const token = localStorage.getItem("token")
  const a = document.createElement("a")
  const url = "/api/exams/" + route.params.id + "/export"
  fetch(url, { headers: { Authorization: "Bearer " + token } })
    .then(r => r.blob())
    .then(blob => {
      a.href = URL.createObjectURL(blob)
      a.download = "考核成绩_" + route.params.id + ".csv"
      a.click()
      URL.revokeObjectURL(a.href)
    })
    .catch(() => ElMessage.error("导出失败"))
}

function copyShareLink() {
  const link = window.location.origin + "/exams/" + route.params.id + "/take";
  navigator.clipboard.writeText(link).then(() => ElMessage.success("考试链接已复制"));
}

const editFormDistTotal = computed(() => {
  let total = 0;
  for (var k in (editForm.distribution || {})) {
    if (editForm.distribution[k] && editForm.distribution[k].count) {
      total += editForm.distribution[k].count;
    }
  }
  return total;
});
function editSyncDistTotal() {
  editForm.questionCount = editFormDistTotal.value;
}
function editOnQCountChange(val) {
  for (var k in editForm.distribution) {
    if (editForm.distribution[k]) editForm.distribution[k].count = 0;
  }
}

async function openEditDialog() {
  try {
    const r = await api.categories.list();
    categoryList.value = (r.items || []);
  } catch(e) {}

  editForm.name = exam.value.name
  editForm.type = exam.value.type
  editForm.duration = exam.value.duration
  editForm.questionCount = exam.value.question_count
  editForm.passScore = exam.value.pass_score
  editForm.strategy = exam.value.strategy
  editForm.categories = exam.value.categories || []
  editForm.distribution = exam.value.distribution || {}
  showEditDialog.value = true
}

async function saveEdit() {
  try {
    await api.exams.update(route.params.id, {
      name: editForm.name, type: editForm.type, duration: editForm.duration,
      question_count: editForm.questionCount, pass_score: editForm.passScore,
      strategy: editForm.strategy, categories: editForm.categories,
      distribution: editForm.distribution
    })
    ElMessage.success("更新成功")
    showEditDialog.value = false
    const examRes = await api.exams.get(route.params.id)
    exam.value = examRes
  } catch(e) { ElMessage.error("更新失败") }
}

function confirmDelete() {
  ElMessageBox.confirm("确定要删除该考核吗？相关试卷记录也会被删除。", "确认删除", {
    confirmButtonText: "删除", cancelButtonText: "取消", type: "warning"
  }).then(async () => {
    await api.exams.delete(route.params.id)
    ElMessage.success("已删除")
    router.push("/exams")
  }).catch(() => {})
}
</script>

<style scoped>
.dist-config { display: flex; flex-direction: column; gap: 12px; width: 100%; }
.dist-row { display: flex; align-items: center; gap: 12px; }
.dist-label { width: 56px; font-size: 13px; color: var(--c-text-secondary); flex-shrink: 0; }

.exam-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}
.detail-header-left {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.back-btn { margin-top: 2px; }
.detail-type-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.exam-type-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 999px;
}
.exam-type-badge.正式 { background: var(--c-danger-bg); color: var(--c-danger); }
.exam-type-badge.练习 { background: var(--c-success-bg); color: var(--c-success); }
.exam-type-badge.模拟 { background: var(--c-warning-bg); color: var(--c-warning); }
.detail-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--c-text);
}
.detail-header-right { display: flex; gap: 8px; flex-shrink: 0; }

/* Stats */
.detail-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}
.detail-stat-item {
  background: var(--c-surface);
  border-radius: var(--radius-md);
  padding: 16px 20px;
  border: 1px solid var(--c-border-light);
  text-align: center;
}
.detail-stat-value {
  display: block;
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--c-primary);
  margin-bottom: 4px;
}
.detail-stat-label {
  font-size: 12px;
  color: var(--c-text-tertiary);
}

.detail-card { border-radius: var(--radius-lg); }
.toolbar-inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.search-sm { width: 200px; }

.config-section { padding: 8px 0; }
.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.config-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.config-label {
  font-size: 12px;
  color: var(--c-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}
.config-value {
  font-size: 14px;
  color: var(--c-text);
  font-weight: 500;
}

.grade-form { }
.grade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--c-border-light);
  margin-bottom: 16px;
}
.grade-questions {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 500px;
  overflow-y: auto;
}
.grade-q-item {
  border: 1px solid var(--c-border-light);
  border-radius: var(--radius-sm);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.grade-q-item.grade-auto {
  border-left: 3px solid var(--c-success);
}
.grade-q-item.grade-manual {
  border-left: 3px solid var(--c-warning);
}
.grade-q-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.grade-q-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text);
}
.grade-q-score {
  font-size: 12px;
  color: var(--c-text-tertiary);
  margin-left: auto;
}
.grade-q-content {
  font-size: 14px;
  color: var(--c-text);
  line-height: 1.6;
}
.grade-answer, .grade-correct {
  font-size: 13px;
  padding: 6px 10px;
  border-radius: var(--radius-sm);
}
.grade-answer {
  background: var(--c-bg);
}
.grade-answer-label { font-weight: 600; color: var(--c-text-secondary); }
.grade-answer-text { color: var(--c-text); }
.grade-correct {
  background: var(--c-success-bg);
  border: 1px solid var(--c-success);
}
.grade-correct-label { font-weight: 600; color: var(--c-success); }
.grade-correct-text { color: var(--c-text); }
.grade-input {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--c-border-light);
}
.grade-input-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-warning);
}
</style>