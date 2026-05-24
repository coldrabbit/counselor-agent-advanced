# 前端 UI 美化 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将前端从 Element Plus 默认灰白风格改造为"清新自然风"，包含柔和青绿配色和均衡动效。

**架构：** 方案 B — CSS 变量覆盖 Element Plus 默认主题 + 独立动画样式文件 + 逐组件重写 scoped 样式。零新增依赖，不改组件结构。

**技术栈：** Vue 3 + Element Plus + 纯 CSS（无预处理器）

---

### 任务 1：创建 CSS 变量覆盖文件

**文件：**
- 创建：`frontend/src/styles/variables.css`

- [ ] **步骤 1：编写 Element Plus CSS 变量覆盖**

```css
/* Element Plus 主题变量覆盖 — 清新自然风 */
:root {
  /* 主色 — 青灰绿 */
  --el-color-primary: #7ec8a0;
  --el-color-primary-light-1: #8dd0ad;
  --el-color-primary-light-2: #9ad7b7;
  --el-color-primary-light-3: #a5dbbf;
  --el-color-primary-light-4: #b2e0c8;
  --el-color-primary-light-5: #bfe5d2;
  --el-color-primary-light-6: #ccebdb;
  --el-color-primary-light-7: #d9f0e4;
  --el-color-primary-light-8: #e5f5ed;
  --el-color-primary-light-9: #f2faf6;
  --el-color-primary-dark-2: #5daa80;

  /* 成功色 — 保留绿色调 */
  --el-color-success: #67c23a;
  --el-color-success-light-3: #95d475;
  --el-color-success-light-5: #b3e19d;

  /* 警告色 */
  --el-color-warning: #e6a23c;
  --el-color-warning-light-3: #eebe77;
  --el-color-warning-light-5: #f3d19e;

  /* 危险色 */
  --el-color-danger: #f56c6c;
  --el-color-danger-light-3: #f89898;
  --el-color-danger-light-5: #fab6b6;

  /* 信息色 */
  --el-color-info: #909399;

  /* 背景 */
  --el-bg-color-page: #f5f7fa;
  --el-bg-color: #ffffff;
  --el-bg-color-overlay: #ffffff;

  /* 文字 */
  --el-text-color-primary: #303133;
  --el-text-color-regular: #606266;
  --el-text-color-secondary: #909399;
  --el-text-color-placeholder: #a8abb2;

  /* 边框 */
  --el-border-color-base: #dce8e3;
  --el-border-color-light: #e8edf2;
  --el-border-color-lighter: #edf2f0;
  --el-border-color-extra-light: #f2f6f5;

  /* 圆角 */
  --el-border-radius-base: 10px;
  --el-border-radius-small: 6px;
  --el-border-radius-round: 20px;

  /* 阴影 */
  --el-box-shadow-light: 0 2px 12px rgba(0, 0, 0, 0.05);
  --el-box-shadow-lighter: 0 2px 8px rgba(0, 0, 0, 0.03);
  --el-box-shadow-dark: 0 4px 16px rgba(0, 0, 0, 0.08);

  /* 字体 */
  --el-font-size-extra-large: 20px;
  --el-font-size-large: 18px;
  --el-font-size-medium: 16px;
  --el-font-size-base: 14px;
  --el-font-size-small: 13px;
  --el-font-size-extra-small: 12px;
}
```

- [ ] **步骤 2：确认文件存在**

运行：`ls -la frontend/src/styles/variables.css`
预期：文件已创建

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/styles/variables.css
git commit -m "feat: add CSS variable overrides for fresh natural theme"
```

---

### 任务 2：创建全局动画样式文件

**文件：**
- 创建：`frontend/src/styles/animations.css`

- [ ] **步骤 1：编写动画关键帧和工具类**

```css
/* 全局动画 — 清新自然风均衡动效 */

/* 卡片从下淡入 */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 按钮悬停上浮 */
@keyframes hover-lift {
  to {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(126, 168, 160, 0.25);
  }
}

/* 脉冲发光 */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(126, 168, 160, 0.2);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(126, 168, 160, 0);
  }
}

/* 旋转 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 波浪点 */
@keyframes wave {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 弹窗缩放入场 */
@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 工具类 */
.anim-fade-in-up {
  animation: fade-in-up 0.4s ease-out both;
}

.anim-hover-lift {
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.anim-hover-lift:hover {
  animation: hover-lift 0.25s ease forwards;
}

.anim-pulse-glow {
  animation: pulse-glow 1.5s ease-in-out infinite;
}

.anim-scale-in {
  animation: scale-in 0.3s ease-out both;
}

/* 加载波浪点 */
.wave-dots {
  display: flex;
  gap: 6px;
  justify-content: center;
  align-items: center;
}
.wave-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--el-color-primary);
  animation: wave 1.2s ease-in-out infinite;
}
.wave-dots span:nth-child(2) {
  animation-delay: 0.2s;
}
.wave-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

