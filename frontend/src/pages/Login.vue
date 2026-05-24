<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const isRegister = ref(false)
const form = ref({ name: '', password: '', college: '' })
const submitting = ref(false)

async function handleSubmit() {
  submitting.value = true
  try {
    if (isRegister.value) {
      await auth.register(form.value.name, form.value.password, form.value.college)
      ElMessage.success('注册成功')
    } else {
      await auth.login(form.value.name, form.value.password)
      ElMessage.success('登录成功')
    }
    router.push('/')
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  } finally { submitting.value = false }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Counselor OS</h1>
      <p class="subtitle">{{ isRegister ? '创建账号' : '登录账号' }}</p>

      <el-form label-position="top" @submit.prevent="handleSubmit">
        <el-form-item label="用户名" required>
          <el-input v-model="form.name" placeholder="输入用户名" size="large" />
        </el-form-item>
        <el-form-item v-if="isRegister" label="学院">
          <el-input v-model="form.college" placeholder="例如：计算机科学与技术学院" size="large" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input v-model="form.password" type="password" placeholder="输入密码" size="large" show-password @keyup.enter="handleSubmit" />
        </el-form-item>

        <el-button type="primary" size="large" :loading="submitting" class="submit-btn" @click="handleSubmit">
          {{ isRegister ? '注册' : '登录' }}
        </el-button>
      </el-form>

      <div class="switch-mode">
        <span v-if="!isRegister">还没有账号？</span>
        <span v-else>已有账号？</span>
        <el-button link type="primary" @click="isRegister = !isRegister">
          {{ isRegister ? '去登录' : '去注册' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #e8f5e9 0%, #e3f2fd 50%, #f5f7fa 100%);
}
.login-card {
  background: #fff; border-radius: 20px; padding: 40px; width: 400px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
}
h1 { text-align: center; font-size: 28px; color: #4a7c6f; margin: 0 0 4px 0; font-weight: 800; }
.subtitle { text-align: center; color: #909399; font-size: 14px; margin: 0 0 28px 0; }
.submit-btn { width: 100%; border-radius: 20px; background: linear-gradient(135deg, #7ec8a0, #6db3b8); border: none; font-weight: 600; height: 44px; }
.switch-mode { text-align: center; margin-top: 16px; font-size: 13px; color: #909399; }
</style>
