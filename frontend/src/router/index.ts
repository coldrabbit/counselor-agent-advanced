import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'notice-generator',
      component: () => import('../pages/NoticeGenerator.vue'),
    },
    {
      path: '/talk-record',
      name: 'talk-record',
      component: () => import('../pages/TalkRecordGenerator.vue'),
    },
    {
      path: '/students',
      name: 'students',
      component: () => import('../pages/StudentManagement.vue'),
    },
  ],
})

export default router
