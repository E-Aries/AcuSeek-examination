<!-- Author: 达咩 | 轻则 -->

<template>
  <div class="results-page">
    <!-- Header -->
    <div class="results-header">
      <div class="results-header-text">
        <h2 class="results-title">{{ isAdmin ? "成绩查询" : "我的成绩" }}</h2>
        <p class="results-subtitle">{{ isAdmin ? "查看所有考核的统计数据与考生成绩" : "查看你参与过的考核成绩" }}</p>
      </div>
      <div v-if="isAdmin" class="results-header-actions">
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" size="small" />
        <el-button :icon="Download" size="small" @click="exportResults">导出报告</el-button>
      </div>
    </div>

    <!-- Admin overview metrics -->
    <div v-if="isAdmin" class="metrics-scroll">
      <div class="metric-card metric-primary">
        <div class="metric-icon-wrap"><el-icon :size="24"><DataBoard /></el-icon></div>
        <div class="metric-body">
          <span class="metric-value">{{ overview.exams_count }}</span>
          <span class="metric-label">考核场次</span>
        </div>
      </div>
      <div class="metric-card metric-success">
        <div class="metric-icon-wrap"><el-icon :size="24"><CircleCheck /></el-icon></div>
        <div class="metric-body">
          <span class="metric-value">{{ overview.pass_rate }}%</span>
          <span class="metric-label">整体通过率</span>
        </div>
      </div>
      <div class="metric-card metric-warning">
        <div class="metric-icon-wrap"><el-icon :size="24"><UserFilled /></el-icon></div>
        <div class="metric-body">
          <span class="metric-value">{{ overview.total_candidates }}</span>
          <span class="metric-label">参考总人次</span>
        </div>
      </div>
      <div class="metric-card metric-danger">
        <div class="metric-icon-wrap"><el-icon :size="24"><WarningFilled /></el-icon></div>
        <div class="metric-body">
          <span class="metric-value">{{ overview.pending }}</span>
          <span class="metric-label">待批改试卷</span>
        </div>
      </div>
    </div>

    <!-- Admin results list: by exam -->
    <div v-if="isAdmin" class="results-list">
      <div v-for="exam in examResults" :key="exam.id" class="result-card" @click="router.push('/exams/' + exam.id)">
        <div class="result-stripe" :style="{ background: exam.color }"></div>
        <div class="result-main">
          <div class="result-top">
            <div class="result-info">
              <span class="result-type" :class="exam.type">{{ exam.type }}</span>
              <h3 class="result-name">{{ exam.name }}</h3>
            </div>
            <div class="score-ring" :style="{ '--ring-color': exam.passRate >= 80 ? 'var(--c-success)' : exam.passRate >= 60 ? 'var(--c-warning)' : 'var(--c-danger)' }">
              <svg viewBox="0 0 60 60" class="ring-svg">
                <circle cx="30" cy="30" r="26" fill="none" stroke="var(--c-border-light)" stroke-width="5" />
                <circle cx="30" cy="30" r="26" fill="none" :stroke="exam.passRate >= 80 ? 'var(--c-success)' : exam.passRate >= 60 ? 'var(--c-warning)' : 'var(--c-danger)'" stroke-width="5" stroke-linecap="round" :stroke-dasharray="(exam.passRate / 100) * 163.36 + ' 163.36'" transform="rotate(-90 30 30)" class="ring-fill" />
              </svg>
              <span class="ring-text">{{ exam.passRate }}%</span>
            </div>
          </div>
          <div class="result-stats">
            <div class="result-stat"><span class="rs-value">{{ exam.candidates }}</span><span class="rs-label">参考</span></div>
            <div class="result-stat"><span class="rs-value">{{ exam.passed }}</span><span class="rs-label">通过</span></div>
            <div class="result-stat"><span class="rs-value">{{ exam.avgScore }}</span><span class="rs-label">均分</span></div>
            <div class="result-stat"><span class="rs-value">{{ exam.topScore }}</span><span class="rs-label">最高</span></div>
          </div>
          <div class="result-footer">
            <span class="result-date">通过率 {{ exam.passRate }}%</span>
            <div class="result-actions">
              <el-button text type="primary" size="small">查看详情 <el-icon><ArrowRight /></el-icon></el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Candidate results: my exam papers -->
    <div v-else class="my-results">
      <div v-if="myResults.length === 0" class="empty-state">
        <el-icon :size="48"><Document /></el-icon>
        <p>还没有参加过考核</p>
      </div>
      <div v-for="item in myResults" :key="item.paper_id" class="my-result-card" @click="item.status !== '进行中' ? router.push('/results/' + item.paper_id) : null">
        <div class="my-result-left">
          <div class="my-result-type" :class="item.exam_type">{{ item.exam_type }}</div>
          <div class="my-result-name">{{ item.exam_name }}</div>
        </div>
        <div class="my-result-center">
          <div class="my-result-status">
            <span v-if="item.status == '已完成'" :style="gradeResultStyle(item)">{{ gradeResultLabel(item) }}</span>
            <span v-else-if="item.status == '待批改'" style="color:#D97706;font-weight:600">待批改</span>
            <span v-else-if="item.status === '进行中'" style="color:var(--c-primary);font-weight:600">已开始</span>
            <span v-else style="color:#9CA3AF">{{ item.status }}</span>
          </div>
          <div class="my-result-time" v-if="item.submitted_at">提交于 {{ item.submitted_at.slice(0, 16).replace('T', ' ') }}</div>
          <div v-if="item.status === '进行中'" class="inprogress-actions">
            <el-button size="small" type="primary" plain @click.stop="router.push('/exams/' + item.exam_id + '/take')">继续考试</el-button>
            <el-button size="small" text type="danger" @click.stop="discardPaper($event, item.paper_id)">放弃</el-button>
          </div>
        </div>
        <div class="my-result-right">
          <div class="my-result-score">
            <span class="score-value">{{ item.score ?? '-' }}</span>
            <span class="score-sep">/</span>
            <span class="score-total">{{ item.total_score }}</span>
            <span v-if="item.score != null && item.total_score > 0" class="score-pct">({{ Math.round(item.score / item.total_score * 100) }}%)</span>
          </div>
          <div class="my-result-action">
            <el-button text type="primary" size="small">查看详情 <el-icon><ArrowRight /></el-icon></el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { DataBoard, CircleCheck, UserFilled, WarningFilled, Download, Document, Clock, CaretRight, ArrowRight, Top, Bottom } from "@element-plus/icons-vue";
