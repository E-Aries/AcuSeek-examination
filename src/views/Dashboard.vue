<!-- Author: 达咩 | 轻则 -->

<template>
  <div class="dashboard">
    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div v-for="stat in stats" :key="stat.label" class="stat-card" :style="{ '--card-accent': stat.color }">
        <div class="stat-icon" :style="{ background: stat.bg }">
          <el-icon :size="22"><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
        <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
          <el-icon><Top v-if="stat.trend > 0" /><Bottom v-else /></el-icon>
          <span>{{ Math.abs(stat.trend) }}%</span>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">月度考试统计</h3>
          <el-tag size="small" effect="plain" round>本年</el-tag>
        </div>
        <div class="chart-body">
          <v-chart :option="examChartOption" autoresize class="chart" />
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">各分类题目分布</h3>
          <el-tag size="small" effect="plain" round>整体</el-tag>
        </div>
        <div class="chart-body">
          <v-chart :option="passChartOption" autoresize class="chart" />
        </div>
      </div>
    </div>

    <!-- Recent Exams & Activity -->
    <div class="activity-grid">
      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">近期考核</h3>
          <el-button text type="primary" @click="$router.push('/exams')">查看全部</el-button>
        </div>
        <el-table :data="recentExams" style="width: 100%" stripe>
          <el-table-column prop="name" label="考核名称" min-width="160" />
          <el-table-column prop="type" label="类型" width="90">
            <template #default="{ row }">
              <el-tag :type="row.type === '正式' ? 'danger' : row.type === '练习' ? 'success' : 'warning'" size="small" effect="plain">
                {{ row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="candidates" label="参考人数" width="90" align="right" />
          <el-table-column prop="avgScore" label="均分" width="80" align="right">
            <template #default="{ row }">
              <span :style="{ color: row.avgScore >= 80 ? 'var(--c-success)' : row.avgScore >= 60 ? 'var(--c-warning)' : 'var(--c-danger)', fontWeight: 600 }">{{ row.avgScore }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="日期" width="100" />
          <el-table-column label="操作" width="60" fixed="right">
            <template #default>
              <el-button text type="primary" size="small" @click="$router.push('/exams/' + (row.id || ''))">管理</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">待办提醒</h3>
        </div>
        <div class="todo-list">
          <div v-for="(item, i) in todos" :key="i" class="todo-item" :class="{ urgent: item.urgent }">
            <div class="todo-dot" :class="{ urgent: item.urgent }"></div>
            <div class="todo-content">
              <span class="todo-text">{{ item.text }}</span>
              <span class="todo-meta">{{ item.meta }}</span>
            </div>
            <el-tag v-if="item.urgent" size="small" type="danger" effect="dark" round>紧急</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import VChart from "vue-echarts";
import "echarts";
import { api } from "../api.js";

const stats = ref([]);
const recentExams = ref([]);
const todos = ref([]);
const monthlyData = ref([]);
const categoryData = ref([]);

onMounted(async () => {
  try {
    const [dash, qStats, rStats] = await Promise.all([
      api.dashboard.get(),
      api.questions.stats(),
      api.results.stats()
    ]);
    const totalQs = dash.total_questions || (qStats.items || []).reduce((s, i) => s + i.count, 0);
    stats.value = [
      { label: "题库总数", value: String(totalQs), icon: "Notebook", color: "var(--c-primary)", bg: "var(--c-primary-lighter)", trend: 0 },
      { label: "考核场次", value: String(dash.total_exams || 0), icon: "EditPen", color: "var(--c-accent)", bg: "var(--c-accent-bg)", trend: 0 },
      { label: "参考人次", value: String(dash.total_candidates || 0), icon: "UserFilled", color: "var(--c-info)", bg: "var(--c-info-bg)", trend: 0 },
      { label: "平均通过率", value: (rStats.pass_rate || 0) + "%", icon: "CircleCheck", color: "var(--c-success)", bg: "var(--c-success-bg)", trend: 0 },
    ];
    monthlyData.value = dash.monthly_stats || [];
    categoryData.value = dash.category_questions || [];
    recentExams.value = (dash.recent_exams || []).map(e => ({
      name: e.name, type: e.type,
      candidates: e.candidates, avgScore: e.avg_score,
      date: e.status, id: e.id
    }));
    todos.value = [
      { text: "待批改试卷 " + (dash.pending || 0) + " 份", meta: "需手动评分", urgent: (dash.pending || 0) > 0 },
      { text: "确认本月考核安排", meta: "建议提前一周准备", urgent: false },
    ];
  } catch(e) { console.error(e); }
});

const monthLabels = computed(() => monthlyData.value.map(d => {
  const parts = d.month.split("-");
  return parts[1] + "月";
}));
const monthCounts = computed(() => monthlyData.value.map(d => d.count));

const examChartOption = computed(() => ({
  grid: { left: 40, right: 16, top: 20, bottom: 24 },
  xAxis: { type: "category", data: monthLabels.value, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: "#9CA3AF", fontSize: 11 } },
  yAxis: { type: "value", splitLine: { lineStyle: { color: "#F0EFEC" } }, axisLabel: { color: "#9CA3AF", fontSize: 11 } },
  series: [{ type: "bar", data: monthCounts.value, barWidth: 28, borderRadius: [4,4,0,0], itemStyle: { color: "var(--c-primary)" } }],
  tooltip: { trigger: "axis" },
}));

const passChartOption = computed(() => {
  const names = categoryData.value.map(d => d.name);
  const counts = categoryData.value.map(d => d.count);
  return {
    grid: { left: 50, right: 30, top: 20, bottom: 24 },
    xAxis: { type: "category", data: names, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: "#9CA3AF", fontSize: 11 } },
    yAxis: { type: "value", splitLine: { lineStyle: { color: "#F0EFEC" } }, axisLabel: { color: "#9CA3AF", fontSize: 11 } },
    series: [{
      type: "bar", data: counts.map((v, i) => ({
        value: v, itemStyle: { color: (categoryData.value[i] && categoryData.value[i].color) || "var(--c-primary)" }
      })),
      barWidth: 24, borderRadius: [4,4,0,0],
      label: { show: true, position: "top", formatter: "{c}题", color: "#6B7280", fontSize: 11, fontWeight: 600 }
    }],
    tooltip: { trigger: "axis", formatter: (p) => p[0].name + "<br/>题目数：" + p[0].value + " 题" },
  };
});
</script>>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Stats Cards ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.stat-card {
  background: var(--c-surface);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--c-border-light);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}
