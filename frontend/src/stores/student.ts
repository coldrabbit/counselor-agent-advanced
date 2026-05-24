import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  listClasses, createClass,
  listStudents, createStudent, updateStudent, deleteStudent,
  type ClassItem, type StudentItem, type StudentCreate, type StudentUpdate,
} from '../api/students'

export const useStudentStore = defineStore('student', () => {
  const classes = ref<ClassItem[]>([])
  const students = ref<StudentItem[]>([])
  const loading = ref(false)

  async function fetchClasses() {
    classes.value = await listClasses()
  }

  async function addClass(name: string, grade: string, major: string) {
    const cls = await createClass({ name, grade, major })
    classes.value.push(cls)
    ElMessage.success('班级添加成功')
    return cls
  }

  async function fetchStudents(classId?: string, search?: string) {
    loading.value = true
    try {
      students.value = await listStudents({ class_id: classId, search })
    } finally {
      loading.value = false
    }
  }

  async function addStudent(data: StudentCreate) {
    await createStudent(data)
    ElMessage.success('学生添加成功')
    await fetchStudents()
  }

  async function editStudent(id: string, data: StudentUpdate) {
    await updateStudent(id, data)
    ElMessage.success('学生更新成功')
    await fetchStudents()
  }

  async function removeStudent(id: string) {
    await deleteStudent(id)
    ElMessage.success('学生已删除')
    await fetchStudents()
  }

  return {
    classes, students, loading,
    fetchClasses, addClass,
    fetchStudents, addStudent, editStudent, removeStudent,
  }
})
