<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useNoticeStore } from '../stores/notice'
import CounselorDrawer from '../components/CounselorDrawer.vue'
import PreGenerateDialog from '../components/PreGenerateDialog.vue'

const store = useNoticeStore()
const event = ref('')
const generating = ref(false)
const showSettings = ref(false)
const showPreDialog = ref(false)

onMounted(() => {
  store.fetchProfile()
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

async function handleApprove() {
  if (!store.currentNotice) return
  try {
    await store.approve(store.currentNotice.id)
    ElMessage.success('通知已审核通过')
  } catch {
    ElMessage.error(store.error || '审核失败')
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
      <el-input
        v-model="event"
        type="textarea"
        :rows="3"
        placeholder="例如：明天下午 3 点召开防诈骗班会，地点 A203，全员参加"
      />
      <el-button
        type="primary"
        :loading="generating"
        class="generate-btn"
        @click="handleGenerateClick"
      >
        {{ generating ? 'AI 生成中...' : '生成通知' }}
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
        <el-button
          v-if="store.currentNotice.status !== 'APPROVED'"
          type="success"
          size="large"
          @click="handleApprove"
        >
          审核通过
        </el-button>
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
