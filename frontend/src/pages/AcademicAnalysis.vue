<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const uploading = ref(false)
const result = ref<any>(null)
const activeTab = ref('overview')

async function handleUpload(options: any) {
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    const resp = await axios.post('/api/analysis/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    if (resp.data.success) {
      result.value = resp.data.analysis
      ElMessage.success('分析完成')
    } else {
      ElMessage.error(resp.data.error || '分析失败')
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

function severityType(s: string) { return s === 'high' ? 'danger' : s === 'medium' ? 'warning' : 'success' }
function severityLabel(s: string) { return s === 'high' ? '严重' : s === 'medium' ? '需关注' : '一般' }

async function exportPDF() {
  if (!result.value) return
  let content = ''
  if (result.value.class_overview) content += `【班级总览】\n${result.value.class_overview}\n\n`
  if (result.value.abnormal_students?.length) {
    content += `【异常学生】\n${result.value.abnormal_students.map((s:any) => `• ${s.name}: ${s.issue} (${s.severity})`).join('\n')}\n\n`
  }
  if (result.value.grade_warnings?.length) {
    content += `【学业预警】\n${result.value.grade_warnings.map((w:any) => `• ${w.name} - ${w.course}: ${w.risk}`).join('\n')}\n\n`
  }
  if (result.value.academic_advice?.length) {
    content += `【学风建议】\n${result.value.academic_advice.map((a:string,i:number) => `${i+1}. ${a}`).join('\n')}\n\n`
  }
  if (result.value.summary) content += `【总结】\n${result.value.summary}`

  try {
    const resp = await axios.post('/api/export/pdf', { title: '学情分析报告', content }, { responseType: 'blob' })
    const url = URL.createObjectURL(resp.data)
    const a = document.createElement('a')
    a.href = url; a.download = '学情分析报告.pdf'; a.click()
    URL.revokeObjectURL(url)
  } catch { /* ignore */ }
}

function downloadTemplate() {
  const rows = [
    ['姓名', '学号', '课程', '成绩', '缺勤次数', '请假次数'],
    ['李明', '2024001', '高等数学', '85', '1', '0'],
    ['王红', '2024002', '高等数学', '55', '4', '2'],
    ['李明', '2024001', '大学英语', '72', '1', '0'],
    ['王红', '2024002', '大学英语', '60', '4', '2'],
  ]
  const csv = rows.map(r => r.join(',')).join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'academic_analysis_template.csv'; a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="analysis-page">
    <header class="page-header">
      <h1>学情分析</h1>
      <p class="subtitle">上传学生成绩和考勤数据，AI 自动生成学情分析报告</p>
    </header>

    <el-card v-if="!result" class="upload-card">
      <div style="text-align:center;padding:40px 20px">
        <p style="font-size:16px;color:#606266;margin-bottom:20px">上传 Excel/CSV 文件，表头需包含：<b>姓名、学号、课程、成绩、缺勤次数、请假次数</b></p>
        <el-upload :show-file-list="false" :auto-upload="false" accept=".xlsx,.xls,.csv" :on-change="handleUpload" drag>
          <el-button type="primary" :loading="uploading" size="large">
            {{ uploading ? 'AI 分析中...' : '选择文件并上传' }}
          </el-button>
        </el-upload>
        <el-button style="margin-top:16px" size="small" @click="downloadTemplate">下载 CSV 模板</el-button>
      </div>
    </el-card>

    <div v-else class="result-area">
      <el-card style="margin-bottom:16px">
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <b>分析结果</b>
            <el-button size="small" @click="exportPDF">导出 PDF</el-button>
          </div>
        </template>
        <p style="font-size:15px;line-height:1.8;color:#303133" v-if="result.summary">{{ result.summary }}</p>
      </el-card>

      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="班级总览" name="overview">
          <div class="report-section" v-if="result.class_overview">{{ result.class_overview }}</div>
          <div v-else class="empty-hint">暂无数据</div>
        </el-tab-pane>
        <el-tab-pane label="异常学生" name="abnormal">
          <el-table :data="result.abnormal_students || []" size="small" v-if="result.abnormal_students?.length">
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="issue" label="问题描述" show-overflow-tooltip />
            <el-table-column label="严重程度" width="120">
              <template #default="{ row }">
                <el-tag :type="severityType(row.severity)" size="small">{{ severityLabel(row.severity) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div v-else class="empty-hint">未发现异常学生</div>
        </el-tab-pane>
        <el-tab-pane label="学业预警" name="warnings">
          <el-table :data="result.grade_warnings || []" size="small" v-if="result.grade_warnings?.length">
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="course" label="课程" width="160" />
            <el-table-column prop="risk" label="风险描述" show-overflow-tooltip />
          </el-table>
          <div v-else class="empty-hint">无学业预警</div>
        </el-tab-pane>
        <el-tab-pane label="学风建议" name="advice">
          <ul v-if="result.academic_advice?.length" style="line-height:2;font-size:14px">
            <li v-for="(a, i) in result.academic_advice" :key="i">{{ a }}</li>
          </ul>
          <div v-else class="empty-hint">暂无建议</div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped>
.analysis-page { max-width: 900px; margin: 0 auto; padding: 28px 24px; }
.page-header { margin-bottom: 24px; text-align: center; }
.page-header h1 { font-size: 26px; color: #4a7c6f; margin: 0 0 6px 0; font-weight: 700; }
.subtitle { color: #909399; font-size: 14px; margin: 0; }
.upload-card { border-radius: 14px; }
.result-area { animation: fade-in-up 0.4s ease-out; }
.report-section { white-space: pre-wrap; line-height: 1.8; font-size: 15px; color: #303133; padding: 16px; background: #fafcfa; border-radius: 10px; }
.empty-hint { text-align: center; color: #909399; padding: 32px; }
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
