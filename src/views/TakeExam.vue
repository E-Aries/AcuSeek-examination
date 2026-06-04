<template>
  <div class="take-exam">
    <!-- Top bar: Timer + Progress -->
    <header class="exam-topbar">
      <div class="exam-topbar-left">
        <div class="exam-breadcrumb">
          <el-button text size="small" @click="handleQuit">退出考试</el-button>
          <el-icon><ArrowRight /></el-icon>
          <span class="exam-breadcrumb-name">{{ examName }}</span>
        </div>
      </div>
      <div class="exam-topbar-center">
        <div class="progress-info">
          <span class="progress-text">{{ currentIndex + 1 }} / {{ questions.length }}</span>
          <el-progress :percentage="progressPercent" :stroke-width="6" :show-text="false" class="progress-bar" />
        </div>
      </div>
      <div class="exam-topbar-right">
        <div class="timer" :class="{ warning: remaining < 300 }">
          <el-icon><Timer /></el-icon>
          <span>{{ formattedTime }}</span>
        </div>
        <div class="exam-name-tag">{{ examName }}</div>
        <el-button type="primary" size="small" @click="handleSubmit">交卷</el-button>
      </div>
    </header>

    <!-- Main area -->
    <div class="exam-body">
      <!-- Question panel -->
      <div class="question-panel">
        <transition name="slide-q" mode="out-in">
          <div class="question-card" :key="currentIndex">
            <div class="q-header">
              <el-tag :type="qTypeTag" size="small" effect="plain" class="q-badge">{{ currentQuestion.type }}</el-tag>
              <span class="q-number">第 {{ currentIndex + 1 }} 题</span>
              <span v-if="currentQuestion.score" class="q-score">{{ currentQuestion.score }} 分</span>
            </div>
            <p class="q-content">{{ currentQuestion.content }}</p>

            <!-- Options -->
            <div v-if="['单选','判断'].includes(currentQuestion.type)" class="q-options">
              <div
                v-for="(opt, i) in currentQuestion.options"
                :key="i"
                class="q-option"
                :class="{ selected: answers[currentIndex] === opt.label, correct: submitted && isOptionCorrect(opt.label), wrong: submitted && isOptionWrong(opt.label) }"
                @click="selectOption(opt.label)"
              >
                <div class="q-option-marker">
                  <div v-if="answers[currentIndex] === opt.label" class="marker-dot active"></div>
                  <div v-else class="marker-dot"></div>
                </div>
                <span class="q-option-label">{{ opt.label }}</span>
                <span class="q-option-text">{{ opt.text }}</span>
              </div>
            </div>

            <!-- Multiple choice -->
            <div v-if="currentQuestion.type === '多选'" class="q-options">
              <div
                v-for="(opt, i) in currentQuestion.options"
                :key="i"
                class="q-option"
                :class="{ selected: multiSelected.includes(opt.label), correct: submitted && isOptionCorrect(opt.label), wrong: submitted && isOptionWrong(opt.label) }"
                @click="toggleMulti(opt.label)"
              >
                <div class="q-option-marker multi">
                  <el-icon v-if="multiSelected.includes(opt.label)" :size="14"><Check /></el-icon>
                </div>
                <span class="q-option-label">{{ opt.label }}</span>
                <span class="q-option-text">{{ opt.text }}</span>
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
          </div>
        </transition>

        <!-- Navigation buttons -->
        <div class="q-nav">
          <el-button :disabled="currentIndex === 0" @click="prevQuestion" :icon="ArrowLeft">上一题</el-button>
          <el-button v-if="currentIndex < questions.length - 1" type="primary" @click="nextQuestion">下一题 <el-icon><ArrowRight /></el-icon></el-button>
          <el-button v-else type="success" @click="handleSubmit">完成作答</el-button>
        </div>
      </div>

      <!-- Question navigator sidebar -->
      <aside class="question-navigator">
        <h4 class="nav-title">答题卡</h4>
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
          <div class="legend-item"><div class="legend-dot answered"></div> 已答</div>
          <div class="legend-item"><div class="legend-dot unanswered"></div> 未答</div>
          <div class="legend-item"><div class="legend-dot active"></div> 当前</div>
        </div>
        <div class="nav-summary">
          已答 <strong>{{ answeredCount }}</strong> / {{ questions.length }} 题
        </div>
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
import { ArrowLeft, ArrowRight, Timer, Check } from "@element-plus/icons-vue";
import { api } from "../api.js";
import { ElMessage } from "element-plus";

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
const resultData = ref({ score: 0, maxScore: 0, correctCount: 0, totalQuestions: 0, status: "", passed: false });
const submitted = ref(false);
const questionDetail = ref({});
let timer = null;

