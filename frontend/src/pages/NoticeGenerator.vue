<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useNoticeStore } from '../stores/notice'
import CounselorDrawer from '../components/CounselorDrawer.vue'
import PreGenerateDialog from '../components/PreGenerateDialog.vue'

interface TemplateItem {
  id: string; name: string; category: string; content: string;
}

const store = useNoticeStore()
const event = ref('')
const generating = ref(false)
const showSettings = ref(false)
const showPreDialog = ref(false)

const batchMode = ref(false)
const batchStudentIds = ref<string[]>([])
const batchStudents = ref<Array<{id:string,name:string,student_id:string,class_id:string|null}>>([])
const batchClasses = ref<Array<{id:string,name:string}>>([])
const batchClassFilter = ref('')
const batchLoading = ref(false)

const templates = ref<TemplateItem[]>([])
const selectedTemplate = ref('')
const showTemplateDialog = ref(false)
const templateForm = ref({ name: '', category: '通用', content: '' })

async function fetchTemplates() {
  const resp = await axios.get('/api/templates')
  templates.value = resp.data
}

function selectTemplate(id: string) {
  const tmpl = templates.value.find(t => t.id === id)
  if (tmpl) { event.value = tmpl.content }
  selectedTemplate.value = ''
}

async function loadClasses() {
  const resp = await axios.get('/api/classes')
  batchClasses.value = resp.data
}

async function loadStudentsForBatch() {
  const params: Record<string, string> = {}
  if (batchClassFilter.value) params.class_id = batchClassFilter.value
  const resp = await axios.get('/api/students', { params })
  batchStudents.value = resp.data
}

async function handleBatchGenerate() {
  if (!event.value.trim()) { ElMessage.warning('请输入事件描述'); return }
  if (batchStudentIds.value.length === 0) { ElMessage.warning('请选择学生'); return }
  batchLoading.value = true
  try {
    const resp = await axios.post('/api/notices/batch-generate', {
      event: event.value, student_ids: batchStudentIds.value,
    })
    const data = resp.data
    ElMessage.success(`批量生成完成：成功 ${data.created} 条，失败 ${data.failed} 条`)
    batchStudentIds.value = []
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '批量生成失败')
  } finally { batchLoading.value = false }
}

async function saveTemplate() {
  if (!templateForm.value.name.trim() || !templateForm.value.content.trim()) return
  await axios.post('/api/templates', { ...templateForm.value })
  showTemplateDialog.value = false
  templateForm.value = { name: '', category: '通用', content: '' }
  await fetchTemplates()
}

onMounted(() => {
  store.fetchProfile()
  fetchTemplates()
  loadClasses()
})

function handleGenerateClick() {
  if (!event.value.trim()) {
    ElMessage.warning('请输入事件描述')
    return
  }
  showPreDialog.value = true
}

async function handleGenerate(payload: { event: string; time: string; location: string; participants: string }) {
  generating.value = true
  try {
    await store.generate(payload.event, payload.time, payload.location, payload.participants)
    ElMessage.success('通知生成成功')
  } catch {
    ElMessage.error(store.error || '生成失败')
  } finally {
    generating.value = false
  }
}

const reviewComment = ref('')

async function handleApprove() {
  if (!store.currentNotice) return
  try {
    await axios.put(`/api/notices/${store.currentNotice.id}/approve`, { comment: reviewComment.value })
    ElMessage.success('通知已审核通过')
    store.currentNotice.status = 'APPROVED'
  } catch { ElMessage.error(store.error || '审核失败') }
}

async function handleReject() {
  if (!store.currentNotice) return
  try {
    await axios.put(`/api/notices/${store.currentNotice.id}/reject`, { comment: reviewComment.value })
    ElMessage.success('已退回修改')
    store.currentNotice.status = 'DRAFT'
  } catch { ElMessage.error(store.error || '操作失败') }
}

async function exportPDF(type: string) {
  let title = ''
  let content = ''
  if (type === 'notice' && store.currentNotice) {
    title = store.currentNotice.title || '通知'
    content = `【正式通知】\n${store.currentNotice.formal_notice}\n\n【微信群通知】\n${store.currentNotice.wechat_notice}\n\n【家长通知】\n${store.currentNotice.parent_notice}\n\n【短信简版】\n${store.currentNotice.sms_notice}`
  }
  if (!title) return
  try {
    const resp = await axios.post('/api/export/pdf', { title, content }, { responseType: 'blob' })
    const url = URL.createObjectURL(resp.data)
    const a = document.createElement('a')
    a.href = url; a.download = `${title}.pdf`; a.click()
    URL.revokeObjectURL(url)
  } catch { /* ignore */ }
}

