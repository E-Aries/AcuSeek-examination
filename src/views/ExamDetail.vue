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
        <el-button type="primary" :icon="Edit">编辑</el-button>
        <el-button type="primary" :icon="CaretRight" @click="$router.push('/exams/' + route.params.id + '/take')" style="--el-button-bg-color:var(--c-success);--el-button-border-color:var(--c-success);--el-button-hover-bg-color:#059669;--el-button-hover-border-color:#059669">开始考试</el-button>
        <el-button :icon="Share">分享</el-button>
      </div>
    </div>

    <!-- Stats -->
    <div class="detail-stats">
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ exam.duration }}</span>
        <span class="detail-stat-label">考试时长（分钟）</span>
      </div>
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ exam.questionCount }}</span>
        <span class="detail-stat-label">题目数量</span>
      </div>
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ exam.candidates }}</span>
        <span class="detail-stat-label">参考人数</span>
      </div>
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ passRate }}%</span>
        <span class="detail-stat-label">通过率</span>
      </div>
      <div class="detail-stat-item">
        <span class="detail-stat-value">{{ avgScore }}</span>
        <span class="detail-stat-label">平均分</span>
      </div>
    </div>

    <!-- Tabs: Candidates, Scores, Config -->
    <el-card shadow="never" class="detail-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="考生成绩" name="scores">
          <div class="toolbar-inline">
            <el-input v-model="candidateSearch" placeholder="搜索考生姓名..." clearable :prefix-icon="Search" class="search-sm" />
            <el-button text type="primary" :icon="Download">导出</el-button>
          </div>
          <el-table :data="candidates" stripe style="width:100%" class="detail-table">
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="department" label="部门" width="140" />
            <el-table-column label="成绩" width="90" align="right">
              <template #default="{ row }">
                <span :style="{ color: row.score >= 60 ? 'var(--c-success)' : 'var(--c-danger)', fontWeight: 600 }">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="结果" width="80">
              <template #default="{ row }">
                <el-tag :type="row.score >= 60 ? 'success' : 'danger'" size="small" effect="plain" round>{{ row.score >= 60 ? '通过' : '未通过' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="用时" width="80" align="right" />
            <el-table-column prop="date" label="提交时间" width="160" />
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" size="small" @click="$router.push(`/results/${row.id}`)">批阅</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="试卷配置" name="config">
          <div class="config-section">
            <div class="config-grid">
              <div class="config-item">
                <span class="config-label">组卷策略</span>
                <span class="config-value">随机组卷（按题型分布）</span>
              </div>
              <div class="config-item">
                <span class="config-label">及格线</span>
                <span class="config-value">60 分</span>
              </div>
              <div class="config-item">
                <span class="config-label">题目分类</span>
                <span class="config-value">售后流程、产品知识、故障处理</span>
              </div>
              <div class="config-item">
                <span class="config-label">允许查看成绩</span>
                <span class="config-value">提交后立即查看</span>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import { ArrowLeft, Edit, Share, Search, Download, CaretRight } from "@element-plus/icons-vue";

const route = useRoute();
const activeTab = ref("scores");
const candidateSearch = ref("");

const exam = ref({
  id: route.params.id,
  name: "售后流程季度考核 Q2",
  type: "正式",
  status: "进行中",
  duration: 60,
  questionCount: 50,
  candidates: 48,
});

const passRate = computed(() => "83");
const avgScore = computed(() => "76.5");

const allCandidates = ref([
  { id: 1, name: "张明", department: "售后一部", score: 88, duration: "52min", date: "2026-06-02 14:30" },
  { id: 2, name: "李华", department: "售后二部", score: 45, duration: "48min", date: "2026-06-02 15:15" },
  { id: 3, name: "王芳", department: "售后一部", score: 92, duration: "55min", date: "2026-06-02 10:00" },
  { id: 4, name: "赵强", department: "技术部", score: 73, duration: "60min", date: "2026-06-03 09:30" },
  { id: 5, name: "陈静", department: "售后二部", score: 68, duration: "58min", date: "2026-06-03 11:00" },
  { id: 6, name: "刘洋", department: "售后一部", score: 55, duration: "50min", date: "2026-06-03 13:45" },
]);

const candidates = computed(() => {
  if (!candidateSearch.value) return allCandidates.value;
  return allCandidates.value.filter((c) => c.name.includes(candidateSearch.value));
});
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

.config-section {
  padding: 8px 0;
}
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
</style>

