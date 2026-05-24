<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

interface DocItem { id: string; title: string; category: string; tags: string; content: string; created_at: string }

const docs = ref<DocItem[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const form = ref({ title: '', category: '通用', tags: '', content: '' })
const searchQuery = ref('')
const filterCategory = ref('')
const viewDoc = ref<DocItem | null>(null)

const categories = ['通用', '安全管理', '学风管理', '心理健康', '资助管理', '就业指导', '党团建设', '规章制度']

async function fetchDocs() {
  loading.value = true
  try {
    const resp = await axios.get('/api/documents', {
      params: { category: filterCategory.value || undefined, search: searchQuery.value || undefined }
    })
    docs.value = resp.data
  } finally { loading.value = false }
}

function openCreate() {
  editingId.value = null
  form.value = { title: '', category: '通用', tags: '', content: '' }
  dialogVisible.value = true
}

function openEdit(doc: DocItem) {
  editingId.value = doc.id
  form.value = { title: doc.title, category: doc.category, tags: doc.tags, content: doc.content }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.title.trim() || !form.value.content.trim()) return
  if (editingId.value) {
    await axios.put(`/api/documents/${editingId.value}`, form.value)
    ElMessage.success('更新成功')
  } else {
    await axios.post('/api/documents', form.value)
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
  await fetchDocs()
}

async function handleDelete(id: string, title: string) {
  try {
    await ElMessageBox.confirm(`确定删除「${title}」吗？`, '确认删除', { type: 'warning' })
    await axios.delete(`/api/documents/${id}`)
    ElMessage.success('已删除')
    await fetchDocs()
  } catch { /* cancelled */ }
}

const showViewDialog = computed({
  get: () => viewDoc.value !== null,
  set: (v: boolean) => { if (!v) viewDoc.value = null },
})

onMounted(fetchDocs)
</script>

<template>
  <div class="kb-page">
    <header class="page-header">
      <h1>📚 知识库</h1>
      <p class="subtitle">管理政策文件、规章制度、工作指南等参考文档，AI 生成时将自动引用相关内容</p>
    </header>

    <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
      <el-select v-model="filterCategory" placeholder="分类筛选" clearable style="width:150px" @change="fetchDocs">
        <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
      </el-select>
      <el-input v-model="searchQuery" placeholder="搜索标题、内容或标签..." clearable style="width:280px"
        @keyup.enter="fetchDocs" @clear="fetchDocs" />
      <el-button @click="fetchDocs">搜索</el-button>
      <div style="flex:1" />
      <el-button type="primary" @click="openCreate">+ 添加文档</el-button>
    </div>

    <el-table :data="docs" v-loading="loading" class="kb-table">
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="tags" label="标签" width="160" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="160" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="viewDoc = row">查看</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id, row.title)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑文档' : '添加文档'" width="600px">
      <el-form label-position="top">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="文档标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" style="width:100%">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tags" placeholder="用逗号分隔，例如：通知模板,防诈骗,安全教育" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="form.content" type="textarea" :rows="10" placeholder="知识库文档内容..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- View Dialog -->
    <el-dialog v-model="showViewDialog" :title="viewDoc?.title" width="700px" @close="viewDoc = null">
      <div v-if="viewDoc">
        <div style="margin-bottom:12px;color:#909399;font-size:13px">
          <el-tag size="small">{{ viewDoc.category }}</el-tag>
          <span v-if="viewDoc.tags" style="margin-left:8px">标签：{{ viewDoc.tags }}</span>
        </div>
        <div style="white-space:pre-wrap;line-height:1.8;font-size:14px;color:#303133;max-height:500px;overflow-y:auto">{{ viewDoc.content }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.kb-page { max-width: 1100px; margin: 0 auto; padding: 28px 24px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 26px; color: #4a7c6f; margin: 0 0 6px 0; font-weight: 700; }
.subtitle { color: #909399; font-size: 14px; margin: 0; }
.kb-table { border-radius: 12px; overflow: hidden; }
</style>