async function handleOCRUpload(options: any) {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    const resp = await axios.post('/api/ocr/recognize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    if (resp.data.success && resp.data.text) {
      event.value = event.value ? event.value + '\n' + resp.data.text : resp.data.text
      ElMessage.success('文字识别完成，已添加到输入框')
    } else {
      ElMessage.warning('未能识别到文字')
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '识别失败')
  }
}
</script>

<template>
  <div class="notice-generator">
    <header class="page-header">
      <div class="header-row">
        <div>
          <h1>通知生成器</h1>
          <p class="subtitle">输入事件描述，AI 自动生成多版本通知</p>
        </div>
        <el-button
          :icon="'Setting'"
          circle
          @click="showSettings = true"
          title="辅导员信息设置"
        >
          ⚙
        </el-button>
      </div>
      <p v-if="!store.profile" class="profile-hint">
        提示：设置辅导员信息后，生成的通知将自动使用真实姓名和学院
      </p>
    </header>

    <!-- Input Section -->
    <el-card class="input-card">
      <template #header>
        <span>事件描述</span>
      </template>
      <div style="margin-bottom:12px">
        <el-upload :show-file-list="false" :auto-upload="false" accept="image/*" :on-change="handleOCRUpload">
          <el-button size="small">📷 拍照/图片识别文字</el-button>
        </el-upload>
      </div>
      <div style="margin-bottom:12px;display:flex;align-items:center;gap:8px">
        <el-switch v-model="batchMode" active-text="批量模式" @change="() => { if(batchMode) loadStudentsForBatch() }" />
      </div>
      <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center">
        <el-select v-model="selectedTemplate" placeholder="使用模板..." clearable size="small" style="width:200px" @change="selectTemplate">
          <el-option v-for="t in templates" :key="t.id" :label="`[${t.category}] ${t.name}`" :value="t.id" />
        </el-select>
        <el-button size="small" @click="showTemplateDialog = true">+ 管理模板</el-button>
      </div>
      <el-input
        v-model="event"
        type="textarea"
        :rows="3"
        placeholder="例如：明天下午 3 点召开防诈骗班会，地点 A203，全员参加"
      />
      <div v-if="batchMode" style="margin-top:12px">
        <div style="display:flex;gap:8px;margin-bottom:8px">
          <el-select v-model="batchClassFilter" placeholder="按班级筛选" clearable size="small" style="width:200px" @change="loadStudentsForBatch">
            <el-option label="全部" value="" />
            <el-option v-for="c in batchClasses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>
        <el-select v-model="batchStudentIds" multiple placeholder="选择学生..." style="width:100%" filterable>
          <el-option v-for="s in batchStudents" :key="s.id" :label="`${s.name} (${s.student_id})`" :value="s.id" />
        </el-select>
      </div>
      <el-button
        v-if="!batchMode"
        type="primary"
        :loading="generating"
        class="generate-btn"
        @click="handleGenerateClick"
      >
        {{ generating ? 'AI 生成中...' : '生成通知' }}
      </el-button>
      <el-button
        v-if="batchMode"
        type="primary"
        :loading="batchLoading"
        class="generate-btn"
        @click="handleBatchGenerate"
      >
        {{ batchLoading ? '批量生成中...' : `批量生成 (${batchStudentIds.length}人)` }}
      </el-button>
    </el-card>

    <!-- Result Section -->
    <div v-if="store.currentNotice" class="result-section">
      <div class="result-header">
        <h2>{{ store.currentNotice.title }}</h2>
        <el-tag :type="store.currentNotice.status === 'APPROVED' ? 'success' : 'warning'" size="large">
          {{ store.currentNotice.status === 'APPROVED' ? '已审核' : '待审核' }}
        </el-tag>
      </div>

      <el-tabs type="border-card" class="notice-tabs">
        <el-tab-pane label="正式通知">
          <div class="notice-content">{{ store.currentNotice.formal_notice }}</div>
        </el-tab-pane>
        <el-tab-pane label="微信群通知">
          <div class="notice-content">{{ store.currentNotice.wechat_notice }}</div>
        </el-tab-pane>
        <el-tab-pane label="家长通知">
          <div class="notice-content">{{ store.currentNotice.parent_notice }}</div>
        </el-tab-pane>
        <el-tab-pane label="短信简版">
          <div class="notice-content">{{ store.currentNotice.sms_notice }}</div>
        </el-tab-pane>
      </el-tabs>

      <div class="actions">
        <el-input v-if="store.currentNotice && store.currentNotice.status !== 'APPROVED'"
          v-model="reviewComment" placeholder="审核意见（可选）" size="large" style="width:300px" />
        <el-button
          v-if="store.currentNotice && store.currentNotice.status !== 'APPROVED'"
          type="success"
          size="large"
          @click="handleApprove"
        >
          审核通过
        </el-button>
        <el-button
          v-if="store.currentNotice && store.currentNotice.status !== 'APPROVED'"
          type="warning"
          size="large"
          @click="handleReject"
        >
          退回修改
        </el-button>
        <el-button size="large" @click="exportPDF('notice')">导出 PDF</el-button>
      </div>
    </div>

    <!-- Settings Drawer -->
    <CounselorDrawer v-model:visible="showSettings" />

    <!-- Pre-generate Dialog -->
    <PreGenerateDialog
      v-model:visible="showPreDialog"
      :initial-event="event"
      @generate="handleGenerate"
    />

    <!-- Template Management Dialog -->
    <el-dialog v-model="showTemplateDialog" title="管理模板" width="500px">
      <div style="margin-bottom:16px">
        <el-form label-position="top">
          <el-form-item label="模板名称" required>
            <el-input v-model="templateForm.name" placeholder="例如：防诈骗班会通知" />
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="templateForm.category" style="width:100%">
              <el-option label="安全" value="安全" />
              <el-option label="学风" value="学风" />
              <el-option label="活动" value="活动" />
              <el-option label="心理健康" value="心理健康" />
              <el-option label="就业" value="就业" />
              <el-option label="通用" value="通用" />
            </el-select>
          </el-form-item>
          <el-form-item label="事件描述" required>
            <el-input v-model="templateForm.content" type="textarea" :rows="3" placeholder="输入模板化的事件描述" />
          </el-form-item>
          <el-button type="primary" @click="saveTemplate" style="width:100%">保存模板</el-button>
        </el-form>
      </div>
      <el-table :data="templates" size="small" max-height="300">
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="async () => { await axios.delete(`/api/templates/${row.id}`); await fetchTemplates(); }">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<style scoped>
.notice-generator {
  max-width: 900px;
  margin: 0 auto;
  padding: 28px 24px;
}

