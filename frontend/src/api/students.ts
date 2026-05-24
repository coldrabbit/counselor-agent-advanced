import axios from 'axios'

export interface ClassItem {
  id: string
  name: string
  grade: string
  major: string
}

export interface StudentItem {
  id: string
  name: string
  student_id: string
  class_id: string | null
  phone: string
  risk_level: string
  created_at: string | null
  updated_at: string | null
}

export interface StudentCreate {
  name: string
  student_id: string
  class_id: string | null
  phone: string
  risk_level: string
}

export interface StudentUpdate {
  name?: string
  student_id?: string
  class_id?: string | null
  phone?: string
  risk_level?: string
}

export function listClasses(): Promise<ClassItem[]> {
  return axios.get('/api/classes').then(r => r.data)
}

export function createClass(data: { name: string; grade?: string; major?: string }): Promise<ClassItem> {
  return axios.post('/api/classes', data).then(r => r.data)
}

export function listStudents(params?: { class_id?: string; search?: string }): Promise<StudentItem[]> {
  return axios.get('/api/students', { params }).then(r => r.data)
}

export function createStudent(data: StudentCreate): Promise<StudentItem> {
  return axios.post('/api/students', data).then(r => r.data)
}

export function updateStudent(id: string, data: StudentUpdate): Promise<StudentItem> {
  return axios.put(`/api/students/${id}`, data).then(r => r.data)
}

export function deleteStudent(id: string): Promise<void> {
  return axios.delete(`/api/students/${id}`)
}
