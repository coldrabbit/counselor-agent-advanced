<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useNoticeStore } from '../stores/notice'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ 'update:visible': [value: boolean] }>()

const store = useNoticeStore()
const form = ref({
  name: '',
  college: '',
  phone: '',
  email: '',
})
const saving = ref(false)

watch(() => props.visible, (val) => {
  if (val && store.profile) {
    form.value = {
      name: store.profile.name || '',
      college: store.profile.college || '',
      phone: store.profile.phone || '',
      email: store.profile.email || '',
    }
  }
})

async function handleSave() {
  if (!form.value.name.trim() || !form.value.college.trim()) {
    ElMessage.warning('请填写姓名和学院')
    return
  }
  saving.value = true
  try {
    await store.saveProfile(form.value)
    ElMessage.success('保存成功')
    emit('update:visible', false)
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function handleClose() {
  emit('update:visible', false)
}
</script>

<template>
  <el-drawer
    :model-value="visible"
    title="辅导员信息设置"
    size="380px"
    @close="handleClose"
  >
    <el-form :model="form" label-position="top">
      <el-form-item label="姓名" required>
        <el-input v-model="form.name" placeholder="例如：张伟" />
      </el-form-item>
      <el-form-item label="学院" required>
        <el-input v-model="form.college" placeholder="例如：计算机科学与技术学院" />
      </el-form-item>
      <el-form-item label="电话">
        <el-input v-model="form.phone" placeholder="选填" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" placeholder="选填" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="handleSave" style="width: 100%">
          保存
        </el-button>
      </el-form-item>
    </el-form>
  </el-drawer>
</template>

<style scoped>
:deep(.el-drawer__header) {
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