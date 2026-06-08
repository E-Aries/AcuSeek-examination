<!-- Author: 达咩 | 轻则 -->

<template>
  <div class="categories-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="showDialog = true">新增分类</el-button>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="categories" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="right" />
        <el-table-column prop="name" label="分类名称" min-width="200" />
        <el-table-column prop="sort" label="排序" width="80" align="center" />
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <span class="action-group">
              <el-button text size="small" :icon="Edit" @click="editCategory(row)" title="编辑" />
              <el-button text type="danger" size="small" :icon="Delete" @click="deleteCategory(row.id)" title="删除" />
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑分类' : '新增分类'" width="400px">
      <el-form label-position="top">
        <el-form-item label="分类名称">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Plus, Edit, Delete } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { api } from "../api.js";

const showDialog = ref(false);
const editingId = ref(null);
const categories = ref([]);
const form = ref({ name: "", sort: 0 });

async function loadCategories() {
  try {
    const res = await api.categories.list();
    categories.value = res.items || [];
  } catch(e) {
    ElMessage.error("加载分类失败");
  }
}

onMounted(loadCategories);

function editCategory(row) {
  editingId.value = row.id;
  form.value = { name: row.name, sort: row.sort };
  showDialog.value = true;
}

async function saveCategory() {
  if (!form.value.name.trim()) {
    ElMessage.warning("请输入分类名称");
    return;
  }
  try {
    if (editingId.value) {
      await api.categories.update(editingId.value, { name: form.value.name, sort: form.value.sort });
      ElMessage.success("更新成功");
    } else {
      await api.categories.create(form.value.name, form.value.sort);
      ElMessage.success("创建成功");
    }
    showDialog.value = false;
    editingId.value = null;
    form.value = { name: "", sort: 0 };
    loadCategories();
  } catch(e) {
    ElMessage.error("操作失败");
  }
}

async function deleteCategory(id) {
  try {
    await ElMessageBox.confirm("确定删除此分类？", "确认");
    await api.categories.delete(id);
    categories.value = categories.value.filter(c => c.id !== id);
    ElMessage.success("删除成功");
  } catch(e) {
    ElMessage.error(e.message || "操作失败");
  }
}
</script>

<style scoped>
.categories-page { display: flex; flex-direction: column; gap: 16px; }
.toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.toolbar-left { display: flex; gap: 8px; }
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
