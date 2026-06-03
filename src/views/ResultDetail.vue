<template>
  <div class="result-detail">
    <!-- Back navigation -->
    <div class="detail-nav">
      <el-button text :icon="ArrowLeft" @click="$router.push('/results')" class="back-btn">
        <span>返回成绩列表</span>
      </el-button>
    </div>

    <!-- Hero Score Section -->
    <div class="score-hero" :class="{ passed: result.passed, failed: !result.passed }">
      <div class="score-hero-bg"></div>
      <div class="score-hero-content">
        <div class="score-display">
          <div class="score-ring-large">
            <svg viewBox="0 0 140 140" class="ring-large-svg">
              <defs>
                <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" :stop-color="result.passed ? 'var(--c-success)' : 'var(--c-danger)'" />
                  <stop offset="100%" :stop-color="result.passed ? '#34D399' : '#F87171'" />
                </linearGradient>
              </defs>
              <circle cx="70" cy="70" r="60" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="8" />
              <circle
                cx="70" cy="70" r="60"
                fill="none"
                stroke="url(#scoreGrad)"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="`${(result.score / 100) * 376.99} 376.99`"
                transform="rotate(-90 70 70)"
                class="ring-large-fill"
              />
            </svg>
            <div class="ring-large-text">
              <span class="ring-large-score">{{ result.score }}</span>
              <span class="ring-large-unit">分</span>
            </div>
          </div>
        </div>
        <div class="score-info">
          <div class="score-badge" :class="result.passed ? 'badge-pass' : 'badge-fail'">
            <el-icon :size="18"><CircleCheck v-if="result.passed" /><CloseBold v-else /></el-icon>
            <span>{{ result.passed ? '通过' : '未通过' }}</span>
          </div>
          <h1 class="score-exam-name">{{ result.examName }}</h1>
          <div class="score-meta">
            <div class="score-meta-item">
              <el-icon><User /></el-icon>
              <span>{{ result.candidate }}</span>
            </div>
            <div class="score-meta-item">
              <el-icon><Clock /></el-icon>
              <span>用时 {{ result.duration }}</span>
            </div>
            <div class="score-meta-item">
              <el-icon><Calendar /></el-icon>
              <span>{{ result.date }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards Grid -->
    <div class="stats-grid">
      <div class="stat-box">
        <span class="stat-box-value">{{ result.rank }}</span>
        <span class="stat-box-label">成绩排名</span>
      </div>
      <div class="stat-box">
        <span class="stat-box-value">{{ result.avgScore }}</span>
        <span class="stat-box-label">平均分</span>
      </div>
      <div class="stat-box">
        <span class="stat-box-value">{{ result.highest }}</span>
        <span class="stat-box-label">最高分</span>
      </div>
      <div class="stat-box">
        <span class="stat-box-value">{{ result.percentile }}%</span>
        <span class="stat-box-label">超过考生</span>
      </div>
    </div>

    <!-- Score Breakdown + Question List -->
    <div class="detail-grid">
      <!-- Left: category breakdown -->
      <div class="section-card">
        <h3 class="section-card-title">各分类得分</h3>
        <div class="category-breakdown">
          <div v-for="(cat, i) in categories" :key="i" class="category-row">
            <div class="category-header">
              <span class="category-name">{{ cat.name }}</span>
              <span class="category-score">{{ cat.score }}/{{ cat.total }} <small>{{ Math.round(cat.score / cat.total * 100) }}%</small></span>
            </div>
            <div class="category-bar-bg">
              <div class="category-bar-fill" :style="{ width: `${cat.score / cat.total * 100}%`, background: cat.color }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: question list -->
      <div class="section-card">
        <h3 class="section-card-title">答题详情</h3>
        <div class="question-review">
          <div
            v-for="(q, i) in questions"
            :key="i"
            class="review-item"
            :class="{ correct: q.correct, wrong: !q.correct }"
          >
            <div class="review-icon">
              <el-icon v-if="q.correct" :size="16"><CircleCheck /></el-icon>
              <el-icon v-else :size="16"><CloseBold /></el-icon>
            </div>
            <div class="review-content">
              <span class="review-number">第 {{ i + 1 }} 题</span>
              <span class="review-type">{{ q.type }}</span>
            </div>
            <span class="review-score">+{{ q.score }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Score Distribution Chart -->
    <div class="chart-card">
      <div class="chart-card-header">
        <h3 class="section-card-title">成绩分布</h3>
      </div>
      <div class="chart-body">
        <v-chart :option="distributionOption" autoresize class="chart" />
      </div>
    </div>
  </div>
</template>

<script setup>
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
    const s = res.score || 0;
    result.value = {
      examName: res.exam_name || "考核", candidate: "考生",
      score: s, passed: s >= 60, rank: "-",
      avgScore: s, highest: s, percentile: 50,
      duration: Math.floor((res.duration_used || 0) / 60) + " 分钟",
      date: res.submitted_at || ""
    };
    questions.value = (res.questions || []).map(q => ({ type: q.type, correct: true, score: q.score || 2 }));
    categories.value = [
      { name: "售后流程", score: Math.round(s * 0.35), total: 36, color: "var(--c-primary)" },
      { name: "产品知识", score: Math.round(s * 0.2), total: 20, color: "var(--c-info)" },
      { name: "故障处理", score: Math.round(s * 0.25), total: 20, color: "var(--c-warning)" },
      { name: "服务规范", score: Math.round(s * 0.1), total: 12, color: "var(--c-success)" },
      { name: "安全合规", score: Math.round(s * 0.1), total: 12, color: "var(--c-danger)" },
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
</script>

<style scoped>
.result-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-nav { display: flex; }

/* ── Score Hero Section ── */
.score-hero {
  position: relative;
  border-radius: var(--radius-xl);
  overflow: hidden;
  min-height: 200px;
}
.score-hero.passed {
  background: linear-gradient(135deg, #064E3B, #065F46);
}
.score-hero.failed {
  background: linear-gradient(135deg, #7F1D1D, #991B1B);
}
.score-hero-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08) 0%, transparent 60%),
              radial-gradient(circle at 20% 80%, rgba(255,255,255,0.05) 0%, transparent 50%);
  pointer-events: none;
}
.score-hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 40px;
  padding: 40px 48px;
}

.score-display { flex-shrink: 0; }
.score-ring-large {
  width: 140px;
  height: 140px;
  position: relative;
}
.ring-large-svg { width: 100%; height: 100%; }
.ring-large-fill {
  transition: stroke-dasharray 1.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.ring-large-text {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}
.ring-large-score {
  font-family: var(--font-display);
  font-size: 44px;
  font-weight: 700;
  line-height: 1;
}
.ring-large-unit {
  font-size: 14px;
  opacity: 0.7;
  margin-top: 2px;
}

.score-info { flex: 1; }
.score-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}
.badge-pass { background: rgba(16, 185, 129, 0.2); color: #6EE7B7; }
.badge-fail { background: rgba(239, 68, 68, 0.2); color: #FCA5A5; }

.score-exam-name {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: white;
  margin-bottom: 12px;
}
.score-meta {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}
.score-meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}
.score-meta-item .el-icon { font-size: 15px; }

/* ── Stats Grid ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.stat-box {
  background: var(--c-surface);
  border-radius: var(--radius-md);
  padding: 16px;
  text-align: center;
  border: 1px solid var(--c-border-light);
}
.stat-box-value {
  display: block;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--c-primary);
  margin-bottom: 4px;
}
.stat-box-label {
  font-size: 12px;
  color: var(--c-text-tertiary);
}

/* ── Detail Grid ── */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.section-card {
  background: var(--c-surface);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--c-border-light);
}
.section-card-title {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 20px;
}

/* Category Breakdown */
.category-breakdown {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.category-row { display: flex; flex-direction: column; gap: 6px; }
.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.category-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--c-text);
}
.category-score {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text-secondary);
}
.category-score small {
  font-weight: 400;
  color: var(--c-text-tertiary);
  margin-left: 4px;
}
.category-bar-bg {
  height: 8px;
  background: var(--c-bg);
  border-radius: 999px;
  overflow: hidden;
}
.category-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 1s ease;
}

