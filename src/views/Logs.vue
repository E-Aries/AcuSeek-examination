<template>
  <div class="logs-page">
    <div class="toolbar">
      <h2 class="page-title">操作日志</h2>
      <div class="toolbar-right">
        <el-select v-model="filterAction" placeholder="操作类型" clearable size="small" style="width: 160px">
          <el-option v-for="a in actions" :key="a" :label="a" :value="a" />
        </el-select>
        <el-button :icon="Refresh" size="small" @click="loadLogs">刷新</el-button>
      </div>
    </div>

    <el-table :data="logs" stripe style="width: 100%" v-loading="loading" max-height="calc(100vh - 220px)">
      <el-table-column label="时间" width="160" prop="created_at" />
      <el-table-column label="用户" width="120" prop="username" />
      <el-table-column label="操作" width="150" prop="action" />
      <el-table-column label="目标" min-width="200" prop="target" />
      <el-table-column label="详情" min-width="300" prop="detail" show-overflow-tooltip />
      <el-table-column label="IP" width="140" prop="ip" />
    </el-table>

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
import { ref, onMounted } from "vue";
import { Refresh } from "@element-plus/icons-vue";
import { api } from "../api.js";

const logs = ref([]);
const actions = ref([]);
const filterAction = ref("");
const currentPage = ref(1);
const total = ref(0);
const loading = ref(false);

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
.toolbar { display: flex; align-items: center; justify-content: space-between; }
.page-title { font-family: var(--font-display); font-size: 20px; font-weight: 700; color: var(--c-text); margin: 0; }
.toolbar-right { display: flex; gap: 8px; align-items: center; }
.pagination-wrap { display: flex; justify-content: center; padding: 16px 0; }
</style>