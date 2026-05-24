<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface Activity {
  id: string
  title: string
  theme: string
  plan: string
  schedule: string
  host_script: string
  promotion: string
  summary_template: string
  budget: string
  participants: string
  status: string
  created_at: string
}

const theme = ref('')
const budget = ref('')
const participants = ref('')
const generating = ref(false)
const result = ref<Activity | null>(null)
const history = ref<Activity[]>([])
const activeTab = ref('plan')

async function fetchHistory() {
  const resp = await axios.get('/api/activities')
  history.value = resp.data
}

async function handleGenerate() {
  if (!theme.value.trim()) {
    ElMessage.warning('请输入活动主题')
    return
  }
  generating.value = true
  try {
    const resp = await axios.post('/api/activities/generate', {
      theme: theme.value,
      budget: budget.value,
      participants: participants.value,
    })
    result.value = resp.data
    ElMessage.success('活动方案生成成功')
    await fetchHistory()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '生成失败')
  } finally {
    generating.value = false
  }
}

onMounted(fetchHistory)
</script>

<template>
  <div class="activity-page">
    <header class="page-header">
      <h1>活动策划</h1>
      <p class="subtitle">输入活动主题，AI 自动生成完整活动方案</p>
    </header>

    <el-card class="input-card">
      <template #header>
        <span>活动需求</span>
      </template>
      <el-input
        v-model="theme"
        type="textarea"
        :rows="2"
        placeholder="活动主题，例如：防诈骗主题教育活动"
        style="margin-bottom:12px"
      />
      <el-row :gutter="12">
        <el-col :span="12">
          <el-input v-model="budget" placeholder="预算（可选）" />
        </el-col>
        <el-col :span="12">
          <el-input v-model="participants" placeholder="参与人数（可选）" />
        </el-col>
      </el-row>
      <el-button
        type="primary"
        :loading="generating"
        class="generate-btn"
        @click="handleGenerate"
      >
        {{ generating ? 'AI 策划中...' : '生成活动方案' }}
      </el-button>
    </el-card>

    <!-- Current Result -->
    <div v-if="result" class="result-area">
      <div class="result-header">
        <h2>{{ result.title }}</h2>
      </div>
      <el-tabs v-model="activeTab" type="border-card" class="activity-tabs">
        <el-tab-pane label="活动方案" name="plan">
          <div class="content-block">{{ result.plan }}</div>
        </el-tab-pane>
        <el-tab-pane label="流程表" name="schedule">
          <div class="content-block">{{ result.schedule }}</div>
        </el-tab-pane>
        <el-tab-pane label="主持稿" name="host_script">
          <div class="content-block">{{ result.host_script }}</div>
        </el-tab-pane>
        <el-tab-pane label="宣传文案" name="promotion">
          <div class="content-block">{{ result.promotion }}</div>
        </el-tab-pane>
        <el-tab-pane label="总结模板" name="summary">
          <div class="content-block">{{ result.summary_template }}</div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Empty State -->
    <div v-if="!result && history.length === 0" class="empty-state">
      <p>暂无活动方案，输入主题开始生成</p>
    </div>
  </div>
</template>

<style scoped>
.activity-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 28px 24px;
}

.page-header {
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

.result-area {
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

.activity-tabs {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
}

.activity-tabs :deep(.el-tabs__item.is-active) {
  color: #4a7c6f;
  font-weight: 600;
}

.activity-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border-radius: 2px;
}

.content-block {
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

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #909399;
  font-size: 14px;
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
