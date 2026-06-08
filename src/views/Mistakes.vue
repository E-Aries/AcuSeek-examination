<template>
  <div class="mistakes-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">错题本</h2>
        <p class="page-subtitle">收集你在所有考试中做错的题目，巩固薄弱知识点</p>
      </div>
      <div class="header-actions">
        <el-tag type="danger" size="large" effect="plain" class="count-tag">
          共 {{ mistakes.length }} 道错题
        </el-tag>
        <el-button v-if="mistakes.length > 0" type="primary" :icon="CaretRight" @click="startPractice">练习错题</el-button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <el-select v-model="filterType" placeholder="题型" clearable size="small" style="width: 110px">
        <el-option label="单选" value="单选" />
        <el-option label="多选" value="多选" />
        <el-option label="判断" value="判断" />
        <el-option label="填空" value="填空" />
      </el-select>
      <el-select v-model="filterCategory" placeholder="分类" clearable size="small" style="width: 120px">
        <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
      </el-select>
    </div>

    <!-- Mistake cards -->
    <div v-if="filteredMistakes.length === 0" class="empty-state">
      <el-icon :size="48"><CircleCheck /></el-icon>
      <h3>暂无错题</h3>
      <p>继续保持！</p>
    </div>

    <div v-else class="mistake-list">
      <div v-for="(item, i) in filteredMistakes" :key="item.id" class="mistake-card" :class="{ expanded: expandedId === i }">
        <div class="mistake-header" @click="expandedId = expandedId === i ? null : i">
          <div class="mistake-meta">
            <el-tag size="small">{{ item.type }}</el-tag>
            <el-tag v-if="item.category" size="small" type="info">{{ item.category }}</el-tag>
            <span class="mistake-exam-label" v-if="item.exam_name">来自：{{ item.exam_name }}</span>
          </div>
          <div class="mistake-score-badge" :class="item.score >= 3 ? 'hard' : 'easy'">{{ item.score }}分</div>
        </div>

        <div class="mistake-body">
          <div class="mistake-content">{{ item.content }}</div>

          <!-- Options -->
          <div v-if="item.options && item.options.length" class="mistake-options">
            <div v-for="opt in item.options" :key="opt.label"
              class="mistake-option"
              :class="{
                correct: isCorrectAnswer(item, opt.label),
                wrong: isUserAnswer(item, opt.label),
                dim: !isCorrectAnswer(item, opt.label) && !isUserAnswer(item, opt.label)
              }">
              <span class="mo-label">{{ opt.label }}.</span>
              <span class="mo-text">{{ opt.text }}</span>
              <el-icon v-if="isCorrectAnswer(item, opt.label)" style="color:var(--c-success)"><CircleCheck /></el-icon>
              <el-icon v-else-if="isUserAnswer(item, opt.label)" style="color:var(--c-danger)"><CloseBold /></el-icon>
            </div>
          </div>

          <!-- Answer/Explanation (shown when expanded) -->
          <transition name="expand">
            <div v-if="expandedId === i" class="mistake-detail">
              <div class="md-row">
                <span class="md-label">你的答案：</span>
                <span class="md-value wrong-text">{{ formatAnswer(item.user_answer, item.type) }}</span>
              </div>
              <div class="md-row">
                <span class="md-label">正确答案：</span>
                <span class="md-value correct-text">{{ formatAnswer(item.answer, item.type) }}</span>
              </div>
              <div v-if="item.explanation" class="md-row explanation">
                <span class="md-label">解析：</span>
                <p class="md-value">{{ item.explanation }}</p>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { CircleCheck, CloseBold, CaretRight } from "@element-plus/icons-vue";
import { api } from "../api.js";
import { ElMessage } from "element-plus";

const router = useRouter();
const mistakes = ref([]);
const categories = ref([]);
const expandedId = ref(null);
const filterType = ref("");
const filterCategory = ref("");

onMounted(async () => {
  try {
    const [mistakeRes, catRes] = await Promise.all([
      api.questions.mistakes(),
      api.categories.list()
    ]);
    mistakes.value = mistakeRes.items || [];
    categories.value = [...new Set((mistakeRes.items || []).map(m => m.category).filter(Boolean))];
  } catch(e) { console.error(e); }
});

const filteredMistakes = computed(() => {
  let list = mistakes.value;
  if (filterType.value) list = list.filter(m => m.type === filterType.value);
  if (filterCategory.value) list = list.filter(m => m.category === filterCategory.value);
  return list;
});