onMounted(async () => {
  try {
    const [res, examRes] = await Promise.all([
      api.exams.start(route.params.id),
      api.exams.get(route.params.id)
    ]);
    paperId.value = res.paper_id;
    questions.value = (res.questions || []).slice(0, 10);
    examName.value = examRes.name || "考试进行中";
    remaining.value = (examRes.duration || 60) * 60;
    totalSeconds.value = remaining.value;
    timer = setInterval(() => { if (remaining.value > 0) remaining.value--; else { clearInterval(timer); confirmSubmit(); } }, 1000);
  } catch(e) { ElMessage.error("加载失败"); }
});

onUnmounted(() => { clearInterval(timer); });

const currentQuestion = computed(() => questions.value[currentIndex.value] || {});
const qTypeTag = computed(() => ({ "单选": "", "多选": "success", "判断": "warning", "填空": "info", "简答": "danger" }[currentQuestion.value.type] || ""));
const progressPercent = computed(() => ((currentIndex.value + 1) / questions.value.length) * 100);
const answeredCount = computed(() => questions.value.filter((_, i) => isAnswered(i)).length);
const formattedTime = computed(() => { const m = Math.floor(remaining.value / 60); const s = remaining.value % 60; return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0"); });

function isAnswered(i) {
  const q = questions.value[i];
  const ans = answers.value[i];
  if (!ans) return false;
  if (q.type === "填空" || q.type === "简答") return ans.trim() !== "";
  if (q.type === "多选") return Array.isArray(ans) && ans.length > 0;
  return !!ans;
}

function selectOption(value) { answers.value[currentIndex.value] = value; }
function toggleMulti(value) {
  const arr = answers.value[currentIndex.value] || [];
  const newArr = arr.includes(value) ? arr.filter(v => v !== value) : [...arr, value];
  answers.value[currentIndex.value] = newArr;
  multiSelected.value = newArr;
}

function updateAnswer() {
  const q = currentQuestion.value;
  if (q.type === "填空") answers.value[currentIndex.value] = blankAnswer.value;
  if (q.type === "简答") answers.value[currentIndex.value] = essayAnswer.value;
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
function goToQuestion(i) { saveCurrentAnswer(); currentIndex.value = i; loadCurrentAnswer(); }
function prevQuestion() { saveCurrentAnswer(); if (currentIndex.value > 0) currentIndex.value--; loadCurrentAnswer(); }
function nextQuestion() { saveCurrentAnswer(); if (currentIndex.value < questions.value.length - 1) currentIndex.value++; loadCurrentAnswer(); }
function handleSubmit() { showSubmitConfirm.value = true; }

async function confirmSubmit() {
  clearInterval(timer);
  try {
    const res = await api.answers.submit(paperId.value, { questions: questions.value, answers: Object.fromEntries(Object.entries(answers.value).map(([k, v]) => [String(questions.value[k]?.id), v])), duration_used: totalSeconds.value - remaining.value });
    showSubmitConfirm.value = false;
    // Calculate detailed results
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
      passed: (res.score || 0) >= (maxScore * 0.6)
    };
    submitted.value = true;
    questionDetail.value = res.detail || {};
    showResult.value = true;
  } catch(e) { ElMessage.error("交卷失败"); }
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

function handleQuit() { router.push("/exams"); }

</script>>

<style scoped>
.take-exam {
  min-height: calc(100vh - 64px - 56px);
  display: flex;
  flex-direction: column;
  margin: -24px -32px;
  background: var(--c-bg);
}

/* ── Top Bar ── */
.exam-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--c-surface);
  border-bottom: 1px solid var(--c-border-light);
  position: sticky;
  top: 0;
  z-index: 20;
  gap: 16px;
}
.exam-topbar-left { min-width: 0; }
.exam-breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--c-text-secondary);
}
.exam-breadcrumb-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
  color: var(--c-text);
  font-weight: 500;
}
.exam-topbar-center {
  flex: 1;
  max-width: 400px;
}
.progress-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.progress-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text-secondary);
  white-space: nowrap;
}
.progress-bar { flex: 1; }
.exam-name-tag {
  font-size: 13px;
  color: var(--c-text-secondary);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.exam-topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.timer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  color: var(--c-text);
  font-variant-numeric: tabular-nums;
}
.timer .el-icon { font-size: 18px; }
.timer.warning { color: var(--c-danger); }

/* ── Body ── */
.exam-body {
  flex: 1;
  display: flex;
  gap: 0;
  padding: 24px;
}