/* 旋转加载环 */
.spinner {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid var(--el-border-color-light);
  border-top-color: var(--el-color-primary);
  animation: spin 0.8s linear infinite;
}
```

- [ ] **步骤 2：确认文件存在**

运行：`ls -la frontend/src/styles/animations.css`
预期：文件已创建

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/styles/animations.css
git commit -m "feat: add global animation keyframes and utility classes"
```

---

### 任务 3：修改 main.ts 引入样式文件

**文件：**
- 修改：`frontend/src/main.ts`

- [ ] **步骤 1：在 element-plus CSS 之后引入自定义样式**

将：
```ts
import 'element-plus/dist/index.css'
```

替换为：
```ts
import 'element-plus/dist/index.css'
import './styles/variables.css'
import './styles/animations.css'
```

修改后的完整文件：

```ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/variables.css'
import './styles/animations.css'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

const app = createApp(App)
app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **步骤 2：验证构建**

运行：`cd frontend && npm run build`
预期：构建成功，无 CSS 相关报错

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/main.ts
git commit -m "feat: import custom CSS variables and animations"
```

---

### 任务 4：重写 App.vue 导航栏样式

**文件：**
- 修改：`frontend/src/App.vue`（仅替换 `<style>` 和 `<style scoped>` 块，template 和 script 不变）

- [ ] **步骤 1：替换全局 body 样式和导航栏样式**

将现有两个 style 块替换为：

```css
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
```

- [ ] **步骤 2：验证构建**

运行：`cd frontend && npm run build`
预期：构建成功

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat: redesign navigation bar with gradient and pill tabs"
```

---

### 任务 5：重写 NoticeGenerator.vue 页面样式

**文件：**
- 修改：`frontend/src/pages/NoticeGenerator.vue`（仅替换 `<style scoped>` 块，template 和 script 不变）

- [ ] **步骤 1：替换页面样式**

```css
<style scoped>
.notice-generator {
  max-width: 900px;
  margin: 0 auto;
  padding: 28px 24px;
}

