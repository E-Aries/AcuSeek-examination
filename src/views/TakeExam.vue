<template>
  <div class="take-exam">
    <!-- Top bar: Timer + Progress -->
    <header class="exam-topbar">
      <div class="exam-topbar-left">
        <el-button text :icon="ArrowLeft" @click="handleQuitConfirm" class="back-btn">退出</el-button>
        <span class="topbar-divider"></span>
        <span class="exam-name-tag">{{ examName }}</span>
      </div>
      <div class="exam-topbar-center">
        <div class="progress-info">
          <span class="progress-text">{{ currentIndex + 1 }} / {{ questions.length }}</span>
          <el-progress :percentage="progressPercent" :stroke-width="6" :show-text="false" class="progress-bar" />
        </div>
      </div>
      <div class="exam-topbar-right">
        <div v-if="!practiceMode" class="timer" :class="{ warning: remaining < 300 }">
          <el-icon><Timer /></el-icon>
          <span>{{ formattedTime }}</span>
        </div>
        <el-button v-if="!practiceMode" type="primary" size="small" class="submit-btn" @click="showSubmitConfirm = true">交卷</el-button>
        <el-button v-else type="success" size="small" class="submit-btn" @click="router.push('/exams')">完成练习</el-button>
      </div>
    </header>

    <!-- Main area -->
    <div class="exam-body">
      <!-- Question panel -->
      <div class="question-panel">
        <transition name="slide-q" mode="out-in">
          <div class="question-card" :key="currentIndex">
            <div class="q-header">
              <span class="q-type-badge" :class="qBadgeClass">{{ currentQuestion.type }}</span>
              <span class="q-number">第 {{ currentIndex + 1 }} 题</span>
              <span v-if="currentQuestion.score" class="q-score-badge">{{ currentQuestion.score }} 分</span>
            </div>
            <div class="q-content-wrapper">
              <p class="q-content">{{ currentQuestion.content }}</p>
            </div>

            <!-- Options -->
            <div v-if="['单选','判断'].includes(currentQuestion.type)" class="q-options">
              <div
                v-for="(opt, i) in currentQuestion.options"
                :key="i"
                class="q-option"
                :class="{ selected: answers[currentIndex] === opt.label, correct: (submitted || isPracticeCorrect(opt.label)), wrong: (submitted || isPracticeWrong(opt.label)), locked: answeredLocked[currentIndex] }"
                @click="selectOption(opt.label)"
              >
                <div class="option-marker">
                  <div v-if="answers[currentIndex] === opt.label" class="marker-dot active"></div>
                  <div v-else class="marker-dot"></div>
                </div>
                <span class="option-label">{{ opt.label }}</span>
                <span class="option-text">{{ opt.text }}</span>
              </div>
            </div>

            <!-- Multiple choice -->
            <div v-if="currentQuestion.type === '多选'" class="q-options">
              <div
                v-for="(opt, i) in currentQuestion.options"
                :key="i"
                class="q-option"
                :class="{ selected: multiSelected.includes(opt.label), correct: (submitted || isPracticeCorrect(opt.label)), wrong: (submitted || isPracticeWrong(opt.label)), locked: answeredLocked[currentIndex] }"
                @click="toggleMulti(opt.label)"
              >
                <div class="option-marker multi">
                  <el-icon v-if="multiSelected.includes(opt.label)" :size="14"><Check /></el-icon>
                </div>
                <span class="option-label">{{ opt.label }}</span>
                <span class="option-text">{{ opt.text }}</span>
              </div>
            </div>

            <!-- Fill in the blank -->
            <div v-if="currentQuestion.type === '填空'" class="q-blank">
              <el-input
                v-model="blankAnswer"
                type="textarea"
                :rows="3"
                placeholder="请输入答案..."
                @input="updateAnswer"
              />
            </div>

            <!-- Short answer -->
            <div v-if="currentQuestion.type === '简答'" class="q-blank">
              <el-input
                v-model="essayAnswer"
                type="textarea"
                :rows="6"
                placeholder="请输入你的回答..."
                @input="updateAnswer"
              />
            </div>

            <!-- Practice mode feedback -->
            <div v-if="practiceMode && currentFeedback" class="practice-feedback">
              <div class="pf-header" :class="currentFeedback.correct ? 'correct' : 'wrong'">
                <el-icon :size="20">
                  <component :is="currentFeedback.correct ? CircleCheckFilled : CircleCloseFilled" />
                </el-icon>
                <span>{{ currentFeedback.correct ? '回答正确' : '回答错误' }}</span>
              </div>
              <div class="pf-answer">
                <span class="pf-label">正确答案：</span>
                <span class="pf-value">{{ formatPracticeAnswer(currentFeedback.correctAnswer) }}</span>
              </div>
              <div v-if="currentFeedback.explanation" class="pf-explanation">
                <span class="pf-label">解析：</span>
                <span class="pf-value">{{ currentFeedback.explanation }}</span>
              </div>
            </div>
          </div>
        </transition>

        <!-- Navigation buttons -->
        <div class="q-nav">
          <el-button :disabled="currentIndex === 0" @click="prevQuestion" :icon="ArrowLeft" class="q-nav-btn">上一题</el-button>
          <el-button v-if="currentIndex < questions.length - 1" type="primary" @click="nextQuestion" class="q-nav-btn">下一题 <el-icon><ArrowRight /></el-icon></el-button>
          <el-button v-else type="success" @click="practiceMode ? router.push('/exams') : (showSubmitConfirm = true)" class="q-nav-btn">{{ practiceMode ? '完成练习' : '完成作答' }}</el-button>
        </div>
      </div>

      <!-- Question navigator sidebar -->
      <aside class="question-navigator">
        <div class="nav-header">
          <span class="nav-title">{{ practiceMode ? '练习模式' : '答题卡' }}</span>
          <span class="nav-count">{{ answeredCount }}/{{ questions.length }}</span>
        </div>
        <div class="nav-grid">
          <div
            v-for="(q, i) in questions"
            :key="i"
            class="nav-dot"
            :class="{
              active: i === currentIndex,
              answered: isAnswered(i),
              unanswered: !isAnswered(i) && i !== currentIndex,
            }"
            @click="goToQuestion(i)"
          >
            {{ i + 1 }}
          </div>
        </div>
        <div class="nav-legend">
          <div class="legend-item"><div class="legend-dot answered"></div>已答</div>
          <div class="legend-item"><div class="legend-dot unanswered"></div>未答</div>
          <div class="legend-item"><div class="legend-dot active"></div>当前</div>
        </div>
        <el-button v-if="nextUnanswered > 0" size="small" text @click="goToNextUnanswered" class="nav-jump-btn">
          <el-icon><ArrowRight /></el-icon> 跳至未答 ({{ unansweredIndex + 1 }})
        </el-button>
      </aside>
    </div>

    <!-- Submit confirm dialog -->
    <el-dialog v-model="showSubmitConfirm" title="确认交卷" width="400px">
      <div class="submit-summary">
        <p>您已完成 <strong>{{ answeredCount }}</strong> / {{ questions.length }} 题。</p>
        <p v-if="unansweredCount > 0" style="color:var(--c-warning)">还有 {{ unansweredCount }} 题未作答，确定要交卷吗？</p>
        <p v-else style="color:var(--c-success)">所有题目均已作答，可以交卷了。</p>
      </div>
      <template #footer>
        <el-button @click="showSubmitConfirm = false">继续作答</el-button>
        <el-button type="primary" @click="confirmSubmit">确认交卷</el-button>
      </template>
    </el-dialog>

    <!-- Score result dialog -->
    <el-dialog v-model="showResult" title="交卷成功" width="480px" :close-on-click-modal="false" :show-close="false">
      <div class="result-display">
        <div class="result-hero" :class="{ passed: resultData.passed }">
          <div class="result-score">{{ resultData.score }}</div>
          <div class="result-label">得分</div>
        </div>
        <div class="result-stats">
          <div class="result-stat-item">
            <span class="rs-value">{{ resultData.totalQuestions }}</span>
            <span class="rs-label">总题数</span>
          </div>
          <div class="result-stat-item">
            <span class="rs-value">{{ resultData.correctCount }}</span>
            <span class="rs-label">答对</span>
          </div>
          <div class="result-stat-item">
            <span class="rs-value">{{ resultData.maxScore }}</span>
            <span class="rs-label">满分</span>
          </div>
          <div class="result-stat-item">
            <span class="rs-value">{{ resultData.status }}</span>
            <span class="rs-label">状态</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="router.push('/results')" type="primary">查看成绩</el-button>
        <el-button @click="router.push('/exams')">返回考试列表</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>

