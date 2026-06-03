<template>
  <div class="exams-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="showCreate = true">新建考核</el-button>
      </div>
      <div class="toolbar-right">
        <el-select v-model="filterStatus" placeholder="状态" clearable size="small" style="width: 120px">
          <el-option label="进行中" value="进行中" />
          <el-option label="未开始" value="未开始" />
          <el-option label="已结束" value="已结束" />
        </el-select>
        <el-input v-model="search" placeholder="搜索考核名称..." clearable :prefix-icon="Search" class="search-input" />
      </div>
    </div>

    <!-- Exam Cards -->
    <div class="exam-grid">
      <div v-for="exam in filteredExams" :key="exam.id" class="exam-card">
        <div class="exam-card-header">
          <div class="exam-type" :class="exam.type">{{ exam.type }}</div>
          <el-tag v-if="exam.status === '进行中'" type="danger" size="small" effect="dark" round class="status-tag">进行中</el-tag>
          <el-tag v-else-if="exam.status === '未开始'" type="info" size="small" effect="plain" round class="status-tag">未开始</el-tag>
          <el-tag v-else size="small" effect="plain" round class="status-tag">已结束</el-tag>
        </div>
        <h3 class="exam-name">{{ exam.name }}</h3>
        <div class="exam-meta">
          <div class="exam-meta-item">
            <el-icon><Clock /></el-icon>
            <span>{{ exam.duration }} 分钟</span>
          </div>
          <div class="exam-meta-item">
            <el-icon><Document /></el-icon>
            <span>{{ exam.questionCount }} 题</span>
          </div>
          <div class="exam-meta-item">
            <el-icon><UserFilled /></el-icon>
            <span>{{ exam.candidates }} 人</span>
          </div>
        </div>
        <div class="exam-actions">
          <el-button text type="primary" size="small" @click="$router.push(`/exams/${exam.id}`)">
            管理 <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button
            v-if="exam.status !== '已结束'"
            type="primary"
            size="small"
            plain
            @click="$router.push(`/exams/${exam.id}/take`)"
          >
            <el-icon :size="14"><CaretRight /></el-icon> 开始考试
          </el-button>
        </div>
      </div>
    </div>

    <!-- Create Dialog ... (unchanged) -->
    <el-dialog v-model="showCreate" title="新建考核" width="600px" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="考核名称">
          <el-input v-model="createForm.name" placeholder="请输入考核名称" />
        </el-form-item>
        <el-form-item label="考核类型">
          <el-radio-group v-model="createForm.type">
            <el-radio value="正式">正式考核</el-radio>
            <el-radio value="练习">练习模式</el-radio>
            <el-radio value="模拟">模拟考试</el-radio>
          </el-radio-group>
        </el-form-item>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
          <el-form-item label="考试时长（分钟）">
            <el-input-number v-model="createForm.duration" :min="5" :max="180" :step="5" style="width:100%" />
          </el-form-item>
          <el-form-item label="题目数量">
            <el-input-number v-model="createForm.questionCount" :min="5" :max="100" style="width:100%" />
          </el-form-item>
        </div>
        <el-form-item label="组卷方式">
          <el-radio-group v-model="createForm.strategy">
            <el-radio value="random">随机组卷</el-radio>
            <el-radio value="manual">手动组卷</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="createForm.strategy === 'random'" label="题型分布">
          <div class="dist-config">
            <div v-for="(dist, key) in createForm.distribution" :key="key" class="dist-row">
              <span class="dist-label">{{ key }}</span>
              <el-slider v-model="dist.count" :min="0" :max="30" :marks="{ 0: '0', 10: '10', 20: '20', 30: '30' }" show-input size="small" />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="关联分类">
          <el-select v-model="createForm.categories" multiple placeholder="选择题目分类" style="width:100%">
            <el-option label="售后流程" value="售后流程" />
            <el-option label="产品知识" value="产品知识" />
            <el-option label="故障处理" value="故障处理" />
            <el-option label="服务规范" value="服务规范" />
          </el-select>
        </el-form-item>
        <el-form-item label="及格分数线">
          <el-input-number v-model="createForm.passScore" :min="0" :max="100" :step="5" style="width: 120px" />
          <span style="margin-left:8px;color:var(--c-text-secondary);font-size:13px">分</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建考核</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>

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

</script>>

<style scoped>
.exams-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
}
.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}
.search-input {
  width: 240px;
}

/* ── Exam Cards Grid ── */
.exam-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}
.exam-card {
  background: var(--c-surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--c-border-light);
  transition: all var(--transition-base);
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.exam-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
  border-color: var(--c-primary-lighter);
}

.exam-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.exam-type {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 999px;
  letter-spacing: 0.5px;
}
.exam-type.正式 { background: var(--c-danger-bg); color: var(--c-danger); }
.exam-type.练习 { background: var(--c-success-bg); color: var(--c-success); }
.exam-type.模拟 { background: var(--c-warning-bg); color: var(--c-warning); }

.exam-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
  line-height: 1.4;
}

.exam-meta {
  display: flex;
  gap: 20px;
}
.exam-meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: var(--c-text-secondary);
}
.exam-meta-item .el-icon {
  font-size: 15px;
  color: var(--c-text-tertiary);
}

.exam-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--c-border-light);
}

.dist-config {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}
.dist-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.dist-label {
  width: 56px;
  font-size: 13px;
  color: var(--c-text-secondary);
  flex-shrink: 0;
}
.dist-row :deep(.el-slider) {
  flex: 1;
}
</style>