/* Question Review */
.question-review {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.review-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--c-border-light);
  transition: all var(--transition-fast);
}
.review-item:hover { box-shadow: var(--shadow-sm); }
.review-item.correct { background: var(--c-success-bg); }
.review-item.wrong { background: var(--c-danger-bg); }
.review-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.review-item.correct .review-icon { color: var(--c-success); background: rgba(16, 185, 129, 0.1); }
.review-item.wrong .review-icon { color: var(--c-danger); background: rgba(239, 68, 68, 0.1); }
.review-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.review-number {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text);
}
.review-type {
  font-size: 11px;
  color: var(--c-text-tertiary);
}
.review-score {
  font-size: 13px;
  font-weight: 700;
  color: var(--c-success);
}
.review-item.wrong .review-score { color: var(--c-danger); }

/* Chart */
.chart-card {
  background: var(--c-surface);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--c-border-light);
}
.chart-card-header { margin-bottom: 16px; }
.chart-body { height: 260px; }
.chart { width: 100%; height: 100%; }

@media (max-width: 768px) {
  .score-hero-content {
    flex-direction: column;
    text-align: center;
    padding: 32px 24px;
  }
  .score-meta { justify-content: center; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .detail-grid { grid-template-columns: 1fr; }
  .question-review { grid-template-columns: 1fr; }
}
</style>