import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, ArrowRight, Timer, Check, CircleCheckFilled, CircleCloseFilled } from "@element-plus/icons-vue";
import { api } from "../api.js";
import { ElMessage, ElMessageBox } from "element-plus";

const route = useRoute();
const router = useRouter();
const currentIndex = ref(0);
const answers = ref({});
const multiSelected = ref([]);
const blankAnswer = ref("");
const essayAnswer = ref("");
const showSubmitConfirm = ref(false);
const questions = ref([]);
const examName = ref("加载中...");
const paperId = ref(null);
const remaining = ref(0);
const totalSeconds = ref(3600);
const showResult = ref(false);
const switchCount = ref(0);
const maxSwitches = 3;
const resultData = ref({ score: 0, maxScore: 0, correctCount: 0, totalQuestions: 0, status: "", passed: false });
const submitted = ref(false);
const practiceMode = ref(false);
const examPassScore = ref(60);
const practiceFeedback = ref({});
const answeredLocked = ref({});
const questionDetail = ref({});
let timer = null;

function saveState() {
  try {
    sessionStorage.setItem("exam_" + route.params.id, JSON.stringify({
      paperId: paperId.value,
      questions: questions.value,
      answers: answers.value,
      remaining: remaining.value,
      totalSeconds: totalSeconds.value,
      currentIndex: currentIndex.value,
      examName: examName.value,
      switchCount: switchCount.value
    }));
  } catch(e) {}
}

