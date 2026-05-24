import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  generateNotice, listNotices, getNotice, approveNotice, rejectNotice,
  getCounselorProfile, saveCounselorProfile,
  type NoticeResponse, type NoticeListItem, type CounselorProfile,
} from '../api/notices'

export const useNoticeStore = defineStore('notice', () => {
  const currentNotice = ref<NoticeResponse | null>(null)
  const notices = ref<NoticeListItem[]>([])
  const loading = ref(false)
  const error = ref('')
  const profile = ref<CounselorProfile | null>(null)

  async function generate(event: string, time?: string, location?: string, participants?: string) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await generateNotice({ event, time, location, participants })
      currentNotice.value = data
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
      const { data } = await approveNotice(id)
      currentNotice.value = data
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
      const { data } = await rejectNotice(id)
      currentNotice.value = data
      return data
    } catch (e: any) {
      const msg = e.response?.data?.detail || e.message || '驳回失败'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchNotices() {
    loading.value = true
    try {
      const { data } = await listNotices()
      notices.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchNotice(id: string) {
    loading.value = true
    try {
      const { data } = await getNotice(id)
      currentNotice.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchProfile() {
    try {
      const { data } = await getCounselorProfile()
      profile.value = data
    } catch {
      profile.value = null
    }
  }

  async function saveProfile(p: CounselorProfile) {
    loading.value = true
    try {
      const { data } = await saveCounselorProfile(p)
      profile.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  return {
    currentNotice, notices, loading, error, profile,
    generate, approve, reject, fetchNotices, fetchNotice, fetchProfile, saveProfile,
  }
})