.stat-card::after {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  width: 3px;
  height: 100%;
  background: var(--card-accent);
  border-radius: 0 2px 2px 0;
}
.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--card-accent);
  flex-shrink: 0;
}
.stat-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.stat-value {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--c-text);
  line-height: 1.2;
}
.stat-label {
  font-size: 13px;
  color: var(--c-text-secondary);
  margin-top: 2px;
}
.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 999px;
  align-self: flex-start;
}
.stat-trend.up {
  color: var(--c-success);
  background: var(--c-success-bg);
}
.stat-trend.down {
  color: var(--c-danger);
  background: var(--c-danger-bg);
}

/* ── Charts ── */
.charts-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 16px;
}
.chart-card {
  background: var(--c-surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--c-border-light);
}
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.chart-title {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text);
}
.chart-body {
  height: 260px;
}
.chart {
  width: 100%;
  height: 100%;
}

/* ── Activity Section ── */
.activity-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 16px;
}
.section-card {
  background: var(--c-surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--c-border-light);
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.section-title {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text);
}

/* ── Todo List ── */
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.todo-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}
.todo-item:hover {
  background: var(--c-surface-hover);
}
.todo-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--c-text-tertiary);
  margin-top: 6px;
  flex-shrink: 0;
}
.todo-dot.urgent {
  background: var(--c-danger);
  box-shadow: 0 0 0 3px var(--c-danger-bg);
}
.todo-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.todo-text {
  font-size: 13px;
  font-weight: 500;
  color: var(--c-text);
}
.todo-meta {
  font-size: 12px;
  color: var(--c-text-tertiary);
  margin-top: 2px;
}

@media (max-width: 1024px) {
  .charts-grid,
  .activity-grid {
    grid-template-columns: 1fr;
  }
}
</style>
