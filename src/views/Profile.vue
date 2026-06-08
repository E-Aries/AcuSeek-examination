<!-- Author: 达咩 | 轻则 -->

<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人资料</h2>
      <p class="page-subtitle">修改个人信息和密码</p>
    </div>

    <div class="profile-card">
      <el-form :model="form" label-width="100px" label-position="top">
        <el-form-item label="用户名">
                    <el-input v-model="form.username" placeholder="请输入用户名" :disabled="userRole === 'admin'" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="form.department" placeholder="请输入部门" />
        </el-form-item>
        <el-divider />
        <el-form-item label="新密码">
          <el-input v-model="form.password" type="password" placeholder="留空则不修改" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存修改</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { api } from "../api.js";
import { ElMessage } from "element-plus";

const form = ref({ username: "", name: "", department: "", password: "" });
const saving = ref(false);
const userRole = ref("");

onMounted(async () => {
  try {
    const me = await api.auth.me();
    userRole.value = me.role || "";
    form.value.username = me.username || me.name || "";
    form.value.name = me.name || "";
    form.value.department = me.department || "";
  } catch(e) {
    // Fallback to local cache
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      form.value.username = user.name || "";
      form.value.name = user.name || "";
      form.value.department = user.department || "";
    } catch(e2) {}
  }
});

async function handleSave() {
  saving.value = true;
  try {
    const data = { username: form.value.username, name: form.value.name, department: form.value.department };
    if (form.value.password) data.password = form.value.password;
    await api.auth.profile(data);
    // Update local user cache
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    user.name = form.value.name;
    user.department = form.value.department;
    if (form.value.username) user.name = form.value.username;
    localStorage.setItem("user", JSON.stringify(user));
    ElMessage.success("保存成功");
    form.value.password = "";
  } catch(e) {
    ElMessage.error("保存失败");
  }
  saving.value = false;
}
</script>

<style scoped>
.profile-page { max-width: 600px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-family: var(--font-display); font-size: 20px; font-weight: 700; color: var(--c-text); margin: 0; }
.page-subtitle { font-size: 13px; color: var(--c-text-tertiary); margin-top: 4px; }
.profile-card { background: var(--c-surface); border-radius: var(--radius-lg); padding: 32px; box-shadow: var(--shadow-sm); border: 1px solid var(--c-border-light); }
</style>