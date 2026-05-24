<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ visible: boolean; initialEvent: string }>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'generate': [payload: { event: string; time: string; location: string; participants: string }]
}>()

const event = ref('')
const time = ref('')
const location = ref('')
const participants = ref('')

watch(() => props.visible, (val) => {
  if (val) {
    event.value = props.initialEvent
    time.value = ''
    location.value = ''
    participants.value = ''
  }
})

function handleGenerate() {
  if (!event.value.trim()) return
  emit('generate', {
    event: event.value.trim(),
    time: time.value.trim(),
    location: location.value.trim(),
    participants: participants.value.trim(),
  })
  emit('update:visible', false)
}

function handleCancel() {
  emit('update:visible', false)
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    title="完善事件信息"
    width="520px"
    @close="handleCancel"
  >
    <el-form label-position="top">
      <el-form-item label="事件描述">
        <el-input
          v-model="event"
          type="textarea"
          :rows="2"
          placeholder="描述事件内容"
        />
      </el-form-item>
      <el-form-item label="时间">
        <el-input v-model="time" placeholder="例如：5月25日下午3点" />
      </el-form-item>
      <el-form-item label="地点">
        <el-input v-model="location" placeholder="例如：A203教室" />
      </el-form-item>
      <el-form-item label="参加人员">
        <el-input v-model="participants" placeholder="例如：2024级软件1班全体同学" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleGenerate">确认生成</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
:deep(.el-dialog__header) {
  color: #4a7c6f;
  font-weight: 700;
  font-size: 16px;
}

:deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  border-radius: 10px;
  background: #f8faf9;
  transition: border-color 0.25s, box-shadow 0.25s;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
}

:deep(.el-textarea__inner) {
  border-radius: 10px;
  background: #f8faf9;
  transition: border-color 0.25s, box-shadow 0.25s;
}

:deep(.el-textarea__inner:focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
}

:deep(.el-button--primary) {
  border-radius: 20px;
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border: none;
  font-weight: 600;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(126, 168, 160, 0.3);
}
</style>
