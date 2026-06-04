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
              <span class="ring-large-unit">/ {{ result.maxScore }}</span>
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
            <span class="review-score">{{ q.correct === true ? q.score : 0 }}/{{ q.score }}</span>
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
import { useRoute } from "vue-router";
import { ArrowLeft, CircleCheck, CloseBold, WarningFilled, User, Clock, Calendar } from "@element-plus/icons-vue";
import VChart from "vue-echarts";
import "echarts";
import { api } from "../api.js";

const route = useRoute();

const result = ref({ examName: "加载中...", candidate: "", score: 0, maxScore: 100, passed: false, duration: "", date: "", rank: "-", avgScore: "-", highest: "-", percentile: 0 });
const questions = ref([]);
const categories = ref([]);
const distributionData = ref([]);
const totalPapers = ref(0);

const CATEGORY_COLORS = ["var(--c-primary)", "var(--c-info)", "var(--c-warning)", "var(--c-primary-light)", "var(--c-success)", "var(--c-danger)"];

function checkAnswer(paperQ, userAns, fullQ) {
  if (!fullQ || userAns === undefined || userAns === null) return false;
  const type = paperQ.type || fullQ.type;
  const correctAns = (fullQ.answer || "").trim();
  if (type === "简答") return null; // needs manual grading
  if (type === "单选" || type === "判断") return String(userAns).trim() === correctAns;
  if (type === "多选") {
    const ua = new Set(Array.isArray(userAns) ? userAns.map(String) : [String(userAns)]);
    let ca;
    try { ca = new Set(correctAns.startsWith("[") ? JSON.parse(correctAns).map(String) : [correctAns]); }
    catch(e) { ca = new Set([correctAns]); }
    return ua.size === ca.size && [...ua].every(v => ca.has(v));
  }
  if (type === "填空") return String(userAns || "").trim() === correctAns;
  return false;
}

onMounted(async () => {
  try {
    const res = await api.results.get(route.params.id);
    if (res.error) { return; }
    
    const s = res.score || 0;
    const passScore = res.pass_score || 60;
    const paperQs = res.questions || [];
    const answers = res.answers || {};
    const examId = res.exam_id;

    // Fetch all questions (for categories + correct answers) and all papers (for stats)
    const [qRes, papersRes] = await Promise.all([
      api.questions.list({ size: 999 }),
      examId ? api.exams.papers(examId) : Promise.resolve({ items: [] })
    ]);
    
    const allQs = qRes.items || [];
    const allPapers = papersRes.items || [];
    
    // Build question lookup map
    const qMap = {};
    allQs.forEach(q => { qMap[q.id] = q; });

    // Compute max possible score from paper questions
    let maxScore = 0;
    paperQs.forEach(pq => { maxScore += pq.score || 2; });

    // Build category breakdown
    const catMap = {};
    paperQs.forEach(pq => {
      const fullQ = qMap[pq.id];
      const cat = (fullQ && fullQ.category) || "未分类";
      if (!catMap[cat]) catMap[cat] = { total: 0, score: 0 };
      catMap[cat].total += pq.score || 2;
    });
    paperQs.forEach(pq => {
      const qid = String(pq.id);
      const fullQ = qMap[pq.id];
      const cat = (fullQ && fullQ.category) || "未分类";
      const userAns = answers[qid];
      const correct = checkAnswer(pq, userAns, fullQ);
      if (correct === true) catMap[cat].score += pq.score || 2;
    });
    
    let colorIdx = 0;
    categories.value = Object.entries(catMap).map(([name, data]) => ({
      name, score: data.score, total: data.total,
      percent: data.total > 0 ? Math.round(data.score / data.total * 100) : 0,
      color: CATEGORY_COLORS[colorIdx++ % CATEGORY_COLORS.length]
    }));

    // Build question review
    questions.value = paperQs.map(pq => {
      const fullQ = qMap[pq.id];
      const userAns = answers[String(pq.id)];
      return {
        type: pq.type || (fullQ && fullQ.type) || "未知",
        correct: checkAnswer(pq, userAns, fullQ),
        score: pq.score || 2
      };
    });

    // Compute rank, avg, highest, percentile
    const scores = allPapers.map(p => p.score).filter(s => s !== null && s !== undefined);
    totalPapers.value = scores.length;
    const sorted = [...scores].sort((a, b) => b - a);
    const rankIdx = sorted.findIndex(sc => sc <= s);
    const rank = rankIdx >= 0 ? rankIdx + 1 : "-";
    const rankDisplay = rank !== "-" ? rank + "/" + scores.length : "-";
    const avg = scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : "-";
    const highest = scores.length > 0 ? Math.max(...scores) : "-";
    const percentile = scores.length > 1 ? Math.round((scores.length - rank) / (scores.length - 1) * 100) : 0;
    
    // Score distribution
    const buckets = [0, 0, 0, 0, 0];
    scores.forEach(sc => {
      if (sc <= 20) buckets[0]++;
      else if (sc <= 40) buckets[1]++;
      else if (sc <= 60) buckets[2]++;
      else if (sc <= 80) buckets[3]++;
      else buckets[4]++;
    });
    distributionData.value = buckets;

    result.value = {
      examName: res.exam_name || "考核",
      candidate: res.candidate || "考生",
      score: s, maxScore: maxScore || 100,
      passed: s >= passScore,
      rank: rankDisplay, avgScore: avg, highest: highest, percentile: percentile,
      duration: Math.floor((res.duration_used || 0) / 60) + " 分钟",
      date: res.submitted_at ? res.submitted_at.slice(0, 16) : ""
    };
  } catch(e) { console.error(e); }
});

const distributionOption = computed(() => {
  const labels = ["0-20", "21-40", "41-60", "61-80", "81-100"];
  const barColors = ["var(--c-danger)", "var(--c-warning)", "var(--c-accent)", "var(--c-primary-light)", "var(--c-success)"];
  return {
    grid: { left: 50, right: 20, top: 10, bottom: 30 },
    xAxis: { type: "category", data: labels, axisLabel: { color: "#9CA3AF", fontSize: 11 }, axisTick: { show: false }, axisLine: { show: false } },
    yAxis: { type: "value", splitLine: { lineStyle: { color: "#F0EFEC", type: "dashed" } }, axisLabel: { color: "#9CA3AF", fontSize: 11 } },
    series: [{
      type: "bar",
      data: distributionData.value.map((v, i) => ({ value: v, itemStyle: { color: barColors[i] } })),
      barWidth: 36, borderRadius: [6,6,0,0],
      label: { show: true, position: "top", formatter: "{c}人", color: "#6B7280", fontSize: 12 }
    }],
    tooltip: { trigger: "axis" },
  };
});
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
