<template>
  <div class="login-page">
    <!-- Decorative Background -->
    <div class="login-bg">
      <div class="bg-grid"></div>
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
    </div>

    <div class="login-container">
      <!-- Left: Brand panel -->
      <div class="login-brand">
        <div class="brand-content">
          <div class="brand-icon-large">
            <svg viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg" class="axus-logo">
              <circle cx="36" cy="36" r="36" fill="url(#loginBrandGrad)"/>
              <circle cx="36" cy="36" r="33" stroke="white" stroke-opacity="0.12" stroke-width="0.8"/>
              <text x="36" y="41" text-anchor="middle" fill="white" font-family="'Outfit',sans-serif" font-weight="700" font-size="22" letter-spacing="2">AX</text>
              <line x1="22" y1="50" x2="50" y2="50" stroke="white" stroke-opacity="0.3" stroke-width="2" stroke-linecap="round"/>
              <text x="36" y="60" text-anchor="middle" fill="white" font-family="'Outfit',sans-serif" font-weight="500" font-size="9" letter-spacing="2" opacity="0.6">EST. 2024</text>
              <defs>
                <linearGradient id="loginBrandGrad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#0A6E73"/>
                  <stop offset="100%" stop-color="#043638"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="brand-title">AXUS</h1>
          <p class="brand-subtitle">天津硕讯科技有限公司</p>
          <p class="brand-desc">
            企业考核管理系统<br>
            高效 · 公正 · 智能
          </p>
          <div class="brand-features">
            <div class="feature-item">
              <el-icon><Select /></el-icon>
              <span>多种题型支持</span>
            </div>
            <div class="feature-item">
              <el-icon><Coin /></el-icon>
              <span>智能随机组卷</span>
            </div>
            <div class="feature-item">
              <el-icon><DataBoard /></el-icon>
              <span>多维数据分析</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Login form -->
      <div class="login-form-panel">
        <div class="form-container">
        <template v-if="!showRegister">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">请登录您的账号</p>
          </div>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                size="large"
                class="login-input"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                class="login-input"
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="remember">记住我</el-checkbox>
            </div>

            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              native-type="submit"
            >
              登 录
            </el-button>
          </el-form>
          <div style="text-align:center;margin-top:16px">
            <el-button text type="primary" size="small" @click="showRegister = !showRegister">{{ showRegister ? "返回登录" : "没有账号？注册" }}</el-button>
          </div>
        </template>

        <template v-else>
          <div class="form-header">
            <h2 class="form-title">注册账号</h2>
            <p class="form-subtitle">创建一个新的考生账号</p>
          </div>
          <el-form ref="registerRef" :model="registerForm" class="login-form" @submit.prevent="handleRegister">
            <el-form-item prop="username" :rules="[{ required: true, message: '请输入用户名' }]">
              <el-input v-model="registerForm.username" placeholder="用户名" :prefix-icon="User" size="large" />
            </el-form-item>
            <el-form-item prop="name">
              <el-input v-model="registerForm.name" placeholder="姓名（可选）" :prefix-icon="Edit" size="large" />
            </el-form-item>
            <el-form-item prop="password" :rules="[{ required: true, message: '\u8bf7\u8f93\u5165密码' }]">
              <el-input v-model="registerForm.password" type="password" placeholder="密码" :prefix-icon="Lock" size="large" show-password />
            </el-form-item>
            <el-button class="login-submit-btn" type="primary" size="large" native-type="submit" :loading="registerLoading" style="width:100%">注 册</el-button>
          </el-form>
          <div style="text-align:center;margin-top:16px">
            <el-button text type="primary" size="small" @click="showRegister = false">已有账号？登录</el-button>
          </div>
        </template>

        <div class="login-footer-content">
            <p class="login-footer-text">首次使用请联系管理员获取账号</p>
            <p class="login-company-name">© 天津硕讯科技有限公司</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { User, Lock, Edit, Select, Coin, DataBoard } from "@element-plus/icons-vue";
import { api } from "../api.js";
import { ElMessage } from "element-plus";

const router = useRouter();
const formRef = ref(null);
const registerRef = ref(null);
const showRegister = ref(false);
const registerLoading = ref(false);
const loading = ref(false);
const remember = ref(false);

const registerForm = reactive({ username: "", name: "", password: "" });

const form = reactive({
  username: "",
  password: "",
});

const rules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 2, max: 20, message: "长度在 2 到 20 个字符", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 3, max: 20, message: "长度在 3 到 20 个字符", trigger: "blur" },
  ],
};


