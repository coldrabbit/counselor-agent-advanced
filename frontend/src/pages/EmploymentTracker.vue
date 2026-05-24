<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface EmpItem {
  id: string
  student_name: string
  student_id: string
  company: string
  position: string
  status: string
  offer_date: string | null
  notes: string
  created_at: string
}

const stats = ref({ seeking: 0, interviewing: 0, offered: 0, accepted: 0, total: 0 })
const employments = ref<EmpItem[]>([])
const loading = ref(false)
const filterStatus = ref('')
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const form = ref({
  student_name: '',
  student_id: '',
  company: '',
  position: '',
  status: 'seeking',
  offer_date: '',
  notes: '',
})
const resumeDialog = ref(false)
const resumeForm = ref({ student_name: '', major: '', target_position: '' })
const resumeAdvice = ref<any>(null)
const generating = ref(false)

const statusLabels: Record<string, string> = {
  seeking: '求职中',
  interviewing: '面试中',
  offered: '已获Offer',
  accepted: '已签约',
}
const statusTagTypes: Record<string, string> = {
  seeking: 'info',
  interviewing: 'warning',
  offered: 'success',
  accepted: '',
}

async function fetchData() {
  loading.value = true
  try {
    const [s, e] = await Promise.all([
      axios.get('/api/employments/stats'),
      axios.get('/api/employments', { params: { status: filterStatus.value || undefined } }),
    ])
    stats.value = s.data
    employments.value = e.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = {
    student_name: '',
    student_id: '',
    company: '',
    position: '',
    status: 'seeking',
    offer_date: '',
    notes: '',
  }
  dialogVisible.value = true
}

function openEdit(emp: EmpItem) {
  editingId.value = emp.id
  form.value = {
    student_name: emp.student_name,
    student_id: emp.student_id,
    company: emp.company,
    position: emp.position,
    status: emp.status,
    offer_date: emp.offer_date || '',
    notes: emp.notes,
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.student_name.trim()) return
  if (editingId.value) {
    await axios.put(`/api/employments/${editingId.value}`, form.value)
  } else {
    await axios.post('/api/employments', form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await fetchData()
}

async function handleDelete(id: string) {
  await axios.delete(`/api/employments/${id}`)
  ElMessage.success('已删除')
  await fetchData()
}

async function handleResumeAdvice() {
  generating.value = true
  try {
    const resp = await axios.post('/api/employments/resume-advice', { ...resumeForm.value })
    resumeAdvice.value = resp.data.advice
    ElMessage.success('建议生成成功')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '生成失败')
  } finally {
    generating.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="emp-page">
    <header class="page-header">
      <h1>就业与实习管理</h1>
      <p class="subtitle">跟踪学生求职进度，AI 提供简历与面试建议</p>
    </header>

    <div class="stats-row">
      <div class="stat-card" v-for="(label, key) in statusLabels" :key="key">
        <div class="num">{{ stats[key as keyof typeof stats] || 0 }}</div>
        <div class="label">{{ label }}</div>
      </div>
    </div>

    <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width:140px" @change="fetchData">
        <el-option v-for="(label, key) in statusLabels" :key="key" :label="label" :value="key" />
      </el-select>
      <div style="flex:1" />
      <el-button @click="resumeDialog = true">AI 简历建议</el-button>
      <el-button type="primary" @click="openCreate">+ 添加记录</el-button>
    </div>

    <el-table :data="employments" v-loading="loading" class="emp-table">
      <el-table-column prop="student_name" label="学生" width="100" />
      <el-table-column prop="student_id" label="学号" width="120" />
      <el-table-column prop="company" label="公司" min-width="140" />
      <el-table-column prop="position" label="岗位" min-width="140" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagTypes[row.status] || 'info'" size="small">
            {{ statusLabels[row.status] || row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="offer_date" label="Offer日期" width="120" />
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Record Dialog -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑' : '添加'" width="500px">
      <el-form label-position="top">
        <el-form-item label="学生姓名" required>
          <el-input v-model="form.student_name" />
        </el-form-item>
        <el-form-item label="学号">
          <el-input v-model="form.student_id" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="公司">
              <el-input v-model="form.company" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="岗位">
              <el-input v-model="form.position" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option v-for="(label, key) in statusLabels" :key="key" :label="label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="Offer日期">
          <el-input v-model="form.offer_date" placeholder="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- Resume Advice Dialog -->
    <el-dialog v-model="resumeDialog" title="AI 简历与面试建议" width="700px">
      <el-form label-position="top">
        <el-form-item label="学生姓名" required>
          <el-input v-model="resumeForm.student_name" />
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="resumeForm.major" />
        </el-form-item>
        <el-form-item label="目标岗位">
          <el-input v-model="resumeForm.target_position" />
        </el-form-item>
        <el-button type="primary" :loading="generating" @click="handleResumeAdvice" style="width:100%">
          生成建议
        </el-button>
      </el-form>
      <div
        v-if="resumeAdvice"
        style="margin-top:16px;line-height:1.8;font-size:14px;white-space:pre-wrap;max-height:500px;overflow-y:auto"
      >
        <div v-if="resumeAdvice.resume_tips">
          <b>简历优化建议：</b><br />
          <ul>
            <li v-for="t in resumeAdvice.resume_tips" :key="t">{{ t }}</li>
          </ul>
          <br />
        </div>
        <div v-if="resumeAdvice.interview_advice">
          <b>面试准备建议：</b><br />
          <ul>
            <li v-for="a in resumeAdvice.interview_advice" :key="a">{{ a }}</li>
          </ul>
          <br />
        </div>
        <div v-if="resumeAdvice.job_recommendations">
          <b>推荐岗位方向：</b><br />
          <ul>
            <li v-for="j in resumeAdvice.job_recommendations" :key="j">{{ j }}</li>
          </ul>
          <br />
        </div>
        <div v-if="resumeAdvice.skill_gap">
          <b>技能提升：</b><br />{{ resumeAdvice.skill_gap }}<br /><br />
        </div>
        <div v-if="resumeAdvice.summary"><b>综合建议：</b>{{ resumeAdvice.summary }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.emp-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 26px;
  color: #4a7c6f;
  margin: 0 0 6px 0;
  font-weight: 700;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 120px;
  padding: 16px;
  border-radius: 12px;
  text-align: center;
  background: #f5f7fa;
  border: 1px solid #e8edf2;
}

.stat-card .num {
  font-size: 28px;
  font-weight: 800;
  color: #303133;
}

.stat-card .label {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.emp-table {
  border-radius: 12px;
  overflow: hidden;
}
</style>
