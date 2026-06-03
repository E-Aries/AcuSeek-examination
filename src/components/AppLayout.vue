<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="20" fill="url(#brandGrad)"/>
            <circle cx="20" cy="20" r="18" stroke="white" stroke-opacity="0.15" stroke-width="0.5"/>
            <text x="20" y="23" text-anchor="middle" fill="white" font-family="'Outfit',sans-serif" font-weight="700" font-size="12" letter-spacing="1.5">AX</text>
            <line x1="13" y1="28" x2="27" y2="28" stroke="white" stroke-opacity="0.4" stroke-width="1.5" stroke-linecap="round"/>
            <text x="20" y="34" text-anchor="middle" fill="white" font-family="'Outfit',sans-serif" font-weight="500" font-size="5" letter-spacing="1">EST.</text>
            <defs>
              <linearGradient id="brandGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#0A6E73"/>
                <stop offset="100%" stop-color="#064244"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <transition name="fade-slide">
          <span v-show="!sidebarCollapsed" class="brand-text">硕讯科技</span>
        </transition>
      </div>

      <el-menu
        :default-active="activeRoute"
        :collapse="sidebarCollapsed"
        :router="true"
        class="sidebar-menu"
        background-color="transparent"
        text-color="var(--c-text-secondary)"
        active-text-color="var(--c-primary)"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Grid /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-menu-item index="/questions">
          <el-icon><Notebook /></el-icon>
          <template #title>题库管理</template>
        </el-menu-item>
        <el-menu-item index="/exams">
          <el-icon><EditPen /></el-icon>
          <template #title>考试管理</template>
        </el-menu-item>
        <el-menu-item index="/results">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>成绩查询</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-tooltip :content="sidebarCollapsed ? '展开侧栏' : '收起侧栏'" placement="right">
          <el-button
            :icon="sidebarCollapsed ? 'Expand' : 'Fold'"
            text
            class="collapse-btn"
            @click="sidebarCollapsed = !sidebarCollapsed"
          />
        </el-tooltip>
      </div>
    </aside>

    <!-- Main Area -->
    <div class="main-area" :class="{ expanded: sidebarCollapsed }">
      <!-- Top Bar -->
      <header class="topbar">
        <div class="topbar-left">
          <h2 class="page-title">{{ pageTitle }}</h2>
        </div>
        <div class="topbar-right">
          <el-tooltip content="通知" placement="bottom">
            <el-button :icon="Bell" text class="topbar-btn" @click="handleBell">
              <el-badge :value="3" :hidden="false" class="bell-badge">
                <Bell style="width: 20px; height: 20px" />
              </el-badge>
            </el-button>
          </el-tooltip>
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="34" class="user-avatar">管</el-avatar>
              <span class="user-name">{{ userName }}</span>
              <el-icon class="user-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人资料
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- Page Content -->
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Bell, ArrowDown, Fold, Expand } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const sidebarCollapsed = ref(false);

const userName = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem("user") || "{}");
    return u.name || "管理员";
  } catch { return "管理员"; }
});

const routeTitles = {
  Dashboard: "仪表盘",
  Questions: "题库管理",
  Exams: "考试管理",
  ExamDetail: "考试详情",
  TakeExam: "在线考试",
  Results: "成绩查询",
  ResultDetail: "成绩详情",
};

const pageTitle = computed(() => routeTitles[route.name] || "硕讯科技");
const activeRoute = computed(() => {
  const path = route.path;
  if (path.startsWith("/exams")) return "/exams";
  if (path.startsWith("/results")) return "/results";
  if (path.startsWith("/questions")) return "/questions";
  return "/dashboard";
});

function handleBell() {
  // Placeholder for notifications
}

function handleUserCommand(cmd) {
  if (cmd === "logout") {
    localStorage.removeItem("token");
    router.push({ name: "Login" });
  }
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ── */
.sidebar {
  width: 240px;
  background: var(--c-surface);
  border-right: 1px solid var(--c-border-light);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-base);
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
}
.sidebar.collapsed {
  width: 64px;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  border-bottom: 1px solid var(--c-border-light);
}
.sidebar.collapsed .sidebar-brand {
  padding: 24px 14px;
  justify-content: center;
}
.brand-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--c-primary), var(--c-primary-dark));
  border-radius: var(--radius-md);
  color: white;
  flex-shrink: 0;
}
.brand-text {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--c-text);
  letter-spacing: 2px;
}

.sidebar-menu {
  flex: 1;
  padding: 12px 8px;
  border: none !important;
}
.sidebar-menu .el-menu-item {
  border-radius: var(--radius-sm);
  margin: 2px 0;
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 14px;
  height: 42px;
  line-height: 42px;
}
.sidebar-menu .el-menu-item:hover {
  background: var(--c-primary-lighter);
}
.sidebar-menu .el-menu-item.is-active {
  background: var(--c-primary-lighter);
  color: var(--c-primary) !important;
  font-weight: 600;
}
.sidebar-menu .el-menu-item .el-icon {
  font-size: 18px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--c-border-light);
  display: flex;
  justify-content: center;
}
.collapse-btn {
  color: var(--c-text-tertiary);
  font-size: 18px;
}
.collapse-btn:hover {
  color: var(--c-text-secondary);
}

/* ── Main Area ── */
.main-area {
  flex: 1;
  margin-left: 240px;
  transition: margin-left var(--transition-base);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.main-area.expanded {
  margin-left: 64px;
}

/* ── Top Bar ── */
.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  background: rgba(246, 245, 243, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--c-border-light);
}
.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--c-text);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.topbar-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  color: var(--c-text-secondary);
}
.topbar-btn:hover {
  background: var(--c-primary-lighter);
  color: var(--c-primary);
}
.bell-badge {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px 4px 4px;
  border-radius: 999px;
  cursor: pointer;
  transition: background var(--transition-fast);
}
.user-info:hover {
  background: var(--c-primary-lighter);
}
.user-avatar {
  background: linear-gradient(135deg, var(--c-primary), var(--c-primary-dark));
  border: 2px solid var(--c-primary-lighter);
  font-family: var(--font-body);
  font-weight: 600;
}
.user-name {
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 13px;
  color: var(--c-text);
}
.user-arrow {
  font-size: 14px;
  color: var(--c-text-tertiary);
}

/* ── Content ── */
.content {
  flex: 1;
  padding: 24px 32px 32px;
}

/* ── Transitions ── */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all var(--transition-base);
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: all var(--transition-base);
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 768px) {
  .sidebar {
    width: 64px;
  }
  .sidebar .brand-text,
  .sidebar .el-menu-item span {
    display: none;
  }
  .main-area {
    margin-left: 64px;
  }
  .topbar {
    padding: 12px 16px;
  }
  .content {
    padding: 16px;
  }
}
</style>
