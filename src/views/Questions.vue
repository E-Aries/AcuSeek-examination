<template>
  <div class="questions-page">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="showDialog = true">新增题目</el-button>
        <el-button :icon="Upload" @click="handleImport">批量导入</el-button>
        <el-button :icon="Download" @click="handleExport">导出模板</el-button>
      </div>
      <div class="toolbar-right">
        <el-input v-model="search" placeholder="搜索题目内容..." clearable :prefix-icon="Search" class="search-input" />
      </div>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <el-radio-group v-model="filterType" size="small">
        <el-radio-button value="">全部题型</el-radio-button>
        <el-radio-button value="单选">单选题</el-radio-button>
        <el-radio-button value="多选">多选题</el-radio-button>
        <el-radio-button value="判断">判断题</el-radio-button>
        <el-radio-button value="填空">填空题</el-radio-button>
        <el-radio-button value="简答">简答题</el-radio-button>
      </el-radio-group>
      <el-select v-model="filterCategory" placeholder="分类" clearable size="small" style="width: 140px">
        <el-option label="售后流程" value="售后流程" />
        <el-option label="产品知识" value="产品知识" />
        <el-option label="故障处理" value="故障处理" />
        <el-option label="服务规范" value="服务规范" />
      </el-select>
    </div>

    <!-- Table -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredQuestions" stripe style="width: 100%" @row-click="handleRowClick">
        <el-table-column label="题目" min-width="320">
          <template #default="{ row }">
            <div class="question-cell">
              <el-tag :type="typeTag(row.type)" size="small" effect="plain" class="q-type">{{ row.type }}</el-tag>
              <span class="q-text">{{ row.content }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="难度" width="80">
          <template #default="{ row }">
            <el-rate v-model="row.difficulty" :max="3" disabled :colors="['var(--c-success)', 'var(--c-warning)', 'var(--c-danger)']" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="使用次数" width="80" align="right" prop="used" />
        <el-table-column label="最近使用" width="90" prop="lastUsed" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default>
            <el-button text type="primary" size="small">编辑</el-button>
            <el-button text type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="15"
          :total="filteredQuestions.length"
          layout="total, prev, pager, next"
          background
          small
        />
      </div>
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="showDialog" title="新增题目" width="600px" :close-on-click-modal="false">
      <el-form :model="newQuestion" label-width="80px" label-position="top">
        <el-form-item label="题型">
          <el-radio-group v-model="newQuestion.type">
            <el-radio value="单选">单选题</el-radio>
            <el-radio value="多选">多选题</el-radio>
            <el-radio value="判断">判断题</el-radio>
            <el-radio value="填空">填空题</el-radio>
            <el-radio value="简答">简答题</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="newQuestion.category" placeholder="选择分类" style="width: 100%">
            <el-option label="售后流程" value="售后流程" />
            <el-option label="产品知识" value="产品知识" />
            <el-option label="故障处理" value="故障处理" />
            <el-option label="服务规范" value="服务规范" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目内容">
          <el-input v-model="newQuestion.content" type="textarea" :rows="3" placeholder="请输入题目内容" />
        </el-form-item>
        <el-form-item v-if="['单选','多选','判断'].includes(newQuestion.type)" label="选项">
          <div class="options-list">
            <div v-for="(opt, i) in newQuestion.options" :key="i" class="option-row">
              <el-tag :type="opt.correct ? 'success' : 'info'" size="small" style="cursor:pointer" @click="opt.correct = !opt.correct">
                {{ opt.correct ? '正确' : '错误' }}
              </el-tag>
              <el-input v-model="opt.label" size="small" :placeholder="`选项 ${String.fromCharCode(65 + i)}`" style="width: 80px" />
              <el-input v-model="opt.text" size="small" placeholder="选项内容" />
              <el-button v-if="newQuestion.options.length > 2" :icon="Delete" text size="small" @click="newQuestion.options.splice(i, 1)" />
            </div>
          </div>
          <el-button size="small" text type="primary" @click="newQuestion.options.push({ label: '', text: '', correct: false })">+ 添加选项</el-button>
        </el-form-item>
        <el-form-item label="难度">
          <el-rate v-model="newQuestion.difficulty" :max="3" :colors="['var(--c-success)', 'var(--c-warning)', 'var(--c-danger)']" show-text />
        </el-form-item>
        <el-form-item label="解析">
          <el-input v-model="newQuestion.explanation" type="textarea" :rows="2" placeholder="答案解析（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="showDialog = false">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>

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

</script>>

<style scoped>
.questions-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.toolbar-left {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.toolbar-right {
  display: flex;
}
.search-input {
  width: 260px;
}
.search-input :deep(.el-input__wrapper) {
  border-radius: var(--radius-sm);
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-card {
  border-radius: var(--radius-lg);
}
.question-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
.q-type {
  flex-shrink: 0;
  min-width: 48px;
  text-align: center;
}
.q-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.option-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
