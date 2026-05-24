<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useStudentStore } from '../stores/student'
import type { StudentItem } from '../api/students'
import axios from 'axios'

const store = useStudentStore()

const filterClassId = ref('')
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('添加学生')
const editingId = ref<string | null>(null)

const showClassDialog = ref(false)
const newClassName = ref('')
const newClassGrade = ref('')
const newClassMajor = ref('')

const importing = ref(false)

function downloadTemplate() {
  window.open('/api/students/import/template', '_blank')
}

async function handleImportFile(options: any) {
  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    const resp = await axios.post('/api/students/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const data = resp.data
    ElMessage.success(`导入完成：成功 ${data.created} 条，跳过 ${data.skipped} 条`)
    if (data.errors.length > 0) {
      const msg = data.errors.slice(0, 5).map((e: any) => `第${e.row}行: ${e.error}`).join('; ')
      ElMessage.warning(`部分失败: ${msg}`)
    }
    store.fetchStudents()
    store.fetchClasses()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

const form = ref({ name: '', student_id: '', class_id: '', phone: '', risk_level: 'low' })

const riskOptions = [
  { label: '低风险', value: 'low' },
  { label: '中风险', value: 'medium' },
  { label: '高风险', value: 'high' },
]

function riskTagType(level: string) {
  if (level === 'low') return 'success'
  if (level === 'high') return 'danger'
  return 'warning'
}

function riskLabel(level: string) {
  if (level === 'low') return '低'
  if (level === 'high') return '高'
  return '中'
}

onMounted(() => {
  store.fetchClasses()
  store.fetchStudents()
})

function handleSearch() {
  store.fetchStudents(filterClassId.value || undefined, searchQuery.value || undefined)
}

function openCreate() {
  dialogTitle.value = '添加学生'
  editingId.value = null
  form.value = { name: '', student_id: '', class_id: '', phone: '', risk_level: 'low' }
  dialogVisible.value = true
}

function openEdit(student: StudentItem) {
  dialogTitle.value = '编辑学生'
  editingId.value = student.id
  form.value = {
    name: student.name,
    student_id: student.student_id,
    class_id: student.class_id || '',
    phone: student.phone,
    risk_level: student.risk_level,
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (editingId.value) {
    await store.editStudent(editingId.value, { ...form.value })
  } else {
    await store.addStudent({ ...form.value, class_id: form.value.class_id || null })
  }
  dialogVisible.value = false
}

async function handleDelete(id: string, name: string) {
  try {
    await ElMessageBox.confirm(`确定删除学生「${name}」吗？`, '确认删除', { type: 'warning' })
    await store.removeStudent(id)
  } catch { /* cancelled */ }
}

async function handleAddClass() {
  if (!newClassName.value.trim()) return
  await store.addClass(newClassName.value.trim(), newClassGrade.value.trim(), newClassMajor.value.trim())
  showClassDialog.value = false
  newClassName.value = ''
  newClassGrade.value = ''
  newClassMajor.value = ''
}
</script>

<template>
  <div class="student-page">
    <header class="page-header">
      <h1>📋 学生数据管理</h1>
      <p class="subtitle">管理学院学生基本信息，支持按班级筛选和姓名搜索</p>
    </header>

    <div class="filter-bar">
      <el-select v-model="filterClassId" placeholder="班级筛选" clearable style="width:200px" @change="handleSearch">
        <el-option v-for="c in store.classes" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-input v-model="searchQuery" placeholder="搜索姓名或学号..." clearable style="width:240px"
        @keyup.enter="handleSearch" @clear="handleSearch" />
      <el-button @click="handleSearch">搜索</el-button>
      <div style="flex:1" />
      <el-button type="primary" @click="openCreate">+ 添加学生</el-button>
      <el-button @click="showClassDialog = true">+ 添加班级</el-button>
      <el-upload
        :show-file-list="false"
        :auto-upload="false"
        accept=".xlsx,.xls"
        :on-change="handleImportFile"
      >
        <el-button :loading="importing">📥 导入 Excel</el-button>
      </el-upload>
      <el-button @click="downloadTemplate">📄 下载模板</el-button>
    </div>

    <el-table :data="store.students" v-loading="store.loading" class="student-table">
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="student_id" label="学号" width="140" />
      <el-table-column label="班级" width="180">
        <template #default="{ row }">
          {{ store.classes.find(c => c.id === row.class_id)?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机" width="160" />
      <el-table-column label="风险等级" width="120">
        <template #default="{ row }">
          <el-tag :type="riskTagType(row.risk_level)" size="small">{{ riskLabel(row.risk_level) }}风险</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id, row.name)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="480px">
      <el-form label-position="top">
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" placeholder="学生姓名" />
        </el-form-item>
        <el-form-item label="学号" required>
          <el-input v-model="form.student_id" placeholder="学号" />
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="form.class_id" placeholder="选择班级" clearable style="width:100%">
            <el-option v-for="c in store.classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="form.phone" placeholder="手机号" />
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="form.risk_level" style="width:100%">
            <el-option v-for="o in riskOptions" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showClassDialog" title="添加班级" width="400px">
      <el-form label-position="top">
        <el-form-item label="班级名称" required>
          <el-input v-model="newClassName" placeholder="例如：2024级软件1班" />
        </el-form-item>
        <el-form-item label="年级">
          <el-input v-model="newClassGrade" placeholder="例如：2024" />
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="newClassMajor" placeholder="例如：软件工程" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showClassDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddClass">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.student-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 24px;
}
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 26px; color: #4a7c6f; margin: 0 0 6px 0; font-weight: 700; }
.subtitle { color: #909399; font-size: 14px; margin: 0; }
.filter-bar {
  display: flex; gap: 12px; align-items: center;
  margin-bottom: 16px; flex-wrap: wrap;
}
.student-table { border-radius: 12px; overflow: hidden; }
</style>
