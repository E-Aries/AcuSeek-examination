<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>系统设置</h2>
      <p class="page-subtitle">通用系统配置</p>
    </div>

    <div class="settings-card">
      <el-form label-position="top">
        <el-form-item label="系统名称">
          <el-input v-model="form.site_name" placeholder="AXUS 企业考核系统" />
        </el-form-item>
        <el-form-item label="默认及格分数线">
          <el-input-number v-model="form.default_pass_score" :min="0" :max="100" :step="5" />
          <span style="margin-left:8px;color:var(--c-text-secondary);font-size:13px">分</span>
        </el-form-item>
        <el-form-item label="最大切屏次数">
          <el-input-number v-model="form.max_switches" :min="0" :max="10" />
          <span style="margin-left:8px;color:var(--c-text-secondary);font-size:13px">次（0=不限制）</span>
        </el-form-item>
        <el-form-item label="考试时长（默认）">
          <el-input-number v-model="form.default_duration" :min="5" :max="180" :step="5" />
          <span style="margin-left:8px;color:var(--c-text-secondary);font-size:13px">分钟</span>
        </el-form-item>
        <el-divider />
        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存设置</el-button>
          <el-button @click="loadSettings">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { api } from "../api.js";
import { ElMessage } from "element-plus";

const form = ref({
  site_name: "AXUS 企业考核系统",
  default_pass_score: 60,
  max_switches: 3,
  default_duration: 60
});
const saving = ref(false);

async function loadSettings() {
  try {
    const res = await api.settings.get();
    if (res.site_name) form.value.site_name = res.site_name;
    if (res.default_pass_score) form.value.default_pass_score = parseInt(res.default_pass_score);
    if (res.max_switches) form.value.max_switches = parseInt(res.max_switches);
    if (res.default_duration) form.value.default_duration = parseInt(res.default_duration);
  } catch(e) {}
}

onMounted(loadSettings);

async function handleSave() {
  saving.value = true;
  try {
    await api.settings.update(form.value);
    ElMessage.success("保存成功");
  } catch(e) {
    ElMessage.error("保存失败");
  }
  saving.value = false;
}
</script>

<style scoped>
.settings-page { max-width: 600px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-family: var(--font-display); font-size: 20px; font-weight: 700; color: var(--c-text); margin: 0; }
.page-subtitle { font-size: 13px; color: var(--c-text-tertiary); margin-top: 4px; }
.settings-card { background: var(--c-surface); border-radius: var(--radius-lg); padding: 32px; box-shadow: var(--shadow-sm); border: 1px solid var(--c-border-light); }
</style>