<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const question = ref('')
const asking = ref(false)
const answer = ref('')
const suggestedQuestions = [
  '帮我生成一个防诈骗主题班会的通知',
  '如何与学生进行有效的谈心谈话？',
  '学生出现成绩下滑应该怎么处理？',
  '策划一个心理健康主题活动',
]

async function handleAsk(q?: string) {
  const qText = q || question.value.trim()
  if (!qText) { ElMessage.warning('请输入问题'); return }
  asking.value = true
  answer.value = ''
  try {
    const resp = await axios.post('/api/ask', { question: qText })
    answer.value = resp.data.answer
  } catch {
    ElMessage.error('请求失败，请稍后再试')
  } finally { asking.value = false }
}

function handleSuggested(q: string) {
  question.value = q
  handleAsk(q)
}
</script>

<template>
  <div class="home-page">
    <div class="hero">
      <h1 class="hero-title">Counselor OS</h1>
      <p class="hero-subtitle">AI 赋能的辅导员工作操作系统 — 从通知生成到风险预警，一站式提升工作效率</p>

      <div class="ask-box">
        <el-input
          v-model="question"
          placeholder="输入问题，例如：帮我生成一个防诈骗主题班会的通知..."
          size="large"
          :disabled="asking"
          @keyup.enter="handleAsk()"
          class="ask-input"
        >
          <template #append>
            <el-button :loading="asking" @click="handleAsk()" style="background:linear-gradient(135deg,#7ec8a0,#6db3b8);border:none;color:#fff;font-weight:600">
              {{ asking ? '思考中...' : '提问' }}
            </el-button>
          </template>
        </el-input>
      </div>

      <div class="suggestions">
        <span class="sug-label">试试问：</span>
        <el-tag v-for="q in suggestedQuestions" :key="q" class="sug-tag" @click="handleSuggested(q)">{{ q }}</el-tag>
      </div>

      <div v-if="answer" class="answer-card">
        <div class="answer-content">{{ answer }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  min-height: calc(100vh - 56px);
  display: flex; align-items: center; justify-content: center;
  padding: 40px 24px;
}
.hero { max-width: 700px; width: 100%; text-align: center; }
.hero-title { font-size: 42px; font-weight: 800; color: #4a7c6f; margin: 0 0 12px 0; letter-spacing: 1px; }
.hero-subtitle { font-size: 16px; color: #909399; margin: 0 0 36px 0; line-height: 1.6; }
.ask-box { margin-bottom: 20px; }
.ask-input :deep(.el-input__wrapper) { border-radius: 24px; padding: 6px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
.ask-input :deep(.el-input-group__append) { border-radius: 0 24px 24px 0; overflow: hidden; }
.suggestions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: center; margin-bottom: 24px; }
.sug-label { font-size: 12px; color: #b0b0b0; margin-right: 4px; }
.sug-tag { cursor: pointer; border-radius: 14px; font-size: 12px; }
.sug-tag:hover { background: #ecf5ff; }
.answer-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); text-align: left; animation: fade-in-up 0.4s ease-out; }
.answer-content { white-space: pre-wrap; line-height: 1.8; font-size: 15px; color: #303133; }
</style>
