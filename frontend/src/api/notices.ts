import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export interface GenerateRequest {
  event: string
  time?: string
  location?: string
  participants?: string
}

export interface NoticeResponse {
  id: string
  title: string
  event: string
  formal_notice: string
  wechat_notice: string
  parent_notice: string
  sms_notice: string
  status: string
  created_by: string
  created_at: string
  updated_at: string
}

export interface NoticeListItem {
  id: string
  title: string
  status: string
  created_at: string
}

export interface CounselorProfile {
  id?: string
  name: string
  college: string
  phone?: string
  email?: string
}

export function generateNotice(data: GenerateRequest) {
  return client.post<NoticeResponse>('/notices/generate', data)
}

export function listNotices() {
  return client.get<NoticeListItem[]>('/notices')
}

export function getNotice(id: string) {
  return client.get<NoticeResponse>(`/notices/${id}`)
}

export function approveNotice(id: string) {
  return client.put<NoticeResponse>(`/notices/${id}/approve`)
}

export function rejectNotice(id: string) {
  return client.put<NoticeResponse>(`/notices/${id}/reject`)
}

export function getCounselorProfile() {
  return client.get<CounselorProfile | null>('/counselor/profile')
}

export function saveCounselorProfile(data: CounselorProfile) {
  return client.put<CounselorProfile>('/counselor/profile', data)
}
