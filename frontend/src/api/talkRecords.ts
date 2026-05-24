import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export interface GenerateTalkRecordRequest {
  student_name: string
  student_id: string
  situation: string
}

export interface TalkRecordResponse {
  id: string
  student_name: string
  student_id: string
  situation: string
  conversation_record: string
  risk_level: string
  follow_up_advice: string
  parent_advice: string
  status: string
  created_by: string
  created_at: string
  updated_at: string
}

export interface TalkRecordListItem {
  id: string
  student_name: string
  risk_level: string
  status: string
  created_at: string
}

export function generateTalkRecord(data: GenerateTalkRecordRequest) {
  return client.post<TalkRecordResponse>('/talk-records/generate', data)
}

export function listTalkRecords() {
  return client.get<TalkRecordListItem[]>('/talk-records')
}

export function getTalkRecord(id: string) {
  return client.get<TalkRecordResponse>(`/talk-records/${id}`)
}

export function approveTalkRecord(id: string) {
  return client.put<TalkRecordResponse>(`/talk-records/${id}/approve`)
}

export function rejectTalkRecord(id: string) {
  return client.put<TalkRecordResponse>(`/talk-records/${id}/reject`)
}
