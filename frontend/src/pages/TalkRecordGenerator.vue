<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useTalkRecordStore } from '../stores/talkRecord'

const store = useTalkRecordStore()
const studentName = ref('')
const studentId = ref('')
const situation = ref('')
const generating = ref(false)

function riskTagType(level: string): 'success' | 'warning' | 'danger' {
  if (level === 'low') return 'success'
  if (level === 'high') return 'danger'
  return 'warning'
}

async function handleGenerate() {
  if (!studentName.value.trim() || !studentId.value.trim()) {
    ElMessage.warning('请填写学生姓名和学号')
    return
  }
  if (!situation.value.trim()) {
    ElMessage.warning('请填写谈话情况描述')
    return
  }
  generating.value = true
  try {
    await store.generate(studentName.value.trim(), studentId.value.trim(), situation.value.trim())
    ElMessage.success('谈话记录生成成功')
  } catch {
    ElMessage.error(store.error || '生成失败')
  } finally {
    generating.value = false
  }
}

async function handleApprove() {
  if (!store.currentRecord) return
  try {
    await store.approve(store.currentRecord.id)
    ElMessage.success('已审核通过')
  } catch {
    ElMessage.error(store.error || '审核失败')
  }
}

async function exportPDF(type: string) {
  let title = ''
  let content = ''
  if (type === 'record' && store.currentRecord) {
    title = `${store.currentRecord.student_name} 谈心谈话记录`
    content = `【学生】${store.currentRecord.student_name} (${store.currentRecord.student_id})\n【风险等级】${store.currentRecord.risk_level}\n\n【谈话记录】\n${store.currentRecord.conversation_record}\n\n【跟进建议】\n${store.currentRecord.follow_up_advice}\n\n【家校沟通建议】\n${store.currentRecord.parent_advice}`
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
</script>

<template>
  <div class="talk-record-page">
    <header class="page-header">
      <h1>谈心谈话记录</h1>
      <p class="subtitle">输入学生信息和谈话情况，AI 自动生成谈话记录、风险评估与跟进建议</p>
    </header>

    <el-card class="input-card">
      <template #header><span>学生信息</span></template>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-input v-model="studentName" placeholder="学生姓名" />
        </el-col>
        <el-col :span="12">
          <el-input v-model="studentId" placeholder="学号" />
        </el-col>
      </el-row>
    </el-card>

    <el-card class="input-card">
      <template #header><span>谈话情况</span></template>
      <el-input
        v-model="situation"
        type="textarea"
        :rows="4"
        placeholder="描述学生的情况，例如：该生近期旷课两次，情绪低落，与室友关系紧张..."
      />
      <el-button type="primary" :loading="generating" class="generate-btn" @click="handleGenerate">
        {{ generating ? 'AI 生成中...' : '生成谈话记录' }}
      </el-button>
    </el-card>

    <div v-if="store.currentRecord" class="result-section">
      <div class="result-header">
        <h2>{{ store.currentRecord.student_name }} 的谈话记录</h2>
        <div class="result-badges">
          <el-tag :type="riskTagType(store.currentRecord.risk_level)" size="large">
            风险等级：{{ store.currentRecord.risk_level === 'low' ? '低' : store.currentRecord.risk_level === 'high' ? '高' : '中' }}
          </el-tag>
          <el-tag :type="store.currentRecord.status === 'APPROVED' ? 'success' : 'warning'" size="large">
            {{ store.currentRecord.status === 'APPROVED' ? '已审核' : '待审核' }}
          </el-tag>
        </div>
      </div>

      <el-tabs type="border-card" class="record-tabs">
        <el-tab-pane label="谈话记录">
          <div class="record-content">{{ store.currentRecord.conversation_record }}</div>
        </el-tab-pane>
        <el-tab-pane label="跟进建议">
          <div class="record-content">{{ store.currentRecord.follow_up_advice }}</div>
        </el-tab-pane>
        <el-tab-pane label="家校沟通建议">
          <div class="record-content">{{ store.currentRecord.parent_advice }}</div>
        </el-tab-pane>
      </el-tabs>

      <div class="actions">
        <el-button
          v-if="store.currentRecord.status !== 'APPROVED'"
          type="success"
          size="large"
          @click="handleApprove"
        >
          审核通过
        </el-button>
        <el-button size="large" @click="exportPDF('record')">导出 PDF</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.talk-record-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 28px 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 28px;
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

.input-card {
  margin-bottom: 18px;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.input-card :deep(.el-card__header) {
  font-weight: 600;
  color: #4a7c6f;
  font-size: 15px;
}

.input-card :deep(.el-input__wrapper) {
  border-radius: 10px;
  background: #f8faf9;
  border-color: #dce8e3;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.input-card :deep(.el-input__wrapper.is-focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
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

.result-section {
  margin-top: 28px;
  animation: fade-in-up 0.4s ease-out;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.result-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.result-badges {
  display: flex;
  gap: 8px;
}

.record-tabs {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
}

.record-tabs :deep(.el-tabs__item.is-active) {
  color: #4a7c6f;
  font-weight: 600;
}

.record-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border-radius: 2px;
}

.record-content {
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