import { api } from "../api.js";
import { ElMessage } from "element-plus";

const router = useRouter();

async function discardPaper(e, paperId) {
  e.stopPropagation();
  var res = await fetch("/api/exams/discard/" + paperId, {
    method: "POST",
    headers: { Authorization: "Bearer " + localStorage.getItem("token") }
  });
  var data = await res.json();
  if (!res.ok) { ElMessage.error(data.detail || "放弃失败"); return; }
  ElMessage.success(data.message);
  myResults.value = myResults.value.filter(function(p) { return p.paper_id !== paperId; });
}
function gradeResultStyle(item) {
  if (!item.total_score || item.score === null || item.score === undefined) return { color: "#9CA3AF" };
  var pct = item.score / item.total_score;
  if (pct >= 0.95) return { display: "inline-block", padding: "2px 8px", borderRadius: "4px", fontSize: "12px", fontWeight: 600, backgroundColor: "#FEF3C7", color: "#D97706" };
  if (pct >= 0.80) return { display: "inline-block", padding: "2px 8px", borderRadius: "4px", fontSize: "12px", fontWeight: 600, backgroundColor: "#DBEAFE", color: "#2563EB" };
  if (pct >= 0.60) return { display: "inline-block", padding: "2px 8px", borderRadius: "4px", fontSize: "12px", fontWeight: 600, backgroundColor: "#D1FAE5", color: "#059669" };
  return { display: "inline-block", padding: "2px 8px", borderRadius: "4px", fontSize: "12px", fontWeight: 600, backgroundColor: "#FEE2E2", color: "#DC2626" };
}
function gradeResultLabel(item) {
  if (!item.total_score || item.score === null || item.score === undefined) return "-";
  var pct = Math.round(item.score / item.total_score * 100);
  if (pct >= 95) return "优秀 " + pct + "%";
  if (pct >= 80) return "良好 " + pct + "%";
  if (pct >= 60) return "通过 " + pct + "%";
  return "未通过 " + pct + "%";
}

