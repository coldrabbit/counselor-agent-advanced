import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('../pages/Login.vue'), meta: { guest: true } },
    { path: '/', name: 'notice-generator', component: () => import('../pages/NoticeGenerator.vue'), meta: { auth: true } },
    { path: '/talk-record', name: 'talk-record', component: () => import('../pages/TalkRecordGenerator.vue'), meta: { auth: true } },
    { path: '/students', name: 'students', component: () => import('../pages/StudentManagement.vue'), meta: { auth: true } },
    { path: '/risks', name: 'risks', component: () => import('../pages/RiskDashboard.vue'), meta: { auth: true } },
    { path: '/analysis', name: 'analysis', component: () => import('../pages/AcademicAnalysis.vue'), meta: { auth: true } },
    { path: '/documents', name: 'documents', component: () => import('../pages/KnowledgeBase.vue'), meta: { auth: true } },
    { path: '/activities', name: 'activities', component: () => import('../pages/ActivityPlanner.vue'), meta: { auth: true } },
    { path: '/employment', name: 'employment', component: () => import('../pages/EmploymentTracker.vue'), meta: { auth: true } },
  ],
})

// 路由守卫
import { useAuthStore } from '../stores/auth'

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // 首次加载时检查 token 是否有效
  if (!auth.user && auth.token) {
    await auth.checkAuth()
  }

  if (to.meta.auth && !auth.user) {
    return '/login'
  }
  if (to.meta.guest && auth.user) {
    return '/'
  }
})

export default router