async function handleRegister() {
  registerRef.value.validate(async (valid) => {
    if (!valid) return;
    registerLoading.value = true;
    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registerForm)
      });
      const data = await res.json();
      if (data.id) {
        ElMessage.success("注册成功，请登录");
        showRegister.value = false;
        registerForm.username = "";
        registerForm.name = "";
        registerForm.password = "";
      } else {
        ElMessage.error(data.detail || "注册失败");
      }
    } catch(e) { ElMessage.error("注册失败"); }
    registerLoading.value = false;
  });
}
async function handleLogin() {
  formRef.value.validate(async (valid) => {
    if (!valid) return;
    loading.value = true;
    try {
      const res = await api.auth.login(form.username, form.password);
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("user", JSON.stringify(res.user));
      loading.value = false;
      const target = res.user?.role === "admin" ? "Dashboard" : "Exams";
          router.push({ name: target });
    } catch (e) {
      loading.value = false;
      ElMessage.error("用户名或密码错误");
    }
  });
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: var(--c-bg);
}

/* ── Background Effects ── */
.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--c-border-light) 1px, transparent 1px),
    linear-gradient(90deg, var(--c-border-light) 1px, transparent 1px);
  background-size: 64px 64px;
  opacity: 0.4;
}
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}
.bg-orb-1 {
  width: 500px;
  height: 500px;
  background: var(--c-primary);
  top: -150px;
  right: -100px;
  animation: orb-float 12s ease-in-out infinite alternate;
}
.bg-orb-2 {
  width: 400px;
  height: 400px;
  background: var(--c-accent);
  bottom: -100px;
  left: -100px;
  animation: orb-float 10s ease-in-out infinite alternate-reverse;
}
@keyframes orb-float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(40px, 30px) scale(1.1); }
}

/* ── Container ── */
.login-container {
  display: flex;
  width: 880px;
  max-width: 95vw;
  min-height: 560px;
  background: var(--c-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

/* ── Brand Panel ── */
.login-brand {
  width: 380px;
  background: linear-gradient(135deg, var(--c-primary-deeper), var(--c-primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 36px;
  position: relative;
  overflow: hidden;
}
.login-brand::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 80%, rgba(255,255,255,0.08) 0%, transparent 60%);
}
.brand-content {
  position: relative;
  z-index: 1;
  color: white;
}
.brand-icon-large {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(8px);
  margin-bottom: 24px;
}
.brand-title {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 700;
  letter-spacing: 4px;
  margin-bottom: 8px;
}
.brand-subtitle {
  font-size: 15px;
  opacity: 0.8;
  margin-bottom: 24px;
  font-weight: 500;
}
.brand-desc {
  font-size: 13px;
  opacity: 0.6;
  line-height: 1.8;
  margin-bottom: 40px;
}
.brand-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  opacity: 0.75;
}
.feature-item .el-icon {
  font-size: 18px;
  opacity: 0.9;
}

/* ── Form Panel ── */
.login-form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}
.form-container {
  width: 100%;
  max-width: 340px;
}
.form-header {
  margin-bottom: 32px;
}
.form-title {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 6px;
}
.form-subtitle {
  font-size: 14px;
  color: var(--c-text-secondary);
}

.login-form {
  margin-bottom: 20px;
}
.login-input :deep(.el-input__wrapper) {
  padding: 2px 16px;
}
.login-input :deep(.el-input__inner) {
  height: 48px;
  font-size: 14px;
}
.login-input :deep(.el-input__prefix) {
  margin-right: 8px;
}
.login-input :deep(.el-input__prefix-inner) .el-icon {
  font-size: 18px;
  color: var(--c-text-tertiary);
}

.form-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}
.form-options :deep(.el-checkbox__label) {
  font-size: 13px;
  color: var(--c-text-secondary);
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  letter-spacing: 2px;
  border-radius: var(--radius-sm);
}


.login-footer-content {
  text-align: center;
}
.login-footer-text {
  font-size: 12px;
  color: var(--c-text-tertiary);
  margin: 0 0 6px;
}
.login-company-name {
  font-size: 11px;
  color: var(--c-text-tertiary);
  opacity: 0.6;
  margin: 0;
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* AXUS logo animation */
.axus-logo {
  animation: logo-float 3s ease-in-out infinite;
}
@keyframes logo-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}


@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    min-height: auto;
  }
  .login-brand {
    width: 100%;
    padding: 32px 24px;
    min-height: 200px;
  }
  .brand-icon-large {
    width: 56px;
    height: 56px;
    margin-bottom: 16px;
  }
  .brand-title {
    font-size: 28px;
  }
  .brand-features {
    display: none;
  }
  .login-form-panel {
    padding: 32px 24px;
  }
}
</style>