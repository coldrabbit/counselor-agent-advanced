<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface RiskItem {
  id: string; student_id: string; student_name: string; student_code: string;
  risk_level: string; reason: string; status: string; created_at: string;
}
interface RiskStats { high: number; medium: number; low: number; total: number }

const stats = ref<RiskStats>({ high: 0, medium: 0, low: 0, total: 0 })
const risks = ref<RiskItem[]>([])
const loading = ref(false)
const filterLevel = ref('')
const filterStatus = ref('')

const statusLabels: Record<string, string> = {
  NEW: '新发现', REVIEWING: '审核中', INTERVIEWED: '已谈话',
  PARENT_CONTACTED: '已联系家长', FOLLOWING: '跟进中', RESOLVED: '已解决',
}
const statusOptions = Object.entries(statusLabels).map(([k, v]) => ({ value: k, label: v }))
const nextStatus: Record<string, string> = {
  NEW: 'REVIEWING', REVIEWING: 'INTERVIEWED', INTERVIEWED: 'PARENT_CONTACTED',
  PARENT_CONTACTED: 'FOLLOWING', FOLLOWING: 'RESOLVED',
}

async function fetchData() {
  loading.value = true
  try {
    const [statsResp, risksResp] = await Promise.all([
      axios.get('/api/risks/stats'),
      axios.get('/api/risks', { params: { risk_level: filterLevel.value || undefined, status: filterStatus.value || undefined } }),
    ])
    stats.value = statsResp.data
    risks.value = risksResp.data
  } finally { loading.value = false }
}

async function advanceStatus(risk: RiskItem) {
  const next = nextStatus[risk.status]
  if (!next) return
  await axios.put(`/api/risks/${risk.id}`, { status: next })
  await fetchData()
}

async function resolveRisk(risk: RiskItem) {
  await axios.put(`/api/risks/${risk.id}`, { status: 'RESOLVED' })
  await fetchData()
}

function levelTagType(l: string) { return l === 'high' ? 'danger' : l === 'medium' ? 'warning' : 'success' }
function levelLabel(l: string) { return l === 'high' ? '高' : l === 'medium' ? '中' : '低' }

onMounted(fetchData)
</script>

<template>
  <div class="risk-page">
    <header class="page-header">
      <h1>风险预警</h1>
      <p class="subtitle">监控学生风险状态，及时跟进处理</p>
    </header>

    <!-- Stats Cards -->
    <div class="stats-row">
      <div class="stat-card high"><div class="num">{{ stats.high }}</div><div class="label">高风险</div></div>
      <div class="stat-card medium"><div class="num">{{ stats.medium }}</div><div class="label">中风险</div></div>
      <div class="stat-card low"><div class="num">{{ stats.low }}</div><div class="label">低风险</div></div>
      <div class="stat-card total"><div class="num">{{ stats.total }}</div><div class="label">总计</div></div>
    </div>

    <!-- Filters -->
    <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
      <el-select v-model="filterLevel" placeholder="风险等级" clearable style="width:140px" @change="fetchData">
        <el-option label="高风险" value="high" />
        <el-option label="中风险" value="medium" />
        <el-option label="低风险" value="low" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="处理状态" clearable style="width:160px" @change="fetchData">
        <el-option v-for="o in statusOptions" :key="o.value" :label="o.label" :value="o.value" />
      </el-select>
    </div>

    <!-- Risk Table -->
    <el-table :data="risks" v-loading="loading" class="risk-table">
      <el-table-column prop="student_name" label="学生" width="100" />
      <el-table-column prop="student_code" label="学号" width="120" />
      <el-table-column label="风险等级" width="100">
        <template #default="{ row }">
          <el-tag :type="levelTagType(row.risk_level)" size="small">{{ levelLabel(row.risk_level) }}风险</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reason" label="原因" min-width="160" show-overflow-tooltip />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ statusLabels[row.status] || row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" />
      <el-table-column label="操作" width="240">
        <template #default="{ row }">
          <el-button v-if="nextStatus[row.status]" size="small" type="primary" @click="advanceStatus(row)">
            推进: {{ statusLabels[nextStatus[row.status]] }}
          </el-button>
          <el-button v-if="row.status !== 'RESOLVED'" size="small" type="success" @click="resolveRisk(row)">已解决</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.risk-page { max-width: 1100px; margin: 0 auto; padding: 28px 24px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 26px; color: #4a7c6f; margin: 0 0 6px 0; font-weight: 700; }
.subtitle { color: #909399; font-size: 14px; margin: 0; }
.stats-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.stat-card { flex: 1; min-width: 140px; padding: 20px; border-radius: 14px; text-align: center; }
.stat-card.high { background: #fef0f0; border: 1px solid #fbc4c4; }
.stat-card.medium { background: #fdf6ec; border: 1px solid #f5dab1; }
.stat-card.low { background: #f0f9f4; border: 1px solid #b7e4cf; }
.stat-card.total { background: #f5f7fa; border: 1px solid #e8edf2; }
.stat-card .num { font-size: 36px; font-weight: 800; color: #303133; }
.stat-card .label { font-size: 13px; color: #909399; margin-top: 4px; }
.risk-table { border-radius: 12px; overflow: hidden; }
</style>
