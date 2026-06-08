<template>
  <div class="users-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="showDialog = true">新增用户</el-button>
      </div>
      <div class="toolbar-right">
        <el-input v-model="search" placeholder="搜索用户名..." clearable :prefix-icon="Search" class="search-input" />
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="filteredUsers" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="right" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="department" label="部门" width="150" />
        <el-table-column label="角色" width="90">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'success'" size="small" effect="plain">
              {{ row.role === "admin" ? "管理员" : "考生" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <span class="action-group">
              <el-button text size="small" :icon="Edit" @click="editUser(row)" title="编辑" />
              <el-button text type="danger" size="small" :icon="Delete" @click="deleteUser(row.id)" title="删除" />
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑用户' : '新增用户'" width="420px">
      <el-form label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="登录用账号" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" :placeholder="editingId ? '留空不修改' : '请输入密码'" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="form.department" placeholder="所属部门" />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="form.role">
            <el-radio value="candidate">考生</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { Plus, Search, Edit, Delete } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";

const search = ref("");
const showDialog = ref(false);
const editingId = ref(null);
const users = ref([]);
const form = ref({ username: "", password: "", name: "", department: "", role: "candidate" });

const token = () => localStorage.getItem("token");
const headers = () => ({ "Authorization": "Bearer " + token(), "Content-Type": "application/json" });

async function loadUsers() {
  const res = await fetch("/api/users", { headers: headers() });
  const data = await res.json();
  users.value = data.items || [];
}

onMounted(loadUsers);

const filteredUsers = computed(() => {
  if (!search.value) return users.value;
  return users.value.filter(u => u.username.includes(search.value) || u.name.includes(search.value));
});

function editUser(row) {
  editingId.value = row.id;
  form.value = { username: row.username, password: "", name: row.name, department: row.department || "", role: row.role };
  showDialog.value = true;
}

async function saveUser() {
  const f = form.value;
  const body = JSON.stringify({ username: f.username, password: f.password || "123456", name: f.name || f.username, role: f.role || "candidate", department: f.department || "" });





  try {
    if (editingId.value) {
      await fetch("/api/users/" + editingId.value, { method: "PUT", headers: headers(), body: body });
      ElMessage.success("更新成功");
    } else {
      await fetch("/api/users", { method: "POST", headers: headers(), body: body });
      ElMessage.success("创建成功");
    }
    showDialog.value = false;
    editingId.value = null;
    form.value = { username: "", password: "", name: "", department: "", role: "candidate" };
    loadUsers();
  } catch(e) { console.error("新增用户失败:", e); ElMessage.error("操作失败: " + e.message); }
}

async function deleteUser(id) {
  try {
    await ElMessageBox.confirm("确定删除此用户？", "确认");
    await fetch("/api/users/" + id, { method: "DELETE", headers: headers() });
    users.value = users.value.filter(u => u.id !== id);
    ElMessage.success("删除成功");
  } catch(e) {}
}
</script>

<style scoped>
.users-page { display: flex; flex-direction: column; gap: 16px; }
.toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.toolbar-left { display: flex; gap: 8px; }
.search-input { width: 240px; }
.table-card { border-radius: var(--radius-lg); }
.action-group {
    display: inline-flex;
    align-items: center;
    gap: 0;
  }
  .action-group .el-button {
    margin-left: 0 !important;
    padding: 5px 4px !important;
    font-size: 15px;
  }
  .action-group .el-button:not(.el-button--danger) {
    --el-button-text-color: #6B7280;
  }
  .action-group .el-button:not(.el-button--danger):hover {
    --el-button-text-color: #1E3A5F;
  }
</style>