/* ── Question Panel ── */
.question-panel {
  flex: 1;
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.question-card {
  background: var(--c-surface);
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--c-border-light);
}
.q-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.q-number {
  font-size: 13px;
  color: var(--c-text-secondary);
  font-weight: 500;
}
.q-score {
  font-size: 12px;
  color: var(--c-text-tertiary);
  margin-left: auto;
}
.q-content {
  font-size: 15px;
  line-height: 1.7;
  color: var(--c-text);
  margin-bottom: 24px;
}

/* Options */
.q-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.q-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.q-option.correct {
  border-color: var(--c-success);
  background: var(--c-success-bg);
}
.q-option.correct .q-option-marker {
  border-color: var(--c-success);
  background: var(--c-success);
  color: white;
}
.q-option.wrong {
  border-color: var(--c-danger);
  background: var(--c-danger-bg);
}
.q-option.wrong .q-option-marker {
  border-color: var(--c-danger);
  background: var(--c-danger);
  color: white;
}
.q-option:hover {

  border-color: var(--c-primary-light);
  background: var(--c-primary-lighter);
}
.q-option.selected {
  border-color: var(--c-primary);
  background: var(--c-primary-lighter);
}
.q-option-marker {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid var(--c-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}
.q-option.selected .q-option-marker { border-color: var(--c-primary); }
.q-option-marker.multi {
  border-radius: 4px;
}
.q-option.selected .q-option-marker.multi {
  background: var(--c-primary);
  border-color: var(--c-primary);
  color: white;
}
.marker-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: transparent;
  transition: all var(--transition-fast);
}
.marker-dot.active { background: var(--c-primary); }

.q-option-label {
  font-weight: 600;
  font-size: 14px;
  color: var(--c-text);
  min-width: 20px;
}
.q-option-text {
  font-size: 14px;
  color: var(--c-text-secondary);
}

.q-blank { margin-top: 8px; }

/* Navigation */
.q-nav {
  display: flex;
  justify-content: space-between;
}

/* ── Navigator Sidebar ── */
.question-navigator {
  width: 180px;
  margin-left: 24px;
  flex-shrink: 0;
}
.nav-title {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 12px;
}
.nav-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
  margin-bottom: 16px;
}
.nav-dot {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.nav-dot.active {
  background: var(--c-primary);
  color: white;
  box-shadow: 0 0 0 3px var(--c-primary-lighter);
}
.nav-dot.answered {
  background: var(--c-primary-lighter);
  color: var(--c-primary);
}
.nav-dot.unanswered {
  background: var(--c-bg);
  color: var(--c-text-tertiary);
  border: 1px solid var(--c-border-light);
}
.nav-dot.unanswered:hover {
  border-color: var(--c-primary-light);
  color: var(--c-primary);
}

.nav-legend {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--c-text-secondary);
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}
.legend-dot.answered { background: var(--c-primary-lighter); }
.legend-dot.unanswered { background: var(--c-bg); border: 1px solid var(--c-border-light); }
.legend-dot.active { background: var(--c-primary); }

.nav-summary {
  text-align: center;
  font-size: 13px;
  color: var(--c-text-secondary);
  padding-top: 12px;
  border-top: 1px solid var(--c-border-light);
}

/* ── Transitions ── */
.slide-q-enter-active,
.slide-q-leave-active {
  transition: all var(--transition-base);
}
.slide-q-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.slide-q-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Score result dialog */
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
  background: linear-gradient(135deg, var(--c-success), #34D399);
  color: white;
}
.result-hero.passed {
  background: linear-gradient(135deg, var(--c-success), #34D399);
}
.result-hero:not(.passed) {
  background: linear-gradient(135deg, var(--c-danger), #F87171);
}
.result-score {
  font-family: var(--font-display);
  font-size: 40px;
  font-weight: 700;
  line-height: 1;
}
.result-label {
  font-size: 14px;
  opacity: 0.8;
  margin-top: 4px;
}
.result-stats {
  display: flex;
  gap: 24px;
  width: 100%;
  justify-content: center;
}
.result-stat-item {
  text-align: center;
}
.result-stat-item .rs-value {
  display: block;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--c-text);
}
.result-stat-item .rs-label {
  font-size: 12px;
  color: var(--c-text-tertiary);
}

@media (max-width: 768px) {
  .exam-body { flex-direction: column; }
  .question-navigator {
    width: 100%;
    margin-left: 0;
    margin-top: 16px;
  }
  .nav-grid { grid-template-columns: repeat(8, 1fr); }
}
</style>
