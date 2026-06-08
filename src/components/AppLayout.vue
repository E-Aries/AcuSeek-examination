<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-brand">
        <div class="brand-icon" :class="{ 'has-logo': !!brandNavLogo }">
          <img v-if="brandNavLogo" :src="brandNavLogo" class="sidebar-logo-img" alt="logo" />
          <svg v-else viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
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
          <span v-show="!sidebarCollapsed" class="brand-text">{{ brandSiteName }}</span>
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
        <el-menu-item v-if="userRole === 'admin'" index="/dashboard">
          <el-icon><Grid /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-menu-item v-if="userRole === 'admin'" index="/questions">
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
        <el-menu-item v-if="userRole === 'admin'" index="/categories">
          <el-icon><Collection /></el-icon>
          <template #title>分类管理</template>
        </el-menu-item>
        <el-menu-item v-if="userRole === 'admin'" index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item v-if="userRole === 'admin'" index="/logs">
          <el-icon><List /></el-icon>
          <template #title>操作日志</template>
        </el-menu-item>
        <el-menu-item v-if="userRole === 'admin'" index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>

      <!-- Brand info -->
      <div class="sidebar-info" v-show="!sidebarCollapsed">
        <div class="sidebar-copy" v-if="brandCopyright">{{ brandCopyright }}</div>
        <div class="sidebar-version" v-if="brandVersion">{{ brandVersion }}</div>
      </div>
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
            <el-button text class="topbar-btn" @click="handleBell">
              <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="bell-badge">
                <Bell style="width: 20px; height: 20px" />
              </el-badge>
            </el-button>
          </el-tooltip>
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="34" class="user-avatar" :style="{ background: avatarColor }">{{ avatarText }}</el-avatar>
              <span class="user-name">{{ userName }}</span>
              <el-icon class="user-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人资料
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
            <keep-alive :include="keepAlivePages">
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { api } from "../api.js";
import { useRoute, useRouter } from "vue-router";
import { Bell, ArrowDown, Fold, Expand } from "@element-plus/icons-vue";

const route = useRoute();
const keepAlivePages = ["Exams", "Questions", "Results", "Dashboard", "Users", "Categories", "Logs", "Settings", "Profile"];
const router = useRouter();
const brandNavLogo = ref("");
const brandSiteName = ref("硕讯科技");
const brandCopyright = ref("");
const brandVersion = ref("");
const unreadCount = ref(0);
const sidebarCollapsed = ref(false);

const userRole = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem("user") || "{}");
    return u.role || "admin";
  } catch(e) { return "admin"; }
});

const avatarColors = ["#409EFF","#67C23A","#E6A23C","#F56C6C","#909399","#B37FEB","#36CFC9","#F2A6B3"];
const avatarText = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem("user") || "{}");
    return (u.name || "管")[0];
  } catch { return "管"; }
});
const avatarColor = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem("user") || "{}");
    const name = u.name || "管理员";
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return avatarColors[Math.abs(hash) % avatarColors.length];
  } catch { return "#409EFF"; }
});

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
  Categories: "分类管理",
  Users: "用户管理",
  Logs: "操作日志",
  Settings: "系统设置",
  Profile: "个人资料",
  Notifications: "通知中心"
};

const pageTitle = computed(() => routeTitles[route.name] || "硕讯科技");
const activeRoute = computed(() => {
  const path = route.path;
  if (path.startsWith("/exams")) return "/exams";
  if (path.startsWith("/results")) return "/results";
  if (path.startsWith("/questions")) return "/questions";
  return "/dashboard";
});

async function loadBrand() {
  try {
    const res = await api.settings.get();
    if (res && res.nav_logo_url) {
      brandNavLogo.value = res.nav_logo_url;
    }
    if (res && res.site_name) brandSiteName.value = res.site_name;
    if (res && res.copyright_text) brandCopyright.value = res.copyright_text;
    if (res && res.version_text) brandVersion.value = res.version_text;
  } catch(e) {}
}
onMounted(loadBrand);

async function handleBell() {
  try {
    const res = await api.notifications.list();
    if (res.items && res.items.length > 0) {
      const msgs = res.items.map(n => n.title + ": " + n.content).join("\n");
      ElMessageBox.alert(msgs, "通知", { confirmButtonText: "知道了" });
    } else {
      ElMessage.info("暂无通知");
    }
  } catch(e) {
    ElMessage.error("获取通知失败");
  }
}