function restoreState() {
  try {
    const saved = sessionStorage.getItem("exam_" + route.params.id);
    if (!saved) return false;
    const state = JSON.parse(saved);
    paperId.value = state.paperId;
    questions.value = state.questions || [];
    answers.value = state.answers || {};
    remaining.value = state.remaining || 0;
    totalSeconds.value = state.totalSeconds || 0;
    currentIndex.value = state.currentIndex || 0;
    examName.value = state.examName || "考试进行中";
    switchCount.value = state.switchCount || 0;
    return true;
  } catch(e) { return false; }
}

onMounted(async () => {
  practiceMode.value = route.query.mode === "practice";
  if (practiceMode.value) {
    try {
      const [res, examRes] = await Promise.all([
        api.exams.start(route.params.id, "practice"),
        api.exams.get(route.params.id)
      ]);
      paperId.value = res.paper_id;
      questions.value = res.questions || [];
      examName.value = (examRes.name || "").replace("考试", "").replace("考核", "") + "（练习模式）";
      saveState();
    } catch(e) { ElMessage.error("加载失败"); }
    return;
  }
  try {
    const [res, examRes] = await Promise.all([
      api.exams.start(route.params.id),
      api.exams.get(route.params.id)
    ]);
    paperId.value = res.paper_id;
    questions.value = res.questions || [];
    examName.value = examRes.name || "考试进行中";
      examPassScore.value = examRes.pass_score || 60;
    remaining.value = (examRes.duration || 60) * 60;
    totalSeconds.value = remaining.value;
    saveState();
    timer = setInterval(() => { if (remaining.value > 0) { remaining.value--; saveState(); } else { clearInterval(timer); confirmSubmit(); } }, 1000);
    document.addEventListener("visibilitychange", handleVisibilityChange);
  } catch(e) { ElMessage.error("加载失败"); }
});

