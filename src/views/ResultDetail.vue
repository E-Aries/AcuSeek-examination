<template>
  <div v-if="loading" class="loading-state">
    <el-icon class="is-loading" :size="32"><Loading /></el-icon>
    <p>加载中...</p>
  </div>
  <template v-else>
  <div class="result-detail">
    <div class="detail-nav">
      <el-button text :icon="ArrowLeft" @click="$router.push('/results')" class="back-btn">
        <span>返回成绩列表</span>
      </el-button>
    </div>
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
              <circle cx="70" cy="70" r="60" fill="none" stroke="url(#scoreGrad)" stroke-width="8" stroke-linecap="round" :stroke-dasharray="`${(result.score / 100) * 376.99} 376.99`" transform="rotate(-90 70 70)" class="ring-large-fill" />
            </svg>
            <div class="ring-large-text">
              <span class="ring-large-score">{{ result.score }}</span>
              <span class="ring-large-unit">/ {{ result.maxScore }}</span>
            </div>
          </div>
        </div>
        <div class="score-info">
          <div class="grade-badge" :class="'grade-' + grade.key">
            <el-icon :size="18">
              <StarFilled v-if="grade.key === 'excellent'" />
              <CircleCheckFilled v-else-if="grade.key === 'good'" />
              <CircleCheck v-else-if="grade.key === 'pass'" />
              <CloseBold v-else />
            </el-icon>
            <span>{{ grade.label }}</span>
            <span class="grade-pct">{{ gradePercent }}%</span>
          </div>
          <h1 class="score-exam-name">{{ result.examName }}</h1>
          <div class="score-meta">
            <div class="score-meta-item"><el-icon><User /></el-icon><span>{{ result.candidate }}</span></div>
            <div class="score-meta-item"><el-icon><Clock /></el-icon><span>用时 {{ result.duration }}</span></div>
            <div class="score-meta-item"><el-icon><Calendar /></el-icon><span>{{ result.date }}</span></div>
          </div>
        </div>
      </div>
    </div>
    <div class="stats-grid">
      <div class="stat-box"><span class="stat-box-value">{{ result.rank }}</span><span class="stat-box-label">成绩排名</span></div>
      <div class="stat-box"><span class="stat-box-value">{{ result.avgScore }}</span><span class="stat-box-label">平均分</span></div>
      <div class="stat-box"><span class="stat-box-value">{{ result.highest }}</span><span class="stat-box-label">最高分</span></div>
      <div class="stat-box"><span class="stat-box-value">{{ result.percentile }}%</span><span class="stat-box-label">超过考生</span></div>
    </div>
    <div class="detail-grid">
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
      <div class="section-card">
        <h3 class="section-card-title">
          答题详情
          <span class="q-summary">
            <span class="q-summary-correct">{{ correctCount }}</span> 正确 /
            <span class="q-summary-wrong">{{ wrongCount }}</span> 错误
          </span>
        </h3>
        <div class="question-review">
          <div v-for="(q, i) in questions" :key="i" class="review-card" :class="{ correct: q.correct, wrong: !q.correct, expanded: expandedIndex === i }">
            <div class="review-header" @click="toggleExpand(i)">
              <div class="review-icon">
                <el-icon v-if="q.correct" :size="16"><CircleCheck /></el-icon>
                <el-icon v-else :size="16"><CloseBold /></el-icon>
              </div>
              <div class="review-content">
                <span class="review-number">第 {{ i + 1 }} 题</span>
                <span class="review-type-tag" :class="q.type">{{ q.type }}</span>
              </div>
              <span class="review-score" :class="q.correct ? 'sc-pass' : 'sc-fail'">{{ q.manualScore !== null ? q.manualScore : (q.correct === true ? q.score : 0) }}/{{ q.score }}<span v-if="q.manualGraded" class="manual-badge">手工评分</span></span>
              <el-icon class="expand-icon" :class="{ rotated: expandedIndex === i }"><ArrowDown /></el-icon>
            </div>
            <div v-if="expandedIndex === i" class="review-detail">
              <div class="rd-section rd-question">
                <div class="rd-label">题目</div>
                <div class="rd-content-text">{{ q.content }}</div>
              </div>
              <div class="rd-section rd-score">
                <div class="rd-label"><el-icon :size="14"><StarFilled /></el-icon><span>得分</span></div>
                <div class="rd-score-value" :class="q.correct ? 'correct' : 'wrong'">
                  {{ q.manualScore !== null ? q.manualScore : (q.correct === true ? q.score : 0) }} / {{ q.score }}<span v-if="q.manualGraded" style="font-size:11px;font-weight:400;margin-left:6px;padding:1px 6px;border-radius:3px;background:rgba(245,158,11,0.15);color:#D97706">手工评分</span>
                  <span class="rd-score-status">({{ q.correct === true ? '正确' : '错误' }})</span>
                </div>
              </div>
              <div v-if="q.options && q.options.length" class="rd-section rd-options">
                <div class="rd-label">选项</div>
                <div v-for="opt in q.options" :key="opt.label" class="rd-option" :class="{ 'is-user-answer': isUserAnswer(q, opt.label), 'is-correct-answer': isCorrectAnswer(q, opt.label), 'is-wrong': isUserAnswer(q, opt.label) && !isCorrectAnswer(q, opt.label) }">
                  <span class="rd-opt-label">{{ opt.label }}</span>
                  <span class="rd-opt-text">{{ opt.text }}</span>
                  <span v-if="isCorrectAnswer(q, opt.label) && !isUserAnswer(q, opt.label)" class="rd-opt-badge correct-badge">正确答案</span>
                </div>
              </div>
              <div class="rd-section rd-comparison">
                <div class="rd-compare-row">
                  <div class="rd-compare-label"><el-icon :size="14"><User /></el-icon><span>你的答案</span></div>
                  <div class="rd-compare-value" :class="{ correct: q.correct, wrong: !q.correct }">{{ formatAnswer(q.userAnswer, q) }}</div>
                </div>
                <div class="rd-compare-row">
                  <div class="rd-compare-label"><el-icon :size="14"><CircleCheck /></el-icon><span>{{ q.type === '简答' ? '参考答案' : '正确答案' }}</span></div>
                  <div  class="rd-compare-value correct">{{ formatAnswer(q.correctAnswer, q) }}</div>
                </div>
              </div>
              <div v-if="q.explanation" class="rd-section rd-explanation">
                <div class="rd-label"><el-icon :size="14"><WarningFilled /></el-icon><span>解析</span></div>
                <div class="rd-explain-text">{{ q.explanation }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Difficulty Breakdown -->
    <div class="section-card">
      <h3 class="section-card-title">难度得分</h3>
      <div class="difficulty-breakdown">
        <div v-for="(ds, key) in difficultyStats" :key="key" class="diff-row">
          <div class="diff-header">
            <span class="diff-label" :style="{ color: ds.color }">{{ ds.label }}</span>
            <span class="diff-count">{{ ds.questions }}题</span>
          </div>
          <div class="category-bar-bg">
            <div class="category-bar-fill" :style="{ width: ds.pct + '%', background: ds.color }"></div>
          </div>
          <div class="diff-score">
            <span class="diff-score-value">{{ ds.correct }}/{{ ds.total }}</span>
            <span class="diff-score-pct">{{ ds.pct }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-card">
      <div class="chart-card-header"><h3 class="section-card-title">成绩分布</h3></div>
      <div class="chart-body">
        <v-chart :option="distributionOption" autoresize class="chart" />
      </div>
    </div>
  </div>
  </template>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { ArrowLeft, ArrowDown, StarFilled, CircleCheckFilled, CircleCheck, CloseBold, WarningFilled, User, Clock, Calendar, Loading } from "@element-plus/icons-vue";
import VChart from "vue-echarts";
import "echarts";
import { api } from "../api.js";
import { ElMessage } from "element-plus";

const route = useRoute();

const result = ref({ examName: "加载中..", candidate: "", score: 0, maxScore: 100, passed: false, duration: "", date: "", rank: "-", avgScore: "-", highest: "-", percentile: 0 });
const questions = ref([]);
const categories = ref([]);
const distributionData = ref([]);
const totalPapers = ref(0);

const loading = ref(true);
const expandedIndex = ref(-1);

const CATEGORY_COLORS = ["var(--c-primary)", "var(--c-info)", "var(--c-warning)", "var(--c-primary-light)", "var(--c-success)", "var(--c-danger)"];

const grade = computed(() => {
  const pct = result.value.maxScore > 0 ? result.value.score / result.value.maxScore : 0;
  if (pct >= 0.95) return { key: "excellent", label: "优秀" };
  if (pct >= 0.80) return { key: "good", label: "良好" };
  if (pct >= 0.60) return { key: "pass", label: "通过" };
  return { key: "fail", label: "未通过" };
});

const gradePercent = computed(() => {
  return result.value.maxScore > 0 ? Math.round(result.value.score / result.value.maxScore * 100) : 0;
});

const difficultyStats = computed(() => {
  const labels = { 1: { label: "简单", color: "#10B981" }, 2: { label: "中等", color: "#F59E0B" }, 3: { label: "困难", color: "#EF4444" } };
  const res = {};
  [1, 2, 3].forEach(d => { res[d] = { ...labels[d], questions: 0, total: 0, correct: 0, pct: 0 }; });
  questions.value.forEach(q => {
    const d = q.difficulty || 1;
    if (res[d]) { res[d].questions++; res[d].total += q.score; if (q.correct === true) res[d].correct += q.score; }
  });
  Object.values(res).forEach(s => { s.pct = s.total > 0 ? Math.round(s.correct / s.total * 100) : 0; });
  return res;
});

const correctCount = computed(() => questions.value.filter(q => q.correct === true).length);
const wrongCount = computed(() => questions.value.filter(q => q.correct === false).length);

function checkAnswer(paperQ, userAns, fullQ) {
  if (!fullQ || userAns === undefined || userAns === null) return false;
  const type = paperQ.type || fullQ.type;
  const correctAns = (fullQ.answer || "").trim();
  if (type === "简答") {
    if (!userAns || !String(userAns).trim()) return false;
    return null;
  }
  if (type === "判断") {
    if (fullQ && fullQ.options) {
      var optMap = {};
      fullQ.options.forEach(function(o) { optMap[o.label] = o.text; });
      var userAnsText = optMap[String(userAns).trim()] || String(userAns).trim();
      return userAnsText === correctAns;
    }
    return String(userAns).trim() === correctAns;
  }
  if (type === "单选") return String(userAns).trim() === correctAns;
  if (type === "多选") {
    const ua = new Set(Array.isArray(userAns) ? userAns.map(String) : [String(userAns)]);
    let ca;
    try {
      if (correctAns.startsWith("[")) {
        ca = new Set(JSON.parse(correctAns).map(String));
      } else {
        ca = new Set(correctAns.split(",").map(function(s) { return s.trim(); }).filter(function(s) { return s; }));
      }
    }
    catch(e) { ca = new Set([correctAns]); }
    return ua.size === ca.size && [...ua].every(v => ca.has(v));
  }
  if (type === "填空") return String(userAns || "").trim() === correctAns;
  return false;
}

function formatAnswer(ans, q) {
  if (ans === undefined || ans === null || ans === "") return "未作答";
  // For judgment, map label to text
  if (q && q.type === "判断" && q.options && typeof ans === "string") {
    var opt = q.options.find(function(o) { return o.label === ans; });
    if (opt) return opt.text;
  }
  if (Array.isArray(ans)) return ans.join(", ");
  return String(ans);
}

function isUserAnswer(q, label) {
  if (q.correctAnswer === undefined) return false;
  if (q.type === "多选") {
    const ua = Array.isArray(q.userAnswer) ? q.userAnswer : [];
    return ua.includes(label);
  }
  return String(q.userAnswer || "").trim() === label;
}

function isCorrectAnswer(q, label) {
  if (q.correctAnswer === undefined) return false;
  // For judgment, map text answer back to label
  if (q.type === "判断" && q.options) {
    var opt = q.options.find(function(o) { return o.text === String(q.correctAnswer || "").trim(); });
    if (opt) return opt.label === label;
  }
  if (q.type === "多选") {
    try {
      var ca;
      if (q.correctAnswer.startsWith("[")) {
        ca = JSON.parse(q.correctAnswer).map(String);
      } else {
        ca = q.correctAnswer.split(",").map(function(s) { return s.trim(); }).filter(function(s) { return s; });
      }
      return ca.includes(label);
    } catch(e) { return String(q.correctAnswer).trim() === label; }
  }
  return String(q.correctAnswer || "").trim() === label;
}

function toggleExpand(i) {
  expandedIndex.value = expandedIndex.value === i ? -1 : i;
}

onMounted(async () => {
  loading.value = true;
  try {
    const res = await api.results.get(route.params.id);
    if (res.error) { loading.value = false; return; }

    const s = res.score || 0;
    const passScore = res.pass_score || 60;
    const paperQs = res.questions || [];
    const answers = res.answers || {};
    const examId = res.exam_id;

    const [qRes, papersRes] = await Promise.all([
      api.questions.list({ size: 999 }),
      examId ? api.exams.papers(examId) : Promise.resolve({ items: [] })
    ]);

    const allQs = qRes.items || [];
    const allPapers = papersRes.items || [];

    const qMap = {};
    allQs.forEach(q => { qMap[q.id] = q; });

    let maxScore = 0;
    paperQs.forEach(pq => { maxScore += pq.score || 2; });

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

    questions.value = paperQs.map(pq => {
      const fullQ = qMap[pq.id] || {};
      const qid = String(pq.id);
      const userAns = answers[qid];
      var grades = answers._grades || {};
      var mGrade = grades[qid];
      return {
        id: pq.id,
        type: pq.type || fullQ.type || "未知",
        score: pq.score || 2,
        difficulty: fullQ.difficulty || 1,
        manualScore: mGrade ? mGrade.score : null,
        manualGraded: mGrade ? mGrade.manual : false,
        correct: mGrade ? mGrade.correct : checkAnswer(pq, userAns, fullQ),
        content: fullQ.content || "",
        options: fullQ.options || [],
        userAnswer: userAns,
        correctAnswer: pq.type === "简答" ? (fullQ.explanation || fullQ.answer || "") : (fullQ.answer || ""),
        explanation: fullQ.explanation || ""
      };
    });

    // For essay questions without stored grades, compute score from total
    if (res.score) {
      var autoTotal = 0;
      questions.value.forEach(function(q) {
        if (q.type !== "简答" && q.correct === true) autoTotal += q.score;
      });
      var manualTotal = Math.max(0, res.score - autoTotal);
      var essayQ = questions.value.filter(function(q) { return q.type === "简答" && q.manualScore === null; });
      if (essayQ.length && manualTotal > 0) {
        var share = Math.round(manualTotal / essayQ.length);
        essayQ.forEach(function(q) {
          q.manualScore = Math.min(share, q.score);
          q.correct = q.manualScore > 0;
          q.manualGraded = true;
        });
      }
    }

    const scores = allPapers.map(p => p.score).filter(s => s !== null && s !== undefined);
    totalPapers.value = scores.length;
    const sorted = [...scores].sort((a, b) => b - a);
    const rankIdx = sorted.findIndex(sc => sc <= s);
    const rank = rankIdx >= 0 ? rankIdx + 1 : "-";
    const rankDisplay = rank !== "-" ? rank + "/" + scores.length : "-";
    const avg = scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : "-";
    const highest = scores.length > 0 ? Math.max(...scores) : "-";
    const percentile = scores.length > 1 ? Math.round((scores.length - rank) / (scores.length - 1) * 100) : 0;

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
      passed: maxScore > 0 && s >= maxScore * passScore / 100,
      rank: rankDisplay, avgScore: avg, highest: highest, percentile: percentile,
      duration: Math.floor((res.duration_used || 0) / 60) + " 分钟",
      date: res.submitted_at ? res.submitted_at.slice(0, 16) : ""
    };
    loading.value = false;
  } catch(e) {
    console.error(e);
    ElMessage.error("加载成绩失败");
    loading.value = false;
  }
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
.result-detail { display: flex; flex-direction: column; gap: 24px; }
.detail-nav { display: flex; }

.score-hero { position: relative; border-radius: var(--radius-xl); overflow: hidden; min-height: 200px; }
.score-hero.passed { background: linear-gradient(135deg, #064E3B, #065F46); }
.score-hero.failed { background: linear-gradient(135deg, #7F1D1D, #991B1B); }
.score-hero-bg { position: absolute; inset: 0; background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08) 0%, transparent 60%), radial-gradient(circle at 20% 80%, rgba(255,255,255,0.05) 0%, transparent 50%); pointer-events: none; }
.score-hero-content { position: relative; z-index: 1; display: flex; align-items: center; gap: 40px; padding: 40px 48px; }
.score-display { flex-shrink: 0; }
.score-ring-large { width: 140px; height: 140px; position: relative; }
.ring-large-svg { width: 100%; height: 100%; }
.ring-large-fill { transition: stroke-dasharray 1.5s cubic-bezier(0.4, 0, 0.2, 1); }
.ring-large-text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; }
.ring-large-score { font-family: var(--font-display); font-size: 44px; font-weight: 700; line-height: 1; }
.ring-large-unit { font-size: 14px; opacity: 0.7; margin-top: 2px; }
.score-info { flex: 1; }
.score-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; margin-bottom: 12px; }
.badge-pass { background: rgba(16, 185, 129, 0.2); color: #6EE7B7; }
.badge-fail { background: rgba(239, 68, 68, 0.2); color: #FCA5A5; }
.score-exam-name { font-family: var(--font-display); font-size: 22px; font-weight: 700; color: white; margin-bottom: 12px; }
.score-meta { display: flex; gap: 24px; flex-wrap: wrap; }
.score-meta-item { display: flex; align-items: center; gap: 6px; font-size: 13px; color: rgba(255, 255, 255, 0.7); }
.score-meta-item .el-icon { font-size: 15px; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.stat-box { background: var(--c-surface); border-radius: var(--radius-md); padding: 16px; text-align: center; border: 1px solid var(--c-border-light); }
.stat-box-value { display: block; font-family: var(--font-display); font-size: 22px; font-weight: 700; color: var(--c-primary); margin-bottom: 4px; }
.stat-box-label { font-size: 12px; color: var(--c-text-tertiary); }

.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.section-card { background: var(--c-surface); border-radius: var(--radius-lg); padding: 24px; box-shadow: var(--shadow-sm); border: 1px solid var(--c-border-light); }
.section-card-title { font-family: var(--font-display); font-size: 15px; font-weight: 600; color: var(--c-text); margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
.q-summary { font-size: 12px; font-weight: 500; margin-left: auto; }
.q-summary-correct { color: var(--c-success); font-weight: 700; }
.q-summary-wrong { color: var(--c-danger); font-weight: 700; }

.category-breakdown { display: flex; flex-direction: column; gap: 16px; }
.category-row { display: flex; flex-direction: column; gap: 6px; }
.category-header { display: flex; justify-content: space-between; align-items: center; }
.category-name { font-size: 13px; font-weight: 500; color: var(--c-text); }
.category-score { font-size: 13px; font-weight: 600; color: var(--c-text-secondary); }
.category-score small { font-weight: 400; color: var(--c-text-tertiary); margin-left: 4px; }
.category-bar-bg { height: 8px; background: var(--c-bg); border-radius: 999px; overflow: hidden; }
.category-bar-fill { height: 100%; border-radius: 999px; transition: width 1s ease; }

.question-review { display: flex; flex-direction: column; gap: 8px; }
.review-card { border: 1px solid var(--c-border-light); border-radius: var(--radius-sm); overflow: hidden; transition: all var(--transition-fast); background: var(--c-surface); }
.review-card.correct { border-left: 3px solid var(--c-success); }
.review-card.wrong { border-left: 3px solid var(--c-danger); }
.review-card.expanded { box-shadow: var(--shadow-sm); }
.review-header { display: flex; align-items: center; gap: 10px; padding: 10px 12px; cursor: pointer; transition: background var(--transition-fast); user-select: none; }
.review-header:hover { background: var(--c-bg); }
.review-icon { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.review-card.correct .review-icon { color: var(--c-success); background: rgba(16, 185, 129, 0.1); }
.review-card.wrong .review-icon { color: var(--c-danger); background: rgba(239, 68, 68, 0.1); }
.review-content { flex: 1; display: flex; align-items: center; gap: 8px; }
.review-number { font-size: 13px; font-weight: 600; color: var(--c-text); }
.review-type-tag { font-size: 11px; font-weight: 500; padding: 1px 8px; border-radius: 4px; background: var(--c-bg); color: var(--c-text-tertiary); border: 1px solid var(--c-border-light); }
.review-type-tag.\5355\9009 { background: #E8EFF7; color: #1E3A5F; }
.review-type-tag.\591A\9009 { background: #ECFDF5; color: #059669; }
.review-type-tag.\5224\65AD { background: #FFFBEB; color: #D97706; }
.review-type-tag.\586B\7A7A { background: #EFF6FF; color: #2563EB; }
.review-type-tag.\7B80\7B54 { background: #FEF2F2; color: #DC2626; }
.review-score { font-size: 13px; font-weight: 700; white-space: nowrap; }
.review-score.sc-pass { color: var(--c-success); }
.review-score.sc-fail { color: var(--c-danger); }
.expand-icon { font-size: 16px; color: var(--c-text-tertiary); transition: transform 0.25s ease; }
.expand-icon.rotated { transform: rotate(180deg); }
.review-detail { padding: 0 12px 14px; border-top: 1px solid var(--c-border-light); animation: detailIn 0.25s ease; }
.rd-section { margin-top: 12px; }
.rd-label { display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: var(--c-text-tertiary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.rd-content-text { font-size: 14px; line-height: 1.7; color: var(--c-text); padding: 10px 14px; background: var(--c-bg); border-radius: var(--radius-sm); border: 1px solid var(--c-border-light); }
.rd-option { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: var(--radius-sm); border: 1px solid var(--c-border-light); margin-bottom: 6px; transition: all var(--transition-fast); position: relative; }
.rd-option.is-user-answer.is-correct-answer { border-color: var(--c-success); background: var(--c-success-bg); }
.rd-option.is-user-answer.is-wrong { border-color: var(--c-danger); background: var(--c-danger-bg); }
.rd-option.is-correct-answer:not(.is-user-answer) { border-color: var(--c-success); background: rgba(16, 185, 129, 0.05); }
.rd-opt-label { font-weight: 700; font-size: 13px; color: var(--c-text); min-width: 20px; }
.rd-opt-text { font-size: 13px; color: var(--c-text-secondary); flex: 1; }
.rd-opt-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; flex-shrink: 0; }
.correct-badge { background: rgba(16, 185, 129, 0.15); color: var(--c-success); }
.wrong-badge { background: rgba(239, 68, 68, 0.15); color: var(--c-danger); }
.rd-compare-row { display: flex; align-items: center; gap: 12px; padding: 8px 12px; margin-bottom: 6px; border-radius: var(--radius-sm); border: 1px solid var(--c-border-light); }
.rd-compare-label { display: flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 600; color: var(--c-text-tertiary); min-width: 80px; flex-shrink: 0; }
.rd-compare-value { font-size: 14px; font-weight: 500; color: var(--c-text); word-break: break-word; }
.rd-compare-value.correct { color: var(--c-success); }
.rd-compare-value.wrong { color: var(--c-danger); text-decoration: line-through; }
.rd-score { margin-top: 12px; }
.rd-score-value { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; font-family: var(--font-display); }
.rd-score-value.correct { color: var(--c-success); }
.rd-score-value.wrong { color: var(--c-danger); }
.rd-score-status { font-size: 12px; font-weight: 500; opacity: 0.7; }
.manual-badge { font-size: 11px; font-weight: 500; margin-left: 6px; padding: 1px 6px; border-radius: 3px; background: rgba(245,158,11,0.15); color: #D97706; }
.rd-explain-text { font-size: 13px; line-height: 1.7; color: var(--c-text-secondary); padding: 10px 14px; background: var(--c-warning-bg); border-radius: var(--radius-sm); border: 1px solid rgba(245, 158, 11, 0.2); }
.chart-card { background: var(--c-surface); border-radius: var(--radius-lg); padding: 24px; box-shadow: var(--shadow-sm); border: 1px solid var(--c-border-light); }
.chart-card-header { margin-bottom: 16px; }
.chart-body { height: 260px; }
.chart { width: 100%; height: 100%; }
.grade-badge { display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; border-radius: 999px; font-size: 14px; font-weight: 700; margin-bottom: 12px; }
.grade-badge .grade-pct { font-size: 12px; font-weight: 500; opacity: 0.8; margin-left: 4px; }
.grade-excellent { background: rgba(245,158,11,0.2); color: #F59E0B; }
.grade-good { background: rgba(59,130,246,0.2); color: #3B82F6; }
.grade-pass { background: rgba(16,185,129,0.2); color: #10B981; }
.grade-fail { background: rgba(239,68,68,0.2); color: #EF4444; }

.difficulty-breakdown { display: flex; flex-direction: column; gap: 16px; }
.diff-row { display: flex; flex-direction: column; gap: 6px; }
.diff-header { display: flex; justify-content: space-between; align-items: center; }
.diff-label { font-size: 13px; font-weight: 600; }
.diff-count { font-size: 12px; color: var(--c-text-tertiary); }
.diff-score { display: flex; justify-content: space-between; align-items: center; font-size: 12px; }
.diff-score-value { font-weight: 700; color: var(--c-text); }
.diff-score-pct { color: var(--c-text-tertiary); }

.loading-state { text-align: center; padding: 80px 0; color: var(--c-text-tertiary); }
.loading-state .el-icon { margin-bottom: 12px; }
.loading-state p { font-size: 14px; }
@keyframes detailIn { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }
@media (max-width: 768px) {
  .score-hero-content { flex-direction: column; text-align: center; padding: 32px 24px; }
  .score-meta { justify-content: center; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .detail-grid { grid-template-columns: 1fr; }
}
</style>