function handleUserCommand(cmd) {
  if (cmd === "logout") {
    localStorage.removeItem("token");
    router.push({ name: "Login" });
  } else if (cmd === "profile") {
    router.push({ name: "Profile" });
  }
}
async function loadUnreadCount() {
  try {
    const res = await api.notifications.unread();
    unreadCount.value = res.count || 0;
  } catch(e) {}
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: var(--c-bg);
}

/* 側边栏 - 深色主题 */
.sidebar {
  width: var(--c-sidebar-width);
  background: var(--c-sidebar-bg);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-base);
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
  overflow: hidden;
}
.sidebar.collapsed {
  width: var(--c-sidebar-collapsed);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  border-bottom: 1px solid var(--c-sidebar-border);
  min-height: 64px;
}
.sidebar.collapsed .sidebar-brand {
  padding: 20px 12px;
  justify-content: center;
}
.brand-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--c-primary-light), var(--c-primary));
  border-radius: var(--radius-md);
  color: white;
}
.brand-icon.has-logo {
  width: auto;
  height: auto;
  background: transparent;
  border-radius: 0;
}
.brand-text {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 700;
  color: white;
  letter-spacing: 1.5px;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  padding: 8px 8px;
  border: none !important;
  background: transparent !important;
}
.sidebar-menu .el-menu-item {
  border-radius: var(--radius-sm);
  margin: 2px 0;
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 13px;
  height: 38px;
  line-height: 38px;
  color: var(--c-sidebar-text) !important;
  background: transparent !important;
  letter-spacing: 0.01em;
}
.sidebar-menu .el-menu-item:hover {
  background: var(--c-sidebar-hover) !important;
  color: var(--c-sidebar-active) !important;
}
.sidebar-menu .el-menu-item.is-active {
  background: var(--c-primary) !important;
  color: var(--c-sidebar-active) !important;
  font-weight: 600;
}
.sidebar-menu .el-menu-item .el-icon {
  font-size: 17px;
  margin-right: 8px;
}

.sidebar-info {
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
  font-size: 11px;
  color: rgba(255,255,255,0.55);
  line-height: 1.6;
  flex-shrink: 0;
  text-align: center;
}
.sidebar-copy { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sidebar-version { margin-top: 2px; opacity: 0.4; }
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--c-sidebar-border);
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}
.collapse-btn {
  color: var(--c-sidebar-text);
  font-size: 16px;
  background: transparent !important;
  border: none !important;
}
.collapse-btn:hover {
  color: var(--c-sidebar-active);
  background: var(--c-sidebar-hover) !important;
}

/* 主区域 */
.main-area {
  flex: 1;
  margin-left: var(--c-sidebar-width);
  transition: margin-left var(--transition-base);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.main-area.expanded {
  margin-left: var(--c-sidebar-collapsed);
}

/* 顶栏 - 简洁白底 */
.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  height: 60px;
  background: var(--c-surface);
  border-bottom: 1px solid var(--c-border-light);
}
.page-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--c-text);
  font-family: var(--font-display);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 4px;
}
.topbar-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  color: var(--c-text-secondary);
  background: transparent !important;
  border: none !important;
  display: flex;
  align-items: center;
  justify-content: center;
}
.topbar-btn:hover {
  background: var(--c-surface-hover) !important;
  color: var(--c-text);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 10px 2px 2px;
  border-radius: 999px;
  cursor: pointer;
  transition: background var(--transition-fast);
  margin-left: 4px;
}
.user-info:hover {
  background: var(--c-surface-hover);
}
.user-avatar {
  background: linear-gradient(135deg, var(--c-primary), var(--c-primary-dark));
  border: none;
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 12px;
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

/* 内容区 */
.content {
  flex: 1;
  padding: 24px 28px 32px;
}

/* 页面过渡 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all var(--transition-base);
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}

@media (max-width: 768px) {
  .sidebar {
    width: var(--c-sidebar-collapsed);
  }
  .sidebar .brand-text,
  .sidebar .el-menu-item span {
    display: none;
  }
  .main-area {
    margin-left: var(--c-sidebar-collapsed);
  }
  .topbar {
    padding: 0 16px;
  }
  .content {
    padding: 16px;
  }
}
.sidebar-logo-img {
  max-width: 36px;
  max-height: 36px;
  width: auto;
  height: auto;
  object-fit: contain;
}
</style>
