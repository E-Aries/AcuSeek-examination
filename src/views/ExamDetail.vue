<template>
  <div class="exam-detail">
    <!-- Header -->
    <div class="detail-header">
      <div class="detail-header-left">
        <el-button text :icon="ArrowLeft" @click="$router.push('/exams')" class="back-btn">返回</el-button>
        <div>
          <div class="detail-type-badge">
            <span class="exam-type-badge" :class="exam.type">{{ exam.type }}</span>
            <el-tag :type="exam.status === '进行中' ? 'danger' : exam.status === '未开始' ? 'info' : ''" size="small" effect="dark" round>{{ exam.status }}</el-tag>
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
            <el-table-column label="结果" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.status === '已完成'" :type="row.score >= (exam.pass_score || 60) ? 'success' : 'danger'" size="small" effect="plain" round>{{ row.score >= (exam.pass_score || 60) ? '通过' : '未通过' }}</el-tag>
                <el-tag v-else-if="row.status === '待批改'" type="warning" size="small" effect="plain" round>待批改</el-tag>
                <el-tag v-else type="info" size="small" effect="plain" round>进行中</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="用时" width="80" align="right">
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
                  <el-tag :type="exam.status === '进行中' ? 'danger' : exam.status === '未开始' ? 'info' : ''" size="small" effect="dark" round>{{ exam.status }}</el-tag>
                </span>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Grade Dialog -->
    <el-dialog v-model="showGradeDialog" title="批改试卷" width="420px">
      <div class="grade-form">
        <p style="margin-bottom:16px;color:var(--c-text-secondary);font-size:14px">
          考生：<strong>{{ gradingPaper.name }}</strong>
        </p>
        <el-form label-position="top">
          <el-form-item label="主观题得分">
            <el-input-number v-model="gradeScore" :min="0" :max="100" :step="1" style="width:160px" />
            <span style="margin-left:8px;color:var(--c-text-tertiary);font-size:13px">分</span>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showGradeDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmGrade">确认批改</el-button>
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
            <el-input-number v-model="editForm.questionCount" :min="5" :max="100" style="width:100%" />
          </el-form-item>
        </div>
        <el-form-item label="组卷方式">
          <el-radio-group v-model="editForm.strategy">
            <el-radio value="random">随机组卷</el-radio>
            <el-radio value="manual">手动组卷</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="及格分数线">
          <el-input-number v-model="editForm.passScore" :min="0" :max="100" :step="5" style="width:120px" />
          <span style="margin-left:8px;color:var(--c-text-secondary);font-size:13px">分</span>
        </el-form-item>
        <el-form-item label="关联分类">
          <el-select v-model="editForm.categories" multiple placeholder="选择分类" style="width:100%">
            <el-option label="售后流程" value="售后流程" />
            <el-option label="产品知识" value="产品知识" />
            <el-option label="故障处理" value="故障处理" />
            <el-option label="服务规范" value="服务规范" />
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
const editForm = reactive({ name: "", type: "正式", duration: 60, questionCount: 30, passScore: 60, strategy: "random", categories: [] });

const gradingPaper = ref({});
const gradeScore = ref(0);

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
      score: p.score, status: p.status,
      duration_used: p.duration_used, submitted_at: p.submitted_at
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

function openGradeDialog(row) {
  gradingPaper.value = row;
  gradeScore.value = row.score || Math.round((exam.value.pass_score || 60) * 0.7);
  showGradeDialog.value = true;
}

async function confirmGrade() {
  try {
    await api.answers.grade(gradingPaper.value.paper_id, { score: gradeScore.value });
    ElMessage.success("批改完成");
    showGradeDialog.value = false;
    // Refresh
    const papersRes = await api.exams.papers(route.params.id);
    allCandidates.value = (papersRes.items || []).map(p => ({
      paper_id: p.paper_id, name: p.name, department: p.department || "",
      score: p.score, status: p.status,
      duration_used: p.duration_used, submitted_at: p.submitted_at
    }));
  } catch(e) { ElMessage.error("批改失败"); }
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

function openEditDialog() {
  editForm.name = exam.value.name
  editForm.type = exam.value.type
  editForm.duration = exam.value.duration
  editForm.questionCount = exam.value.question_count
  editForm.passScore = exam.value.pass_score
  editForm.strategy = exam.value.strategy
  editForm.categories = exam.value.categories || []
  showEditDialog.value = true
}

async function saveEdit() {
  try {
    await api.exams.update(route.params.id, {
      name: editForm.name, type: editForm.type, duration: editForm.duration,
      question_count: editForm.questionCount, pass_score: editForm.passScore,
      strategy: editForm.strategy, categories: editForm.categories
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

.grade-form { padding: 8px 0; }
</style>