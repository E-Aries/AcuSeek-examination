<template>
  <div class="logs-page">
    <!-- Header card -->
    <div class="logs-header">
      <div class="logs-header-left">
        <div class="logs-icon">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div>
          <h2 class="logs-title">操作日志</h2>
          <p class="logs-subtitle">审计记录查看</p>
        </div>
      </div>
      <div class="logs-header-right">
        <el-select v-model="filterAction" placeholder="操作类型" clearable size="default" style="width: 160px">
          <el-option v-for="a in actions" :key="a" :label="a" :value="a" />
        </el-select>
        <el-button type="primary" :icon="Refresh" @click="loadLogs">刷新</el-button>
      </div>
    </div>

    <!-- Stats row -->
    <div class="logs-stats">
      <div class="stat-item">
        <span class="stat-number">{{ total }}</span>
        <span class="stat-label">总记录</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ uniqueUsers }}</span>
        <span class="stat-label">操作用户</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ uniqueActions }}</span>
        <span class="stat-label">操作类型</span>
      </div>
    </div>

    <!-- Table card -->
    <div class="logs-table-wrap">
      <el-table :data="logs" stripe style="width: 100%" v-loading="loading"  size="small">
        <el-table-column label="时间" width="150" prop="created_at" />
        <el-table-column label="用户" width="90" prop="username" />
        <el-table-column label="操作" width="110" prop="action" />
        <el-table-column label="目标" min-width="120" prop="target" show-overflow-tooltip />
        <el-table-column label="详情" min-width="160" prop="detail" show-overflow-tooltip />
        <el-table-column label="IP" width="120" prop="ip" />
      </el-table>
    </div>

    <div class="pagination-wrap" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="50"
        :total="total"
        layout="prev, pager, next, total"
        @current-change="loadLogs"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { Refresh, Document } from "@element-plus/icons-vue";
import { api } from "../api.js";

const logs = ref([]);
const actions = ref([]);
const filterAction = ref("");
const currentPage = ref(1);
const total = ref(0);
const loading = ref(false);

const uniqueUsers = computed(() => {
  const users = new Set(logs.value.map(l => l.username).filter(Boolean));
  return users.size;
});
const uniqueActions = computed(() => {
  const acts = new Set(logs.value.map(l => l.action).filter(Boolean));
  return acts.size;
});

async function loadLogs() {
  loading.value = true;
  try {
    const params = { page: currentPage.value, size: 50 };
    if (filterAction.value) params.action = filterAction.value;
    const res = await api.logs.list(params);
    logs.value = res.items || [];
    total.value = res.total || 0;
  } catch(e) { logs.value = []; }
  loading.value = false;
}

onMounted(async () => {
  try {
    const res = await api.logs.actions();
    actions.value = res.items || [];
  } catch(e) {}
  await loadLogs();
});
</script>

<style scoped>
.logs-page { display: flex; flex-direction: column; gap: 16px; }

/* Header card */
.logs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--c-surface);
  border: 1px solid var(--c-border-light);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
}
.logs-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.logs-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--c-primary-lighter);
  border-radius: var(--radius-md);
  color: var(--c-primary);
}
.logs-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  color: var(--c-text);
  margin: 0;
}
.logs-subtitle {
  font-size: 12px;
  color: var(--c-text-tertiary);
  margin: 2px 0 0;
}
.logs-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Stats */
.logs-stats {
  display: flex;
  gap: 12px;
}
.stat-item {
  flex: 1;
  background: var(--c-surface);
  border: 1px solid var(--c-border-light);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-primary);
  font-family: var(--font-display);
}
.stat-label {
  font-size: 12px;
  color: var(--c-text-tertiary);
}

/* Table */
.logs-table-wrap {
  background: var(--c-surface);
  border: 1px solid var(--c-border-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 8px 0 4px;
}
</style>
