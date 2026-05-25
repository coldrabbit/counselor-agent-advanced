<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import PreGenerateDialog from '../components/PreGenerateDialog.vue'
import { useNoticeStore } from '../stores/notice'

interface MonthlyTask {
  id: string
  month: number
  category: string
  title: string
  description: string
  action_type: 'notice' | 'talk' | 'todo'
  action_label: string
  action_params: Record<string, string>
}

const categoryOrder = ['安全管理', '学风建设', '心理健康', '资助管理', '活动组织', '党团建设', '就业实习', '日常管理']

const router = useRouter()
const noticeStore = useNoticeStore()
const selectedMonth = ref(new Date().getMonth() + 1)
const tasks = ref<MonthlyTask[]>([])
const loading = ref(false)
const generating = ref(false)
const doneTaskIds = ref<Set<string>>(new Set())
const showPreDialog = ref(false)
const initialEvent = ref('')

const monthOptions = Array.from({ length: 12 }, (_, index) => ({ label: `${index + 1} 月`, value: index + 1 }))

const orderedTasks = computed(() => [...tasks.value].sort((left, right) => {
  const categoryDiff = categoryOrder.indexOf(left.category) - categoryOrder.indexOf(right.category)
  return categoryDiff || left.title.localeCompare(right.title, 'zh-Hans-CN')
}))

const categoryStats = computed(() => categoryOrder
  .map(category => ({ category, count: tasks.value.filter(task => task.category === category).length }))
  .filter(group => group.count > 0))

async function loadTasks() {
  loading.value = true
  try {
    const resp = await axios.get<MonthlyTask[]>('/api/monthly-tasks', { params: { month: selectedMonth.value } })
    tasks.value = resp.data
  } catch {
    ElMessage.error('月度任务加载失败')
  } finally {
    loading.value = false
  }
}

function isDone(taskId: string) {
  return doneTaskIds.value.has(taskId)
}

function toggleDone(taskId: string) {
  const next = new Set(doneTaskIds.value)
  if (next.has(taskId)) {
    next.delete(taskId)
  } else {
    next.add(taskId)
  }
  doneTaskIds.value = next
}

function openNoticeDialog(task: MonthlyTask) {
  initialEvent.value = task.action_params.event || task.title
  showPreDialog.value = true
}

function openTalkRecord() {
  router.push('/talk-record')
}

async function handleGenerate(payload: { event: string; time: string; location: string; participants: string }) {
  generating.value = true
  try {
    await noticeStore.generate(payload.event, payload.time, payload.location, payload.participants)
    ElMessage.success('通知生成成功，可去通知页查看')
  } catch {
    ElMessage.error(noticeStore.error || '通知生成失败')
  } finally {
    generating.value = false
  }
}

watch(selectedMonth, loadTasks)
onMounted(loadTasks)
</script>

<template>
  <main class="monthly-workbench">
    <header class="workbench-header">
      <div>
        <h1>月度工作台</h1>
        <p>按月份聚合辅导员重点工作，快速进入通知、谈心和待办处理。</p>
      </div>
      <el-select v-model="selectedMonth" class="month-select" size="large" aria-label="切换月份">
        <el-option v-for="month in monthOptions" :key="month.value" :label="month.label" :value="month.value" />
      </el-select>
    </header>

    <el-alert v-if="tasks.length === 0 && !loading" title="当前月份暂无工作事项" type="info" :closable="false" class="empty-alert" />

    <div v-loading="loading || generating" class="task-grid-wrap">
      <div class="category-summary">
        <el-tag v-for="group in categoryStats" :key="group.category" effect="plain">
          {{ group.category }} · {{ group.count }}
        </el-tag>
      </div>

      <el-row :gutter="16">
        <el-col v-for="task in orderedTasks" :key="task.id" :xs="24" :sm="12" :md="8" :lg="6" class="task-col">
          <el-card class="task-card" :class="{ done: isDone(task.id) }" shadow="hover">
            <div class="task-card-header">
              <el-tag size="small">{{ task.category }}</el-tag>
              <span v-if="isDone(task.id)" class="done-label">已完成</span>
            </div>
            <h2>{{ task.title }}</h2>
            <p>{{ task.description }}</p>

            <div class="card-actions">
              <el-button v-if="task.action_type === 'notice'" type="primary" size="small" @click="openNoticeDialog(task)">
                {{ task.action_label }}
              </el-button>
              <el-button v-else-if="task.action_type === 'talk'" type="warning" size="small" @click="openTalkRecord">
                {{ task.action_label }}
              </el-button>

              <el-button v-if="task.action_type !== 'todo'" size="small" :type="isDone(task.id) ? 'success' : 'info'" plain @click="toggleDone(task.id)">
                {{ isDone(task.id) ? '取消完成' : '标记完成' }}
              </el-button>
              <el-button v-else size="small" :type="isDone(task.id) ? 'success' : 'primary'" plain @click="toggleDone(task.id)">
                {{ isDone(task.id) ? '取消完成' : task.action_label }}
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <PreGenerateDialog v-model:visible="showPreDialog" :initial-event="initialEvent" @generate="handleGenerate" />
  </main>
</template>

<style scoped>
.monthly-workbench {
  max-width: 1280px; margin: 0 auto; padding: 28px 24px 44px;
}

.workbench-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 22px;
}

.workbench-header h1 {
  margin: 0 0 6px; color: #30424a; font-size: 26px; font-weight: 700;
}

.workbench-header p {
  margin: 0; color: #697780; font-size: 14px; line-height: 1.6;
}

.month-select {
  width: 150px; flex: 0 0 auto;
}

.empty-alert {
  margin-bottom: 16px;
}

.task-grid-wrap {
  min-height: 320px;
}

.category-summary {
  display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;
}

.task-col {
  margin-bottom: 16px;
}

.task-card {
  height: 100%; min-height: 214px; border-radius: 8px; border: 1px solid #e7edf0;
  transition: opacity 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
}

.task-card:hover {
  transform: translateY(-2px); border-color: #c9d8de;
}

.task-card.done {
  opacity: 0.58;
}

.task-card.done h2,
.task-card.done p {
  text-decoration: line-through;
}

.task-card-header {
  display: flex; align-items: center; justify-content: space-between; gap: 10px; min-height: 24px; margin-bottom: 12px;
}

.done-label {
  color: #67c23a; font-size: 12px; font-weight: 600;
}

.task-card h2 {
  margin: 0 0 8px; color: #263238; font-size: 16px; font-weight: 700; line-height: 1.4;
}

.task-card p {
  min-height: 62px; margin: 0 0 18px; color: #697780; font-size: 13px; line-height: 1.6;
}

.card-actions {
  display: flex; flex-wrap: wrap; gap: 8px;
}

.card-actions :deep(.el-button) {
  margin-left: 0;
}

@media (max-width: 640px) {
  .monthly-workbench {
    padding: 20px 14px 32px;
  }

  .workbench-header {
    flex-direction: column; align-items: stretch;
  }

  .month-select {
    width: 100%;
  }
}
</style>