const dateRange = ref(null);
const examResults = ref([]);
const myResults = ref([]);
const overview = ref({ exams_count: 0, total_candidates: 0, pass_rate: 0, pending: 0 });

const isAdmin = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem("user") || "{}");
    return u.role === "admin";
  } catch { return false; }
});

onMounted(async () => {
  try {
    const u = JSON.parse(localStorage.getItem("user") || "{}");
    if (u.role === "admin") {
      const [byExamRes, statsRes] = await Promise.all([
        api.results.byExam(),
        api.results.stats()
      ]);
      overview.value = statsRes;
      examResults.value = (byExamRes.items || []).map(r => ({
        id: r.exam_id, name: r.exam_name, type: r.exam_type || "正式",
        candidates: r.candidates, passed: r.passed,
        avgScore: r.avg_score, topScore: r.top_score,
        passRate: r.pass_rate,
        color: r.pass_rate >= 80 ? "linear-gradient(180deg, #10B981, #059669)" : r.pass_rate >= 60 ? "linear-gradient(180deg, #F59E0B, #D97706)" : "linear-gradient(180deg, #EF4444, #DC2626)"
      }));
    } else {
      const myRes = await api.results.my();
      myResults.value = (myRes.items || []).map(r => ({ ...r }));
    }
  } catch(e) { console.error(e); }
});

function exportResults() {
  const token = localStorage.getItem("token");
  const a = document.createElement("a");
  fetch("/api/results/export", { headers: { Authorization: "Bearer " + token } })
    .then(r => r.blob())
    .then(blob => { a.href = URL.createObjectURL(blob); a.download = "考试成绩.csv"; a.click(); URL.revokeObjectURL(a.href); })
    .catch(() => ElMessage.error("导出失败"));
}
</script>

<style scoped>
.results-page { display: flex; flex-direction: column; gap: 24px; }

.results-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.results-title { font-family: var(--font-display); font-size: 22px; font-weight: 700; color: var(--c-text); margin-bottom: 4px; }
.results-subtitle { font-size: 13px; color: var(--c-text-secondary); margin: 0; }
.results-header-actions { display: flex; gap: 8px; align-items: center; }

