<template>
  <div class="results-page">
    <!-- Header with stats -->
    <div class="results-header">
      <div class="results-header-text">
        <h2 class="results-title">成绩查询</h2>
        <p class="results-subtitle">查看所有考核的统计数据与考生成绩</p>
      </div>
      <div class="results-header-actions">
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" size="small" />
        <el-button :icon="Download" size="small">导出报告</el-button>
      </div>
    </div>

    <!-- Overview metrics -->
    <div class="metrics-scroll">
      <div class="metric-card metric-primary">
        <div class="metric-icon-wrap">
          <el-icon :size="24"><DataBoard /></el-icon>
        </div>
        <div class="metric-body">
          <span class="metric-value">18</span>
          <span class="metric-label">考核场次</span>
        </div>
        <div class="metric-trend up">
          <el-icon><Top /></el-icon> +23%
        </div>
      </div>
      <div class="metric-card metric-success">
        <div class="metric-icon-wrap">
          <el-icon :size="24"><CircleCheck /></el-icon>
        </div>
        <div class="metric-body">
          <span class="metric-value">87%</span>
          <span class="metric-label">整体通过率</span>
        </div>
        <div class="metric-trend up">
          <el-icon><Top /></el-icon> +5%
        </div>
      </div>
      <div class="metric-card metric-warning">
        <div class="metric-icon-wrap">
          <el-icon :size="24"><UserFilled /></el-icon>
        </div>
        <div class="metric-body">
          <span class="metric-value">346</span>
          <span class="metric-label">参考总人次</span>
        </div>
        <div class="metric-trend up">
          <el-icon><Top /></el-icon> +12%
        </div>
      </div>
      <div class="metric-card metric-danger">
        <div class="metric-icon-wrap">
          <el-icon :size="24"><WarningFilled /></el-icon>
        </div>
        <div class="metric-body">
          <span class="metric-value">24</span>
          <span class="metric-label">待批改试卷</span>
        </div>
        <div class="metric-trend down">
          <el-icon><Bottom /></el-icon> -8%
        </div>
      </div>
    </div>

    <!-- Results list -->
    <div class="results-list">
      <div
        v-for="(exam, i) in examResults"
        :key="exam.id"
        class="result-card"
        @click="$router.push(`/results/${exam.id}`)"
      >
        <!-- Left decorative stripe -->
        <div class="result-stripe" :style="{ background: exam.color }"></div>

        <div class="result-main">
          <div class="result-top">
            <div class="result-info">
              <span class="result-type" :class="exam.type">{{ exam.type }}</span>
              <h3 class="result-name">{{ exam.name }}</h3>
            </div>
            <!-- Score ring -->
            <div class="score-ring" :style="{ '--ring-color': exam.passRate >= 80 ? 'var(--c-success)' : exam.passRate >= 60 ? 'var(--c-warning)' : 'var(--c-danger)' }">
              <svg viewBox="0 0 60 60" class="ring-svg">
                <circle cx="30" cy="30" r="26" fill="none" stroke="var(--c-border-light)" stroke-width="5" />
                <circle
                  cx="30" cy="30" r="26"
                  fill="none"
                  :stroke="exam.passRate >= 80 ? 'var(--c-success)' : exam.passRate >= 60 ? 'var(--c-warning)' : 'var(--c-danger)'"
                  stroke-width="5"
                  stroke-linecap="round"
                  :stroke-dasharray="`${(exam.passRate / 100) * 163.36} 163.36`"
                  transform="rotate(-90 30 30)"
                  class="ring-fill"
                />
              </svg>
              <span class="ring-text">{{ exam.passRate }}%</span>
            </div>
          </div>

          <div class="result-stats">
            <div class="result-stat">
              <span class="rs-value">{{ exam.candidates }}</span>
              <span class="rs-label">参考</span>
            </div>
            <div class="result-stat">
              <span class="rs-value">{{ exam.passed }}</span>
              <span class="rs-label">通过</span>
            </div>
            <div class="result-stat">
              <span class="rs-value">{{ exam.avgScore }}</span>
              <span class="rs-label">均分</span>
            </div>
            <div class="result-stat">
              <span class="rs-value">{{ exam.topScore }}</span>
              <span class="rs-label">最高</span>
            </div>
          </div>

          <div class="result-footer">
            <span class="result-date">{{ exam.date }}</span>
            <div class="result-actions">
              <el-button text type="primary" size="small">查看详情</el-button>
              <el-button text size="small" :icon="Download" @click.stop />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { DataBoard, CircleCheck, UserFilled, WarningFilled, Download, Top, Bottom } from "@element-plus/icons-vue";