.page-header {
  margin-bottom: 28px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-row h1 {
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

.profile-hint {
  margin: 14px 0 0 0;
  padding: 10px 14px;
  background: #fdf6ec;
  color: #e6a23c;
  border-radius: 8px;
  font-size: 13px;
  border: 1px solid #faecd8;
}

.input-card {
  margin-bottom: 24px;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.input-card :deep(.el-card__header) {
  font-weight: 600;
  color: #4a7c6f;
  font-size: 15px;
}

.input-card :deep(.el-textarea__inner) {
  border-radius: 10px;
  background: #f8faf9;
  border-color: #dce8e3;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.input-card :deep(.el-textarea__inner:focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
}

.generate-btn {
  margin-top: 16px;
  width: 100%;
  border-radius: 20px;
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border: none;
  font-weight: 600;
  font-size: 15px;
  height: 44px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(126, 168, 160, 0.3);
}

.generate-btn :deep(.el-button) {
  background: transparent;
}

.result-section {
  margin-top: 28px;
  animation: fade-in-up 0.4s ease-out;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}

.result-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.notice-tabs {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
}

.notice-tabs :deep(.el-tabs__item.is-active) {
  color: #4a7c6f;
  font-weight: 600;
}

.notice-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border-radius: 2px;
}

.notice-content {
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
  min-height: 200px;
  padding: 20px;
  background: #fafcfa;
  border-radius: 10px;
  border: 1px solid #edf2f0;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.actions :deep(.el-button--success) {
  border-radius: 20px;
  font-weight: 600;
}
</style>