.metrics-scroll { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
.metric-card { background: var(--c-surface); border-radius: var(--radius-lg); padding: 18px 20px; display: flex; align-items: center; gap: 14px; border: 1px solid var(--c-border-light); }
.metric-icon-wrap { width: 44px; height: 44px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.metric-primary .metric-icon-wrap { background: var(--c-primary-lighter); color: var(--c-primary); }
.metric-success .metric-icon-wrap { background: var(--c-success-bg); color: var(--c-success); }
.metric-warning .metric-icon-wrap { background: var(--c-warning-bg); color: var(--c-warning); }
.metric-danger .metric-icon-wrap { background: var(--c-danger-bg); color: var(--c-danger); }
.metric-body { flex: 1; }
.metric-value { display: block; font-family: var(--font-display); font-size: 24px; font-weight: 700; color: var(--c-text); line-height: 1.2; }
.metric-label { font-size: 12px; color: var(--c-text-tertiary); }

/* Admin results */
.results-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 16px; }
.result-card { background: var(--c-surface); border-radius: var(--radius-lg); display: flex; overflow: hidden; border: 1px solid var(--c-border-light); cursor: pointer; transition: all var(--transition-base); }
.result-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-4px); }
.result-stripe { width: 5px; flex-shrink: 0; }
.result-main { flex: 1; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.result-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
.result-info { flex: 1; }
.result-type { display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 999px; margin-bottom: 6px; }
.result-type.正式 { background: var(--c-danger-bg); color: var(--c-danger); }
.result-type.练习 { background: var(--c-success-bg); color: var(--c-success); }
.result-type.模拟 { background: var(--c-warning-bg); color: var(--c-warning); }
.result-name { font-family: var(--font-display); font-size: 15px; font-weight: 600; color: var(--c-text); }

.score-ring { position: relative; width: 60px; height: 60px; flex-shrink: 0; }
.ring-svg { width: 100%; height: 100%; }
.ring-fill { transition: stroke-dasharray 1s ease; }
.ring-text { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-family: var(--font-display); font-size: 13px; font-weight: 700; color: var(--c-text); }

.result-stats { display: flex; background: var(--c-bg); border-radius: var(--radius-sm); overflow: hidden; }
.result-stat { flex: 1; text-align: center; padding: 8px 0; border-right: 1px solid var(--c-border-light); }
.result-stat:last-child { border-right: none; }
.rs-value { display: block; font-family: var(--font-display); font-size: 16px; font-weight: 700; color: var(--c-text); }
.rs-label { font-size: 11px; color: var(--c-text-tertiary); }
.result-footer { display: flex; align-items: center; justify-content: space-between; padding-top: 10px; border-top: 1px solid var(--c-border-light); }
.result-date { font-size: 12px; color: var(--c-text-tertiary); }
.result-actions { display: flex; gap: 4px; }

/* Candidate results */
.my-results { display: flex; flex-direction: column; gap: 12px; }
.empty-state { text-align: center; padding: 60px 20px; color: var(--c-text-tertiary); }
.empty-state p { margin-top: 12px; font-size: 14px; }
.my-result-card { background: var(--c-surface); border-radius: var(--radius-lg); padding: 16px 20px; display: flex; align-items: center; gap: 20px; border: 1px solid var(--c-border-light); cursor: pointer; transition: all var(--transition-base); }
.my-result-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); border-color: var(--c-primary-lighter); }
.my-result-left { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.my-result-type { font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 999px; display: inline-block; width: fit-content; }
.my-result-type.正式 { background: var(--c-danger-bg); color: var(--c-danger); }
.my-result-type.练习 { background: var(--c-success-bg); color: var(--c-success); }
.my-result-type.模拟 { background: var(--c-warning-bg); color: var(--c-warning); }
.my-result-name { font-size: 16px; font-weight: 600; color: var(--c-text); }
.my-result-center { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.my-result-status { display: flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 500; }
.my-result-status.pass { color: var(--c-success); }
.my-result-status.pending { color: var(--c-warning); }
.my-result-status.doing { color: var(--c-primary); }
.my-result-time { font-size: 12px; color: var(--c-text-tertiary); }
.my-result-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.my-result-score { display: flex; align-items: baseline; gap: 2px; }
.inprogress-actions { display: flex; gap: 8px; margin-top: 4px; }
.score-pct { font-size: 11px; color: var(--c-text-tertiary); margin-left: 2px; }
.my-result-score.pass .score-value { color: var(--c-success); }
.my-result-score.fail .score-value { color: var(--c-danger); }
.score-value { font-family: var(--font-display); font-size: 24px; font-weight: 700; }
.score-sep { font-size: 14px; color: var(--c-text-tertiary); }
.score-total { font-size: 14px; color: var(--c-text-tertiary); }

@media (max-width: 768px) {
  .results-list { grid-template-columns: 1fr; }
  .my-result-card { flex-direction: column; align-items: stretch; gap: 12px; }
  .my-result-right { flex-direction: row; align-items: center; justify-content: space-between; }
}
</style>
