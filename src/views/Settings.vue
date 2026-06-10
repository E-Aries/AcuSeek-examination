<template>
  <div class="oem-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">系统设置</h2>
      </div>
    </div>

    <div class="oem-body">
      <!-- Left: form -->
      <div class="oem-form">
        <el-form label-position="top" size="default">

          <h3 class="section-title">文字定制</h3>

          <el-form-item label="系统全称">
            <el-input v-model="form.site_name" placeholder="企业考核系统" />
            <div class="form-tip">同步至浏览器标题、登录页、页面头部</div>
          </el-form-item>

          <el-form-item label="公司名称">
            <el-input v-model="form.company_name" placeholder="如：公司名称" />
            <div class="form-tip">显示在登录页副标题、导出文件页眉</div>
          </el-form-item>

          <el-form-item label="底部版权文字">
            <el-input v-model="form.copyright_text" placeholder="Copyright 2026" />
            <div class="form-tip">显示在每个页面底部</div>
          </el-form-item>

          <el-form-item label="版本说明">
            <el-input v-model="form.version_text" placeholder="v1.0.0" style="max-width:200px" />
          </el-form-item>

          <el-divider />
          <el-form-item>
            <el-button type="primary" @click="handleSave" :loading="saving" size="large">保存配置</el-button>
            <el-button type="danger" plain :icon="Refresh" @click="handleReset" size="large" style="margin-left:12px">一键还原默认</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Right: live preview -->
      <div class="oem-preview">
        <h3 class="section-title">实时预览</h3>
        <div class="preview-frame">
          <div class="pf-brand">
            <div class="pf-brand-title">{{ form.site_name || "" }}</div>
            <div class="pf-brand-sub" v-if="form.company_name">{{ form.company_name }}</div>
            <div class="pf-brand-desc">企业考核管理系统</div>
            <div class="pf-footer-info">
              <div class="pf-copyright" v-if="form.copyright_text">{{ form.copyright_text }}</div>
              <div class="pf-version" v-if="form.version_text">{{ form.version_text }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Refresh, Setting } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";

const form = ref({
  site_name: "企业考核系统",
  company_name: "武汉xx科技",

  copyright_text: "Copyright 2026@武汉XX有限公司",
  version_text: "v2.0.1",

});
const saving = ref(false);

async function loadSettings() {
  try {
    const res = await fetch("/api/settings", {
      headers: { Authorization: "Bearer " + localStorage.getItem("token") },
    });
    const data = await res.json();
    if (data.site_name) form.value.site_name = data.site_name;
    if (data.company_name) form.value.company_name = data.company_name;

    if (data.copyright_text) form.value.copyright_text = data.copyright_text;
    if (data.version_text) form.value.version_text = data.version_text;
  } catch (e) {}
}

async function handleSave() {
  saving.value = true;
  try {
    // 把相对路径转成完整 URL 再保存
    const saveData = { ...form.value };
    const fields = ["logo_url", "nav_logo_url", "favicon_url"];
    const apiOrigin = window.location.origin === "http://192.168.0.230:5173" ? "http://192.168.0.230:8000" : window.location.origin;
    fields.forEach(f => {
      if (saveData[f] && saveData[f].startsWith("/")) {
        saveData[f] = apiOrigin + saveData[f];
      }
    });
    const res = await fetch("/api/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + localStorage.getItem("token") },
      body: JSON.stringify(saveData),
    });
    if (!res.ok) throw new Error((await res.json()).detail || "保存失败");
    // Update page title
    document.title = form.value.site_name || "企业考核系统";
    ElMessage.success("保存成功，已全局生效");
  } catch (e) {
    ElMessage.error(e.message || "保存失败");
  }
  saving.value = false;
}

async function handleReset() {
  try {
    await ElMessageBox.confirm("确定恢复为系统默认品牌配置？此操作不可撤销。", "确认还原");
    const res = await fetch("/api/settings/reset", {
      method: "POST",
      headers: { Authorization: "Bearer " + localStorage.getItem("token") },
    });
    if (!res.ok) throw new Error("还原失败");
    await loadSettings();
    document.title = "企业考核系统";
    ElMessage.success("已恢复默认配置");
  } catch (e) {
    if (e !== "cancel") ElMessage.error("还原失败");
  }
}

onMounted(loadSettings);
</script>

<style scoped>
.oem-page { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.page-title { font-family: var(--font-display); font-size: 22px; font-weight: 700; color: var(--c-text); margin: 0; }
.page-subtitle { font-size: 13px; color: var(--c-text-secondary); margin-top: 4px; }

.oem-body { display: grid; grid-template-columns: 1fr 340px; gap: 24px; align-items: start; }

.oem-form { background: var(--c-surface); border-radius: var(--radius-lg); padding: 28px; border: 1px solid var(--c-border-light); }

.section-title { font-size: 15px; font-weight: 600; color: var(--c-text); margin: 0 0 16px; padding-top: 4px; }

.form-tip { font-size: 12px; color: var(--c-text-tertiary); margin-top: 4px; }

.upload-row { display: flex; gap: 8px; }
.upload-row .el-input { flex: 1; }

.preview-wrap { margin-top: 8px; }
.preview-img { border-radius: var(--radius-sm); object-fit: contain; border: 1px solid var(--c-border-light); }
.preview-img.lg { max-width: 320px; max-height: 120px; }
.preview-img.sm { max-width: 160px; max-height: 48px; }
.preview-img.favicon { width: 32px; height: 32px; }

/* Preview panel */
.oem-preview { position: sticky; top: 20px; }
.preview-frame { background: var(--c-surface); border-radius: var(--radius-lg); border: 1px solid var(--c-border-light); overflow: hidden; box-shadow: var(--shadow-md); }

.pf-brand { background: linear-gradient(135deg, var(--c-primary-deeper), var(--c-primary-dark)); padding: 40px 28px; text-align: center; color: white; min-height: 320px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.pf-brand-icon { margin-bottom: 16px; }
.pf-brand-logo { max-width: 400px; max-height: 160px; object-fit: contain; }
.pf-brand-svg { width: 64px; height: 64px; }
.pf-brand-title { font-size: 22px; font-weight: 700; letter-spacing: 2px; margin-bottom: 4px; }
.pf-brand-sub { font-size: 13px; opacity: 0.6; margin-bottom: 16px; }
.pf-brand-desc { font-size: 13px; opacity: 0.7; margin-bottom: 24px; }
.pf-footer-info { margin-top: auto; font-size: 11px; opacity: 0.5; }
.pf-copyright { margin-bottom: 2px; }
.pf-version { opacity: 0.6; }

@media (max-width: 960px) {
  .oem-body { grid-template-columns: 1fr; }
  .oem-preview { position: static; }
}
</style>