import { api } from "../api.js";

const dateRange = ref(null);
const examResults = ref([]);
const overview = ref({ exams_count: 0, total_candidates: 0, pass_rate: 0, pending: 0 });

onMounted(async () => {
  try {
    const [res, statsRes] = await Promise.all([
      api.results.list(),
      api.results.stats()
    ]);
    overview.value = statsRes;
    examResults.value = (res.items || []).map(r => ({
      id: r.paper_id, name: r.exam_name, type: r.exam_type || "正式",
      candidates: r.candidate || "-", passed: (r.score || 0) >= 60 ? 1 : 0,
      avgScore: r.score || 0, topScore: r.score || 0,
      passRate: (r.score || 0) >= 60 ? 85 : 40,
      date: r.submitted_at || "",
      color: (r.score || 0) >= 60 ? "linear-gradient(180deg, #10B981, #059669)" : "linear-gradient(180deg, #EF4444, #DC2626)"
    }));
  } catch(e) { console.error(e); }
});
</script>

<style scoped>
.results-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Header ── */
.results-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.results-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--c-text);
  margin-bottom: 4px;
}
.results-subtitle {
  font-size: 13px;
  color: var(--c-text-secondary);
  margin: 0;
}
.results-header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* ── Metrics Scroll ── */
.metrics-scroll {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.metric-card {
  background: var(--c-surface);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--c-border-light);
  position: relative;
  overflow: hidden;
  transition: all var(--transition-base);
}
.metric-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.metric-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.metric-primary .metric-icon-wrap { background: var(--c-primary-lighter); color: var(--c-primary); }
.metric-success .metric-icon-wrap { background: var(--c-success-bg); color: var(--c-success); }
.metric-warning .metric-icon-wrap { background: var(--c-warning-bg); color: var(--c-warning); }
.metric-danger .metric-icon-wrap { background: var(--c-danger-bg); color: var(--c-danger); }

.metric-body { flex: 1; }
.metric-value {
  display: block;
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text);
  line-height: 1.2;
}
.metric-label {
  font-size: 12px;
  color: var(--c-text-tertiary);
}
.metric-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  align-self: flex-start;
}
.metric-trend.up { color: var(--c-success); background: var(--c-success-bg); }
.metric-trend.down { color: var(--c-danger); background: var(--c-danger-bg); }

/* ── Results List ── */
.results-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px;
}
.result-card {
  background: var(--c-surface);
  border-radius: var(--radius-lg);
  display: flex;
  overflow: hidden;
  border: 1px solid var(--c-border-light);
  cursor: pointer;
  transition: all var(--transition-base);
}
.result-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}
.result-stripe {
  width: 5px;
  flex-shrink: 0;
}
.result-main {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.result-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}
.result-info {
  flex: 1;
}
.result-type {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 999px;
  margin-bottom: 6px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.result-type.正式 { background: var(--c-danger-bg); color: var(--c-danger); }
.result-type.练习 { background: var(--c-success-bg); color: var(--c-success); }
.result-type.模拟 { background: var(--c-warning-bg); color: var(--c-warning); }
.result-name {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text);
  line-height: 1.4;
}

/* Score Ring */
.score-ring {
  position: relative;
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}
.ring-svg { width: 100%; height: 100%; }
.ring-fill {
  transition: stroke-dasharray 1s ease;
}
.ring-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 700;
  color: var(--c-text);
}

/* Stats row */
.result-stats {
  display: flex;
  gap: 0;
  background: var(--c-bg);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.result-stat {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  border-right: 1px solid var(--c-border-light);
}
.result-stat:last-child { border-right: none; }
.rs-value {
  display: block;
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--c-text);
}
.rs-label {
  font-size: 11px;
  color: var(--c-text-tertiary);
}

.result-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid var(--c-border-light);
}
.result-date {
  font-size: 12px;
  color: var(--c-text-tertiary);
}
.result-actions {
  display: flex;
  gap: 4px;
}

@media (max-width: 768px) {
  .results-list {
    grid-template-columns: 1fr;
  }
}
</style>