.page-header {
  margin-bottom: 28px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-row h1 {
  font-size: 26px;
  color: #4a7c6f;
  margin: 0 0 6px 0;
  font-weight: 700;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.profile-hint {
  margin: 14px 0 0 0;
  padding: 10px 14px;
  background: #fdf6ec;
  color: #e6a23c;
  border-radius: 8px;
  font-size: 13px;
  border: 1px solid #faecd8;
}

.input-card {
  margin-bottom: 24px;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.input-card :deep(.el-card__header) {
  font-weight: 600;
  color: #4a7c6f;
  font-size: 15px;
}

.input-card :deep(.el-textarea__inner) {
  border-radius: 10px;
  background: #f8faf9;
  border-color: #dce8e3;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.input-card :deep(.el-textarea__inner:focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
}

.generate-btn {
  margin-top: 16px;
  width: 100%;
  border-radius: 20px;
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border: none;
  font-weight: 600;
  font-size: 15px;
  height: 44px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(126, 168, 160, 0.3);
}

.generate-btn :deep(.el-button) {
  background: transparent;
}

.result-section {
  margin-top: 28px;
  animation: fade-in-up 0.4s ease-out;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}

.result-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.notice-tabs {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
}

.notice-tabs :deep(.el-tabs__item.is-active) {
  color: #4a7c6f;
  font-weight: 600;
}

.notice-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border-radius: 2px;
}

.notice-content {
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
  min-height: 200px;
  padding: 20px;
  background: #fafcfa;
  border-radius: 10px;
  border: 1px solid #edf2f0;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.actions :deep(.el-button--success) {
  border-radius: 20px;
  font-weight: 600;
}
</style>
```

- [ ] **步骤 2：验证构建**

运行：`cd frontend && npm run build`
预期：构建成功

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/pages/NoticeGenerator.vue
git commit -m "feat: refresh NoticeGenerator page with fresh natural style"
```

---

### 任务 6：重写 TalkRecordGenerator.vue 页面样式

**文件：**
- 修改：`frontend/src/pages/TalkRecordGenerator.vue`（仅替换 `<style scoped>` 块，template 和 script 不变）

- [ ] **步骤 1：替换页面样式**

```css
<style scoped>
.talk-record-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 28px 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 28px;
}

.page-header h1 {
  font-size: 26px;
  color: #4a7c6f;
  margin: 0 0 6px 0;
  font-weight: 700;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.input-card {
  margin-bottom: 18px;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.input-card :deep(.el-card__header) {
  font-weight: 600;
  color: #4a7c6f;
  font-size: 15px;
}

.input-card :deep(.el-input__wrapper) {
  border-radius: 10px;
  background: #f8faf9;
  border-color: #dce8e3;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.input-card :deep(.el-input__wrapper.is-focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
}

.input-card :deep(.el-textarea__inner) {
  border-radius: 10px;
  background: #f8faf9;
  border-color: #dce8e3;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.input-card :deep(.el-textarea__inner:focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
}

.generate-btn {
  margin-top: 16px;
  width: 100%;
  border-radius: 20px;
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border: none;
  font-weight: 600;
  font-size: 15px;
  height: 44px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(126, 168, 160, 0.3);
}

.result-section {
  margin-top: 28px;
  animation: fade-in-up 0.4s ease-out;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.result-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.result-badges {
  display: flex;
  gap: 8px;
}

.record-tabs {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
}

.record-tabs :deep(.el-tabs__item.is-active) {
  color: #4a7c6f;
  font-weight: 600;
}

.record-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border-radius: 2px;
}

.record-content {
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
  min-height: 200px;
  padding: 20px;
  background: #fafcfa;
  border-radius: 10px;
  border: 1px solid #edf2f0;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.actions :deep(.el-button--success) {
  border-radius: 20px;
  font-weight: 600;
}
</style>
```

- [ ] **步骤 2：验证构建**

运行：`cd frontend && npm run build`
预期：构建成功

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/pages/TalkRecordGenerator.vue
git commit -m "feat: refresh TalkRecordGenerator page with unified fresh natural style"
```

---

### 任务 7：微调 CounselorDrawer.vue 和 PreGenerateDialog.vue

**文件：**
- 修改：`frontend/src/components/CounselorDrawer.vue`
- 修改：`frontend/src/components/PreGenerateDialog.vue`

- [ ] **步骤 1：在 CounselorDrawer.vue 末尾添加 scoped 样式块**

在 `</template>` 后添加：

```css
<style scoped>
:deep(.el-drawer__header) {
  color: #4a7c6f;
  font-weight: 700;
  font-size: 16px;
}

:deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  border-radius: 10px;
  background: #f8faf9;
  transition: border-color 0.25s, box-shadow 0.25s;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
}

:deep(.el-button--primary) {
  border-radius: 20px;
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border: none;
  font-weight: 600;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(126, 168, 160, 0.3);
}
</style>
```

- [ ] **步骤 2：在 PreGenerateDialog.vue 末尾添加 scoped 样式块**

在 `</template>` 后添加：

```css
<style scoped>
:deep(.el-dialog__header) {
  color: #4a7c6f;
  font-weight: 700;
  font-size: 16px;
}

:deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  border-radius: 10px;
  background: #f8faf9;
  transition: border-color 0.25s, box-shadow 0.25s;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
}

:deep(.el-textarea__inner) {
  border-radius: 10px;
  background: #f8faf9;
  transition: border-color 0.25s, box-shadow 0.25s;
}

:deep(.el-textarea__inner:focus) {
  border-color: #7ec8a0;
  box-shadow: 0 0 0 2px rgba(126, 168, 160, 0.15);
}

:deep(.el-button--primary) {
  border-radius: 20px;
  background: linear-gradient(135deg, #7ec8a0, #6db3b8);
  border: none;
  font-weight: 600;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(126, 168, 160, 0.3);
}
</style>
```

- [ ] **步骤 3：验证构建**

运行：`cd frontend && npm run build`
预期：构建成功

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/components/CounselorDrawer.vue frontend/src/components/PreGenerateDialog.vue
git commit -m "feat: apply fresh natural style to drawer and dialog components"
```

---

### 任务 8：最终验证

- [ ] **步骤 1：完整构建**

运行：`cd frontend && npm run build`
预期：构建成功，无错误

- [ ] **步骤 2：启动开发服务器排查构建输出**

运行：`cd frontend && npm run dev`
预期：开发服务器启动，打开浏览器确认：
  - 导航栏显示青绿渐变背景 + 白色胶囊切换器
  - 按钮为渐变圆角，悬停时有上浮动效
  - 卡片为圆角 + 柔和阴影
  - 输入框聚焦时有绿色边框发光
  - 谈心谈话页面风格与通知生成器统一

- [ ] **步骤 3：阶段 Commit**

```bash
git add -A
git commit -m "chore: final verification of UI beautify changes"
```
