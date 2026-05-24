<script setup lang="ts">
</script>

<template>
  <div class="app">
    <nav class="app-nav">
      <router-link to="/">通知生成器</router-link>
      <router-link to="/talk-record">谈心谈话</router-link>
      <router-link to="/students">学生管理</router-link>
      <router-link to="/risks">风险预警</router-link>
      <router-link to="/analysis">学情分析</router-link>
    </nav>
    <router-view />
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
  min-height: 100vh;
}
</style>

<style scoped>
.app-nav {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #7ec8a0 0%, #6db3b8 50%, #7ea8c8 100%);
  box-shadow: 0 3px 12px rgba(126, 168, 160, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-nav::before {
  content: 'Counselor OS';
  font-weight: 800;
  font-size: 16px;
  color: #fff;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.app-nav a {
  padding: 7px 20px;
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.25s ease;
}

.app-nav a:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.12);
}

.app-nav a.router-link-active {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
  font-weight: 600;
  backdrop-filter: blur(4px);
}
</style>