onUnmounted(() => { clearInterval(timer); document.removeEventListener("visibilitychange", handleVisibilityChange); });

const currentQuestion = computed(() => questions.value[currentIndex.value] || {});
const qTypeTag = computed(() => ({ "单选": "", "多选": "success", "判断": "warning", "填空": "info", "简答": "danger" }[currentQuestion.value.type] || ""));
const progressPercent = computed(() => ((currentIndex.value + 1) / questions.value.length) * 100);
const qBadgeClass = computed(() => {
  const m = { '单选': 'single', '多选': 'multiple', '判断': 'judge', '填空': 'fill', '简答': 'essay' };
  return m[currentQuestion.value.type] || '';
});

const answeredCount = computed(() => questions.value.filter((_, i) => isAnswered(i)).length);
const unansweredCount = computed(() => questions.value.length - answeredCount.value);
const unansweredIndex = computed(() => {
  for (let i = currentIndex.value + 1; i < questions.value.length; i++) {
    if (!isAnswered(i)) return i;
  }
  for (let i = 0; i < currentIndex.value; i++) {
    if (!isAnswered(i)) return i;
  }
  return -1;
});
const nextUnanswered = computed(() => unansweredIndex.value >= 0 ? unansweredIndex.value + 1 : 0);
const formattedTime = computed(() => { const m = Math.floor(remaining.value / 60); const s = remaining.value % 60; return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0"); });

function isAnswered(i) {
  const q = questions.value[i];
  const ans = answers.value[i];
  if (!ans) return false;
  if (q.type === "填空" || q.type === "简答") return ans.trim() !== "";
  if (q.type === "多选") return Array.isArray(ans) && ans.length > 0;
  return !!ans;
}

function selectOption(value) {
  answers.value[currentIndex.value] = value;
  if (practiceMode.value) {
    const q = currentQuestion.value;
    if (!q.id) return;
    let correct = value === q.answer;
    if (q.type === "判断" && q.options) {
      const j_map = Object.fromEntries(q.options.map(o => [o.label, o.text || o.label]));
      correct = j_map[value] === q.answer || value === q.answer;
    }
    const qid = String(q.id);
    practiceFeedback.value[qid] = { correct, correctAnswer: q.answer, userAnswer: value, explanation: q.explanation || "" };
    answeredLocked.value[currentIndex.value] = true;
  }
}
function toggleMulti(value) {
  const arr = answers.value[currentIndex.value] || [];
  const newArr = arr.includes(value) ? arr.filter(v => v !== value) : [...arr, value];
  answers.value[currentIndex.value] = newArr;
  multiSelected.value = newArr;
  if (practiceMode.value) {
    const q = currentQuestion.value;
    if (!q.id) return;
    const correctAnswer = q.answer;
    const ca = Array.isArray(correctAnswer) ? correctAnswer : (correctAnswer || "").startsWith("[") ? JSON.parse(correctAnswer) : [correctAnswer];
    const sortedCorrect = [...ca].sort().join(",");
    const sortedUser = [...newArr].sort().join(",");
    const correct = sortedUser === sortedCorrect;
    const qid = String(q.id);
    practiceFeedback.value[qid] = { correct, correctAnswer, userAnswer: newArr, explanation: q.explanation || "" };
    answeredLocked.value[currentIndex.value] = true;
  }
}

function updateAnswer() {
  const q = currentQuestion.value;
  if (q.type === "填空") answers.value[currentIndex.value] = blankAnswer.value;
  if (q.type === "简答") answers.value[currentIndex.value] = essayAnswer.value;
  if (practiceMode.value && q.id && (q.type === "填空" || q.type === "简答")) {
    const val = String(answers.value[currentIndex.value] || "").trim();
    if (!val) return;
    const correct = q.answer && val.toLowerCase() === String(q.answer).toLowerCase();
    const qid = String(q.id);
    practiceFeedback.value[qid] = { correct, correctAnswer: q.answer, userAnswer: val, explanation: q.explanation || "" };
    answeredLocked.value[currentIndex.value] = true;
  }
}
function saveCurrentAnswer() {
  const q = currentQuestion.value;
  if (q.type === "填空") answers.value[currentIndex.value] = blankAnswer.value;
  else if (q.type === "简答") answers.value[currentIndex.value] = essayAnswer.value;
}
function loadCurrentAnswer() {
  const q = currentQuestion.value;
  if (q.type === "多选") multiSelected.value = answers.value[currentIndex.value] || [];
  else if (q.type === "填空") blankAnswer.value = answers.value[currentIndex.value] || "";
  else if (q.type === "简答") essayAnswer.value = answers.value[currentIndex.value] || "";
  else multiSelected.value = [];
}
function goToNextUnanswered() {
  const idx = unansweredIndex.value;
  if (idx >= 0) goToQuestion(idx);
}
function goToQuestion(i) { saveCurrentAnswer(); currentIndex.value = i; loadCurrentAnswer(); saveState(); }
function prevQuestion() { saveCurrentAnswer(); if (currentIndex.value > 0) currentIndex.value--; loadCurrentAnswer(); saveState(); }
function nextQuestion() { saveCurrentAnswer(); if (currentIndex.value < questions.value.length - 1) currentIndex.value++; loadCurrentAnswer(); saveState(); }
function handleSubmit() { showSubmitConfirm.value = true; }

async function confirmSubmit() {
  clearInterval(timer);
  sessionStorage.removeItem("exam_" + route.params.id);
  try {
    const res = await api.answers.submit(paperId.value, { questions: questions.value, answers: Object.fromEntries(Object.entries(answers.value).map(([k, v]) => [String(questions.value[k]?.id), v])), duration_used: totalSeconds.value - remaining.value });
    showSubmitConfirm.value = false;
    const qs = questions.value;
    let correctCount = 0;
    let maxScore = 0;
    qs.forEach((q, i) => {
      const qid = String(q.id);
      const userAns = answers.value[i];
      maxScore += q.score || 2;
      const correct = res.detail?.[qid]?.correct;
      if (correct) correctCount++;
    });
    resultData.value = {
      score: res.score || 0,
      maxScore: maxScore,
      correctCount: correctCount,
      totalQuestions: qs.length,
      status: res.status === "已完成" ? "已完成" : "待批改",
      passed: maxScore > 0 && (res.score || 0) >= maxScore * examPassScore.value / 100
    };
    submitted.value = true;
    questionDetail.value = res.detail || {};
    showResult.value = true;
  } catch(e) {
    const msg = e?.response?.data?.detail || e?.message || "交卷失败";
    ElMessage.error("交卷失败: " + msg);
    console.error("Submit error:", e);
  }
}

function isOptionCorrect(label) {
  const q = currentQuestion.value;
  if (!submitted.value || !q.id) return false;
  const detail = questionDetail.value[String(q.id)];
  if (!detail) return false;
  if (q.type === "多选") {
    const ca = Array.isArray(detail.correctAnswer) ? detail.correctAnswer :
      detail.correctAnswer ? (detail.correctAnswer.startsWith("[") ? JSON.parse(detail.correctAnswer) : [detail.correctAnswer]) : [];
    return ca.includes(label);
  }
  return detail.correctAnswer === label;
}
function isOptionWrong(label) {
  const q = currentQuestion.value;
  if (!submitted.value || !q.id) return false;
  const detail = questionDetail.value[String(q.id)];
  if (!detail) return false;
  if (!detail.correct) {
    if (q.type === "多选") {
      const userAns = Array.isArray(detail.userAnswer) ? detail.userAnswer : [];
      return userAns.includes(label);
    }
    return detail.userAnswer === label;
  }
  return false;
}

function isPracticeCorrect(label) {
  if (!practiceMode.value) return false;
  const q = currentQuestion.value;
  if (!q.id) return false;
  const fb = practiceFeedback.value[String(q.id)];
  if (!fb) return false;
  if (q.type === "多选") {
    const ca = Array.isArray(fb.correctAnswer) ? fb.correctAnswer : (fb.correctAnswer || "").startsWith("[") ? JSON.parse(fb.correctAnswer) : [fb.correctAnswer];
    return ca.includes(label);
  }
  return fb.correctAnswer === label;
}
function isPracticeWrong(label) {
  if (!practiceMode.value) return false;
  const q = currentQuestion.value;
  if (!q.id) return false;
  const fb = practiceFeedback.value[String(q.id)];
  if (!fb) return false;
  if (fb.correct) return false;
  if (q.type === "多选") return (fb.userAnswer || []).includes(label);
  return fb.userAnswer === label;
}
const currentFeedback = computed(() => {
  if (!practiceMode.value) return null;
  const q = currentQuestion.value;
  if (!q.id) return null;
  return practiceFeedback.value[String(q.id)] || null;
});
function formatPracticeAnswer(answer) {
  if (!answer) return "";
  if (Array.isArray(answer)) return answer.join("、");
  return String(answer);
}

function handleVisibilityChange() {
  if (document.hidden) {
    switchCount.value++;
    saveState();
    if (switchCount.value >= maxSwitches) {
      ElMessage.warning("已超过最大切屏次数，系统将自动交卷");
      confirmSubmit();
    } else {
      ElMessage.warning("警告：切屏记录 (" + switchCount.value + "/" + maxSwitches + ")，超过会自动交卷");
    }
  }
}

function handleQuitConfirm() {
  ElMessageBox.confirm("确定要退出考试吗？未作答的题目将不会保存。", "退出确认", {
    confirmButtonText: "退出", cancelButtonText: "继续答题", type: "warning"
  }).then(() => {
    handleQuit();
  }).catch(() => {});
}

function handleQuit() { sessionStorage.removeItem("exam_" + route.params.id); router.push("/exams"); }

</script>>

<style scoped>
/* ── Container ── */
.take-exam {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #F5F4F0;
  overflow: hidden;
}

/* ── Top Bar ── */
.exam-topbar {
  display: flex;
  align-items: center;
  padding: 10px 24px;
  gap: 14px;
  background: #FFFFFF;
  border-bottom: 1px solid #E8E5DE;
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}
.exam-topbar::after {
  content: "";
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 1px;
  background: linear-gradient(90deg, transparent, #D4923A40, transparent);
}
.exam-topbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex-shrink: 0;
}
.back-btn {
  font-size: 13px !important;
  color: #6B7280 !important;
  padding: 5px 10px !important;
  border-radius: 6px !important;
  transition: all 0.2s !important;
}
.back-btn:hover {
  color: #1E3A5F !important;
  background: #E8EFF7 !important;
}
.topbar-divider {
  width: 1px;
  height: 20px;
  background: #E0DDD6;
  flex-shrink: 0;
}
.exam-name-tag {
  font-family: "Outfit", sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #1A1D23;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}
.exam-topbar-center {
  flex: 1;
  min-width: 0;
  max-width: 380px;
}
.progress-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.progress-text {
  font-size: 12px;
  font-weight: 600;
  color: #9CA3AF;
  white-space: nowrap;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}
.progress-bar { flex: 1; min-width: 60px; }
.progress-bar :deep(.el-progress-bar__outer) {
  background: #EBE9E3;
}
.progress-bar :deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, #1E3A5F, #2B4F7A);
}
.exam-topbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}
.timer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: "Outfit", sans-serif;
  font-size: 17px;
  font-weight: 700;
  color: #1A1D23;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  padding: 4px 12px;
  background: #F8F7F3;
  border-radius: 8px;
  border: 1px solid #EBE9E3;
}
.timer .el-icon { font-size: 16px; color: #D4923A; }
.timer.warning {
  color: #DC2626;
  border-color: #FECACA;
  background: #FEF2F2;
}
.timer.warning .el-icon { color: #DC2626; }
.submit-btn {
  border-radius: 8px !important;
  padding: 7px 18px !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
}

/* ── Body ── */
.exam-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

/* ── Question Panel ── */
.question-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 32px 36px 20px;
  overflow-y: auto;
  min-width: 0;
}
.question-card {
  width: 100%;
  max-width: 740px;
  margin: 0 auto;
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* ── Question Header ── */
.q-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
  flex-shrink: 0;
}
.q-number {
  font-family: "Outfit", sans-serif;
  font-size: 13px;
  color: #9CA3AF;
  font-weight: 500;
  letter-spacing: 0.03em;
}
.q-type-badge {
  font-family: "Outfit", sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  padding: 3px 10px;
  border-radius: 4px;
  text-transform: uppercase;
}
.q-type-badge.single { background: #E8EFF7; color: #1E3A5F; }
.q-type-badge.multiple { background: #ECFDF5; color: #059669; }
.q-type-badge.judge { background: #FFFBEB; color: #D97706; }
.q-type-badge.fill { background: #EFF6FF; color: #2563EB; }
.q-type-badge.essay { background: #FEF2F2; color: #DC2626; }

.q-score-badge {
  margin-left: auto;
  font-family: "Outfit", sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: #1E3A5F;
  background: linear-gradient(135deg, #E8EFF7, #F5F8FC);
  padding: 3px 14px;
  border-radius: 20px;
  border: 1px solid #D0DCEB;
  flex-shrink: 0;
}

/* ── Question Content ── */
.q-content-wrapper {
  position: relative;
  margin: 16px 0 24px;
  flex-shrink: 0;
}
.q-content {
  font-size: 17px;
  line-height: 1.75;
  color: #1A1D23;
  font-weight: 500;
  margin: 0;
  padding: 20px 24px;
  background: #FFFFFF;
  border-radius: 12px;
  border: 1px solid #E8E5DE;
  box-shadow: 0 1px 3px rgba(13,29,51,0.04);
  position: relative;
}
.q-content::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #1E3A5F, #D4923A);
  border-radius: 3px 0 0 3px;
}

/* ── Options ── */
.q-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}
.q-option {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: #FFFFFF;
  border: 1.5px solid #EBE9E3;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(13,29,51,0.02);
}
.q-option:hover {
  border-color: #1E3A5F60;
  background: #FAF9F6;
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(13,29,51,0.05);
}
.q-option:active {
  transform: translateY(0);
}
.q-option.selected {
  border-color: #1E3A5F;
  background: #F5F8FC;
  box-shadow: 0 0 0 3px #E8EFF7;
}
.q-option.correct {
  border-color: #059669;
  background: #F0FDF8;
  box-shadow: 0 0 0 3px rgba(5,150,105,0.1);
}
.q-option.wrong {
  border-color: #DC2626;
  background: #FEF5F5;
  box-shadow: 0 0 0 3px rgba(220,38,38,0.08);
}
.q-option.locked { pointer-events: none; opacity: 0.85; }

.option-marker {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid #D0D0C8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;
  font-size: 11px;
  font-weight: 700;
  color: transparent;
}
.option-marker.multi { border-radius: 5px; }
.q-option.selected .option-marker {
  border-color: #1E3A5F;
  background: #1E3A5F;
  color: #FFFFFF;
}
.q-option.correct .option-marker {
  border-color: #059669;
  background: #059669;
  color: #FFFFFF;
}
.q-option.wrong .option-marker {
  border-color: #DC2626;
  background: #DC2626;
  color: #FFFFFF;
}

.option-label {
  font-family: "Outfit", sans-serif;
  font-weight: 700;
  font-size: 14px;
  color: #1A1D23;
  min-width: 20px;
  flex-shrink: 0;
}
.option-text {
  font-size: 14px;
  color: #4B5563;
  word-break: break-word;
  line-height: 1.5;
}

/* ── Text Inputs ── */
.q-blank { margin-top: 8px; flex-shrink: 0; }

/* ── Navigation ── */
.q-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0 0;
  margin-top: auto;
  border-top: 1px solid #E8E5DE;
  flex-shrink: 0;
}
.q-nav-btn {
  border-radius: 8px !important;
  font-weight: 600 !important;
}

/* ── Navigator Sidebar ── */
.question-navigator {
  width: 210px;
  min-width: 170px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 24px 18px;
  border-left: 1px solid #E8E5DE;
  background: #FFFFFF;
  overflow-y: auto;
}
.nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.nav-title {
  font-family: "Outfit", sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: #1A1D23;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
.nav-count {
  font-family: "Outfit", sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #9CA3AF;
  background: #F1F0EC;
  padding: 2px 10px;
  border-radius: 10px;
}
.nav-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
  margin-bottom: 14px;
}
.nav-dot {
  aspect-ratio: 1;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: "Outfit", sans-serif;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.nav-dot.active {
  background: #1E3A5F;
  color: #FFFFFF;
  box-shadow: 0 0 0 3px #E8EFF7;
}
.nav-dot.answered {
  background: #E8EFF7;
  color: #1E3A5F;
}
.nav-dot.unanswered {
  background: #F1F0EC;
  color: #9CA3AF;
  border: 1px solid #E0DDD6;
}
.nav-dot.unanswered:hover {
  border-color: #1E3A5F80;
  color: #1E3A5F;
}
.nav-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: #6B7280;
}
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}
.legend-dot.answered { background: #E8EFF7; }
.legend-dot.unanswered { background: #F1F0EC; border: 1px solid #E0DDD6; }
.legend-dot.active { background: #1E3A5F; }

.nav-jump-btn {
  width: 100% !important;
  border-radius: 8px !important;
  font-size: 12px !important;
  padding: 8px 12px !important;
}

/* ── Practice Feedback ── */
.practice-feedback {
  margin-top: 20px;
  padding: 18px 20px;
  border-radius: 12px;
  background: #FFFFFF;
  border: 1px solid #E8E5DE;
  box-shadow: 0 2px 8px rgba(13,29,51,0.04);
  animation: feedbackIn 0.35s ease;
  flex-shrink: 0;
}
.practice-feedback .pf-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "Outfit", sans-serif;
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #F1F0EC;
}
.practice-feedback .pf-header.correct { color: #059669; }
.practice-feedback .pf-header.wrong { color: #DC2626; }
.practice-feedback .pf-row {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.6;
}
.practice-feedback .pf-lbl { font-weight: 600; color: #1A1D23; }
.practice-feedback .pf-val { color: #6B7280; }

/* ── Result Dialog ── */
.result-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 16px 0;
}
.result-hero {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 24px rgba(5,150,105,0.2);
}
.result-hero.passed { background: linear-gradient(135deg, #059669, #34D399); box-shadow: 0 8px 24px rgba(5,150,105,0.2); }
.result-hero:not(.passed) { background: linear-gradient(135deg, #DC2626, #F87171); box-shadow: 0 8px 24px rgba(220,38,38,0.15); }
.result-score {
  font-family: "Outfit", sans-serif;
  font-size: 38px;
  font-weight: 700;
  line-height: 1;
}
.result-label { font-size: 13px; opacity: 0.8; margin-top: 4px; }
.result-stats {
  display: flex;
  gap: 24px;
  width: 100%;
  justify-content: center;
}
.result-stat-item { text-align: center; }
.result-stat-item .rs-value {
  display: block;
  font-family: "Outfit", sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #1A1D23;
}
.result-stat-item .rs-label { font-size: 12px; color: #9CA3AF; }

.submit-summary { text-align: center; line-height: 2.2; font-size: 15px; }

/* ── Transitions ── */
.slide-q-enter-active,
.slide-q-leave-active {
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
}
.slide-q-enter-from { opacity: 0; transform: translateX(24px); }
.slide-q-leave-to { opacity: 0; transform: translateX(-24px); }

@keyframes feedbackIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .question-navigator { display: none; }
  .question-panel { padding: 20px; }
}
@media (max-width: 600px) {
  .exam-topbar { padding: 8px 12px; gap: 8px; }
  .exam-topbar-center { display: none; }
  .exam-name-tag { max-width: 100px; }
  .question-panel { padding: 16px; }
}
</style>