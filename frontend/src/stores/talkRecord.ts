import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  generateTalkRecord, listTalkRecords, getTalkRecord, approveTalkRecord, rejectTalkRecord,
  type TalkRecordResponse, type TalkRecordListItem,
} from '../api/talkRecords'

export const useTalkRecordStore = defineStore('talkRecord', () => {
  const currentRecord = ref<TalkRecordResponse | null>(null)
  const records = ref<TalkRecordListItem[]>([])
  const loading = ref(false)
  const error = ref('')

  async function generate(studentName: string, studentId: string, situation: string) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await generateTalkRecord({
        student_name: studentName,
        student_id: studentId,
        situation,
      })
      currentRecord.value = data
      return data
    } catch (e: any) {
      const msg = e.response?.data?.detail || e.message || '生成失败'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  async function approve(id: string) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await approveTalkRecord(id)
      currentRecord.value = data
      return data
    } catch (e: any) {
      const msg = e.response?.data?.detail || e.message || '审核失败'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  async function reject(id: string) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await rejectTalkRecord(id)
      currentRecord.value = data
      return data
    } catch (e: any) {
      const msg = e.response?.data?.detail || e.message || '驳回失败'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchRecords() {
    loading.value = true
    try {
      const { data } = await listTalkRecords()
      records.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchRecord(id: string) {
    loading.value = true
    try {
      const { data } = await getTalkRecord(id)
      currentRecord.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  return {
    currentRecord, records, loading, error,
    generate, approve, reject, fetchRecords, fetchRecord,
  }
})
