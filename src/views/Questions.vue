<template>
  <div class="questions-page">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="showDialog = true; editingId = null">新增题目</el-button>
        <el-button :icon="Upload" @click="handleImport">批量导入</el-button>
        <el-button :icon="Download" @click="handleExport">导出模板</el-button>
      </div>
      <div class="toolbar-right">
        <el-select v-model="filterType" placeholder="题型" clearable size="small" style="width:100px">
          <el-option label="单选" value="单选" />
          <el-option label="多选" value="多选" />
          <el-option label="判断" value="判断" />
          <el-option label="填空" value="填空" />
          <el-option label="简答" value="简答" />
        </el-select>
        <el-select v-model="filterCategory" placeholder="分类" clearable size="small" style="width:120px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.name" />
        </el-select>
        <el-input v-model="search" placeholder="搜索题目..." clearable :prefix-icon="Search" class="search-input" />
      </div>
    </div>

    <!-- Batch action bar -->
    <div v-if="multipleSelection.length > 0" class="batch-bar">
      <span class="batch-info">已选择 {{ multipleSelection.length }} 项</span>
      <el-button type="danger" size="small" :icon="Delete" @click="handleBatchDelete">批量删除</el-button>
      <el-button size="small" :icon="Download" @click="handleBatchExport">导出CSV</el-button>
      <el-button size="small" @click="showCategoryDialog = true">改分类</el-button>
      <el-button size="small" @click="clearSelection">取消选择</el-button>
    </div>

    <!-- Table -->
    <el-table :data="filteredQuestions" stripe style="width: 100%" ref="dataTable" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="36" />
      <el-table-column label="题型" prop="type" width="60" />
      <el-table-column label="分类" prop="category" width="80" />
      <el-table-column label="题目" min-width="180" show-overflow-tooltip>
        <template #default="scope">
          <span class="q-title-link" @click.stop="previewQuestion(scope.row)" title="点击预览题目">
            {{ scope.row.content }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="难度" prop="difficulty" width="80" align="center">
        <template #default="scope">
          <el-rate v-model="scope.row.difficulty" disabled :max="3" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="分值" prop="score" width="55" align="center" />
      <el-table-column label="操作" width="80" align="center">
        <template #default="scope">
          <span class="action-group">
            <el-button text size="small" :icon="Edit" @click="editQuestion(scope.row)" title="编辑" />
            <el-button text type="danger" size="small" :icon="Delete" @click="confirmDelete(scope.row.id)" title="删除" />
          </span>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="20"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadQuestions"
      />
    </div>

    <!-- Create / Edit Dialog -->
    <el-dialog v-model="showDialog" :title="editingId ? '编辑题目' : '新增题目'" width="700px" :close-on-click-modal="false">
      <el-form label-position="top">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
          <el-form-item label="题型">
            <el-select v-model="form.type">
              <el-option label="单选" value="单选" />
              <el-option label="多选" value="多选" />
              <el-option label="判断" value="判断" />
              <el-option label="填空" value="填空" />
              <el-option label="简答" value="简答" />
            </el-select>
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="form.category" allow-create filterable placeholder="选择或新建分类">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.name" />
            </el-select>
          </el-form-item>
          <el-form-item label="分值">
            <el-input-number v-model="form.score" :min="1" :max="100" style="width:100%" />
          </el-form-item>
        </div>
        <el-form-item label="题目内容">
          <el-input v-model="form.content" type="textarea" :rows="3" placeholder="请输入题目内容" />
        </el-form-item>
        <div v-if="form.type === '单选' || form.type === '多选'" class="options-group">
          <div class="options-header">
            <span class="options-title">选项</span>
            <el-button size="small" :icon="Plus" @click="addOption">添加选项</el-button>
          </div>
          <div v-for="(opt, i) in form.options" :key="i" class="option-row">
            <span class="option-label">{{ labels[i] }}</span>
            <el-input v-model="opt.text" placeholder="选项内容" />
            <el-button text type="danger" size="small" :icon="Delete" @click="form.options.splice(i, 1)" />
          </div>
          <div v-if="form.type === '单选'" class="answer-row">
            <span class="option-label">答案</span>
            <el-radio-group v-model="form.answer">
              <el-radio v-for="(opt, i) in form.options" :key="i" :value="labels[i]">{{ labels[i] }}</el-radio>
            </el-radio-group>
          </div>
          <div v-else class="answer-row">
            <span class="option-label">答案</span>
            <el-checkbox-group v-model="multiAnswer">
              <el-checkbox v-for="(opt, i) in form.options" :key="i" :label="labels[i]" :value="labels[i]">{{ labels[i] }}</el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
        <el-form-item v-if="form.type === '判断'" label="答案">
          <el-radio-group v-model="form.answer">
            <el-radio value="正确">正确</el-radio>
            <el-radio value="错误">错误</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.type === '填空'" label="答案">
          <el-input v-model="form.answer" placeholder="填空答案" />
        </el-form-item>
        <el-form-item label="解析">
          <el-input v-model="form.explanation" type="textarea" :rows="2" placeholder="答案解析（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- Batch category dialog -->
    <el-dialog v-model="showCategoryDialog" title="批量修改分类" width="400px">
      <el-select v-model="batchCategory" placeholder="选择分类" style="width:100%">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.name" />
      </el-select>
      <template #footer>
        <el-button @click="showCategoryDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchUpdateCategory">确认</el-button>
      </template>
    </el-dialog>

    <!-- Preview Dialog -->
    <el-dialog v-model="showPreview" title="题目预览" width="600px" :close-on-click-modal="false">
      <div v-if="previewData" class="preview-wrap">
        <div class="preview-meta">
          <el-tag size="small">{{ previewData.type }}</el-tag>
          <el-tag size="small" type="info">{{ previewData.category }}</el-tag>
          <el-tag size="small">{{ previewData.score }}分</el-tag>
        </div>
        <div class="preview-content">{{ previewData.content }}</div>
        <div v-if="previewData.options && previewData.options.length" class="preview-options">
          <div v-for="opt in previewData.options" :key="opt.label" class="preview-option" :class="{ correct: isCorrectAnswer(opt.label) }">
            <span class="po-label">{{ opt.label }}.</span>
            <span class="po-text">{{ opt.text }}</span>
            <el-icon v-if="isCorrectAnswer(opt.label)" style="color:var(--c-success)"><CircleCheck /></el-icon>
          </div>
        </div>
        <div v-if="previewData.answer" class="preview-answer">
          <span class="preview-answer-label">答案：</span>
          <span class="preview-answer-text">{{ previewAnswer }}</span>
        </div>
        <div v-if="previewData.explanation" class="preview-explanation">
          <span class="preview-explanation-label">解析：</span>
          <p class="preview-explanation-text">{{ previewData.explanation }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { Plus, Upload, Download, Search, Delete, Edit, View , InfoFilled, CircleCheck } from "@element-plus/icons-vue";
import { api } from "../api.js";
import { ElMessage, ElMessageBox } from "element-plus";

const search = ref("");
const filterType = ref("");
const filterCategory = ref("");
const currentPage = ref(1);
const total = ref(0);
const showDialog = ref(false);
const questions = ref([]);
const categories = ref([]);
const editingId = ref(null);
const multipleSelection = ref([]);
const showCategoryDialog = ref(false);
const batchCategory = ref("");
const showPreview = ref(false);
const previewData = ref(null);
const labels = ["A","B","C","D","E","F","G","H"];

const form = ref({ type:"单选", category:"", content:"", options:[{text:""},{text:""}], answer:"", explanation:"", score:2, difficulty:1 });
const multiAnswer = ref([]);

watch(() => form.value.type, (t) => {
  if (t === "单选" || t === "多选") {
    if (form.value.options.length < 2) form.value.options = [{text:""},{text:""}];
  }
  if (t !== "多选") multiAnswer.value = [];
});

watch(multiAnswer, (val) => {
  if (form.value.type === "多选") form.value.answer = JSON.stringify(val);
});

onMounted(async () => {
  try {
    const [qRes, catRes] = await Promise.all([api.questions.list({size:100}), api.categories.list()]);
    questions.value = (qRes.items || []);
    total.value = qRes.total || 0;
    categories.value = (catRes.items || []);
  } catch(e) { console.error(e); }
});

const filteredQuestions = computed(() => {
  let list = questions.value;
  if (filterType.value) list = list.filter(q => q.type === filterType.value);
  if (filterCategory.value) list = list.filter(q => q.category === filterCategory.value);
  if (search.value) list = list.filter(q => q.content.includes(search.value));
  return list;
});

function addOption() {
  if (form.value.options.length < 8) form.value.options.push({text:""});
}

function editQuestion(row) {
  editingId.value = row.id;
  form.value = {
    type: row.type || "单选",
    category: row.category || "",
    content: row.content || "",
    options: JSON.parse(JSON.stringify(row.options || [{text:""},{text:""}])),
    answer: row.answer || "",
    explanation: row.explanation || "",
    score: row.score || 2,
    difficulty: row.difficulty || 1,
  };
  if (row.type === "多选") {
    try { multiAnswer.value = JSON.parse(row.answer); } catch(e) { multiAnswer.value = []; }
  }
  showDialog.value = true;
}

async function handleSave() {
  try {
    if (editingId.value) {
      await api.questions.update(editingId.value, form.value);
      ElMessage.success("更新成功");
    } else {
      await api.questions.create(form.value);
      ElMessage.success("创建成功");
    }
    showDialog.value = false;
    const qRes = await api.questions.list({size:100});
    questions.value = (qRes.items || []);
  } catch(e) { ElMessage.error("保存失败"); }
}

async function confirmDelete(id) {
  try {
    await ElMessageBox.confirm("确定删除该题目？", "确认删除");
    await handleDelete(id);
  } catch(e) {}
}
async function handleDelete(id) {
  try { await api.questions.delete(id); ElMessage.success("删除成功"); questions.value = questions.value.filter(q => q.id !== id); } catch(e) { ElMessage.error("删除失败"); }
}

function handleSelectionChange(val) {
  multipleSelection.value = val;
}

function clearSelection() {
  multipleSelection.value = [];
}

async function handleBatchDelete() {
  if (multipleSelection.value.length === 0) return;
  try {
    await ElMessageBox.confirm("确定删除选中的 " + multipleSelection.value.length + " 道题？", "确认删除");
    const ids = multipleSelection.value.map(q => q.id);
    await api.questions.batchDelete(ids);
    ElMessage.success("删除成功");
    multipleSelection.value = [];
    const qRes = await api.questions.list({size:100});
    questions.value = (qRes.items || []);
  } catch(e) { if (e !== "cancel") ElMessage.error("删除失败"); }
}

async function handleBatchExport() {
  if (multipleSelection.value.length === 0) return;
  try {
    const ids = multipleSelection.value.map(q => q.id);
    const resp = await api.questions.batchExport(ids);
    const blob = await resp.blob();
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "选中题目.csv"; a.click();
  } catch(e) { ElMessage.error("导出失败"); }
}

async function handleBatchUpdateCategory() {
  if (multipleSelection.value.length === 0 || !batchCategory.value) return;
  try {
    const ids = multipleSelection.value.map(q => q.id);
    await api.questions.batchCategory(ids, batchCategory.value);
    ElMessage.success("更新成功");
    batchCategory.value = "";
    multipleSelection.value = [];
    showCategoryDialog.value = false;
    const qRes = await api.questions.list({size:100});
    questions.value = (qRes.items || []);
  } catch(e) { ElMessage.error("更新失败"); }
}

function handleImport() {
  ElMessage.info("请下载模板按格式填写：题型、分类、题目内容、选项A-D、答案、解析、分值、难度");
  const input = document.createElement("input");
  input.type = "file"; input.accept = ".xlsx,.csv";
  input.onchange = async (ev) => {
    const file = ev.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/api/questions/import", { method: "POST", headers: { "Authorization": "Bearer " + localStorage.getItem("token") }, body: formData });
      const data = await res.json();
      ElMessage.success(data.message);
      const qRes = await api.questions.list({size:100});
      questions.value = (qRes.items || []);
    } catch(e) { ElMessage.error("导入失败"); }
  };
  input.click();
}

function handleExport() {
  const cols = ["题型","分类","题目内容","选项A","选项B","选项C","选项D","答案","解析","分值","难度"];
  const csv = [cols.join(",")];
  const samples = [
    { type:"单选", category:"产品知识", content:"XX 产品的标准保修期限是?", optA:"1年", optB:"2年", optC:"3年", optD:"5年", answer:"A", explanation:"标准保修1年", score:2, difficulty:1 },
    { type:"多选", category:"产品知识", content:"以下哪些属于核心功能?", optA:"用户管理", optB:"权限控制", optC:"数据报表", optD:"邮件发送", answer:"A,B", explanation:"用户管理和权限控制是核心功能", score:3, difficulty:2 },
    { type:"判断", category:"故障处理", content:"设备红灯闪烁表示正常运行.", optA:"正确", optB:"错误", answer:"错误", explanation:"红灯闪烁表示故障", score:1, difficulty:1 },
    { type:"填空", category:"售后流程", content:"客户投诉应在 ____ 小时内响应.", answer:"24", explanation:"SLA要求24小时内响应", score:2, difficulty:1 },
    { type:"简答", category:"故障处理", content:"简述设备无法开机的排查步骤.", answer:"", explanation:"检查电源、开关、保险丝等", score:5, difficulty:3 },
  ];
  function esc(v) {
    const q = String.fromCharCode(34); // double quote
    const s = String(v || "");
    if (s.indexOf(q) >= 0 || s.indexOf(String.fromCharCode(44)) >= 0) {
      return q + s.split(q).join(q + q) + q;
    }
    return s;
  }

  samples.forEach(s => {
    const row = [esc(s.type), esc(s.category), esc(s.content), esc(s.optA), esc(s.optB), esc(s.optC), esc(s.optD), esc(s.answer), esc(s.explanation), esc(s.score), esc(s.difficulty)];
    csv.push(row.join(","));
  });
  const blob = new Blob(["\ufeff" + csv.join("\n")], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "题库模板.csv"; a.click();
}


function previewQuestion(row) {
  previewData.value = { ...row };
  showPreview.value = true;
}

const previewAnswer = computed(() => {
  if (!previewData.value) return "";
  const d = previewData.value;
  if (d.type === "多选") {
    try {
      const arr = JSON.parse(d.answer);
      return Array.isArray(arr) ? arr.join(", ") : d.answer;
    } catch(e) { return d.answer; }
  }
  return d.answer || "";
});

function isCorrectAnswer(label) {
  if (!previewData.value) return false;
  const d = previewData.value;
  if (d.type === "多选") {
    try {
      const arr = JSON.parse(d.answer);
      return Array.isArray(arr) && arr.includes(label);
    } catch(e) { return false; }
  }
  return d.answer === label;
}

async function loadQuestions() {}
</script>

<style scoped>
.questions-page { min-width: 0; display: flex; flex-direction: column; gap: 16px; }

.toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.toolbar-right { display: flex; gap: 8px; align-items: center; }
.search-input { width: 220px; }

.batch-bar { display: flex; align-items: center; gap: 10px; padding: 10px 16px; background: var(--c-primary-lighter); border-radius: var(--radius-md); }
.batch-info { font-size: 13px; font-weight: 600; color: var(--c-primary); }

.pagination-wrap { display: flex; justify-content: center; }

.options-group { border: 1px solid var(--c-border); border-radius: var(--radius-md); padding: 16px; margin-bottom: 18px; }
.options-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.options-title { font-weight: 600; font-size: 14px; }
.option-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.option-label { width: 24px; font-weight: 700; color: var(--c-primary); text-align: center; flex-shrink: 0; }
.answer-row { display: flex; align-items: center; gap: 10px; margin-top: 8px; padding-top: 12px; border-top: 1px dashed var(--c-border-light); }

.preview-wrap { display: flex; flex-direction: column; gap: 14px; }
.preview-meta { display: flex; gap: 8px; }
.preview-content { font-size: 16px; line-height: 1.6; padding: 12px 0; }
.preview-options { display: flex; flex-direction: column; gap: 8px; }
.preview-option { display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: var(--radius-sm); background: var(--c-bg); }
.preview-option.correct { background: var(--c-success-bg); border: 1px solid var(--c-success-lighter); }
.po-label { font-weight: 700; color: var(--c-text-secondary); }
.preview-answer-label, .preview-explanation-label { font-weight: 600; color: var(--c-text-secondary); }
.preview-answer-text { color: var(--c-success); font-weight: 600; }
.preview-explanation-text { font-size: 13px; color: var(--c-text-secondary); line-height: 1.5; }
.action-group {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.action-group .el-button {
  margin-left: 0 !important;
}
</style>