function isCorrectAnswer(item, label) {
  if (item.type === "多选") {
    try {
      const ca = JSON.parse(item.answer);
      return Array.isArray(ca) && ca.includes(label);
    } catch { return item.answer === label; }
  }
  return item.answer === label;
}

function isUserAnswer(item, label) {
  if (item.type === "多选") {
    return Array.isArray(item.user_answer) && item.user_answer.includes(label);
  }
  return item.user_answer === label;
}

function formatAnswer(ans, type) {
  if (type === "多选") {
    try {
      const arr = JSON.parse(ans);
      return Array.isArray(arr) ? arr.join(", ") : ans;
    } catch { return ans || "(未作答)"; }
  }
  return ans || "(未作答)";
}

function startPractice() {
  // Pick up to 10 random mistakes and go to take exam mode
  const pool = filteredMistakes.value;
  if (pool.length === 0) return;
  const selected = pool.sort(() => Math.random() - 0.5).slice(0, 10);
  // Store to session and go to practice page
  sessionStorage.setItem("mistake_practice", JSON.stringify(selected));
  router.push("/mistakes/practice");
}
</script>

<style scoped>
.mistakes-page { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.page-title { font-family: var(--font-display); font-size: 22px; font-weight: 700; color: var(--c-text); margin-bottom: 4px; }
.page-subtitle { font-size: 13px; color: var(--c-text-secondary); margin: 0; }
.header-actions { display: flex; align-items: center; gap: 10px; }
.count-tag { font-size: 15px; padding: 6px 16px; }

.filter-bar { display: flex; gap: 8px; }

.empty-state { text-align: center; padding: 80px 20px; color: var(--c-text-tertiary); }
.empty-state h3 { margin: 16px 0 8px; font-size: 18px; color: var(--c-text); }
.empty-state p { font-size: 14px; }
.empty-state .el-icon { color: var(--c-success); }

.mistake-list { display: flex; flex-direction: column; gap: 12px; }
.mistake-card { background: var(--c-surface); border-radius: var(--radius-lg); border: 1px solid var(--c-border-light); overflow: hidden; transition: all var(--transition-base); }
.mistake-card:hover { border-color: var(--c-danger-lighter); }
.mistake-card.expanded { border-color: var(--c-danger); box-shadow: var(--shadow-md); }

.mistake-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; cursor: pointer; }
.mistake-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.mistake-exam-label { font-size: 12px; color: var(--c-text-tertiary); margin-left: 4px; }
.mistake-score-badge { font-size: 12px; font-weight: 600; padding: 2px 10px; border-radius: 999px; }
.mistake-score-badge.easy { background: var(--c-warning-bg); color: var(--c-warning); }
.mistake-score-badge.hard { background: var(--c-danger-bg); color: var(--c-danger); }

.mistake-body { padding: 0 18px 14px; }
.mistake-content { font-size: 15px; line-height: 1.6; margin-bottom: 12px; }

.mistake-options { display: flex; flex-direction: column; gap: 6px; }
.mistake-option { display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: var(--radius-sm); transition: background 0.2s; }
.mistake-option.correct { background: var(--c-success-bg); }
.mistake-option.wrong { background: var(--c-danger-bg); }
.mistake-option.dim { opacity: 0.5; }
.mo-label { font-weight: 700; color: var(--c-text-secondary); flex-shrink: 0; }
.mo-text { flex: 1; }

.mistake-detail { margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--c-border-light); display: flex; flex-direction: column; gap: 6px; }
.md-row { display: flex; gap: 8px; font-size: 13px; }
.md-label { font-weight: 600; color: var(--c-text-secondary); flex-shrink: 0; min-width: 70px; }
.md-value { color: var(--c-text); }
.correct-text { color: var(--c-success); font-weight: 600; }
.wrong-text { color: var(--c-danger); font-weight: 600; }
.md-row.explanation { margin-top: 4px; }
.md-row.explanation .md-value { font-size: 13px; color: var(--c-text-secondary); line-height: 1.5; margin: 0; }

.expand-enter-active { transition: all 0.25s ease; max-height: 300px; opacity: 1; }
.expand-leave-active { transition: all 0.2s ease; max-height: 300px; opacity: 1; }
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; overflow: hidden; }

@media (max-width: 768px) {
  .page-header { flex-direction: column; }
  .header-actions { width: 100%; }
  .header-actions .count-tag { flex: 1; text-align: center; }
}
</style>