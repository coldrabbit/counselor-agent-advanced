import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

interface User {
  id: string; name: string; role: string; college: string;
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)
  const loading = ref(false)

  function setAuth(t: string, u: User) {
    token.value = t
    user.value = u
    localStorage.setItem('token', t)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  async function checkAuth() {
    if (!token.value) return false
    try {
      const resp = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      user.value = resp.data
      return true
    } catch {
      logout()
      return false
    }
  }

  async function login(name: string, password: string) {
    loading.value = true
    try {
      const resp = await axios.post('/api/auth/login', { name, password })
      setAuth(resp.data.token, resp.data.user)
      return true
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || '登录失败')
    } finally { loading.value = false }
  }

  async function register(name: string, password: string, college: string) {
    loading.value = true
    try {
      const resp = await axios.post('/api/auth/register', { name, password, college })
      setAuth(resp.data.token, resp.data.user)
      return true
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || '注册失败')
    } finally { loading.value = false }
  }

  return { token, user, loading, login, register, logout, checkAuth }
})
