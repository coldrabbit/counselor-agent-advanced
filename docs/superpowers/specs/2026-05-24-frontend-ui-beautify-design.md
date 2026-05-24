# 前端 UI 美化设计文档

**日期**：2026-05-24
**状态**：已确认
**版本**：1.0

---

## 目标

将前端页面从 Element Plus 默认风格改造为"清新自然风"，提升视觉活泼感和专业度。

## 设计方向

- **风格**：清新自然风（柔和版）
- **配色**：青灰绿渐变主色 + 柔和中性辅助色
- **动效**：均衡动效（按钮、卡片入场、导航切换、加载状态均有轻量动画）
- **方案**：方案 B — CSS 变量覆盖 + 自定义样式，零新增依赖

## 不变更

- 不引入 Tailwind CSS 或任何新依赖
- 不改变组件结构、Props、Emits
- 不改变路由和状态管理逻辑

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/styles/variables.css` | **新建** | Element Plus CSS 变量覆盖 + 自定义设计 token |
| `src/styles/animations.css` | **新建** | 全局动画关键帧 + 工具类 |
| `src/main.ts` | 修改 | 引入 variables.css 和 animations.css |
| `src/App.vue` | 修改 | 导航栏渐变 + 胶囊标签 |
| `src/pages/NoticeGenerator.vue` | 修改 | 全页面样式刷新 |
| `src/pages/TalkRecordGenerator.vue` | 修改 | 统一配色 + 动效 |
| `src/components/CounselorDrawer.vue` | 微调 | 按钮、表单样式适配 |
| `src/components/PreGenerateDialog.vue` | 微调 | 弹窗、按钮样式适配 |

---

## 设计系统

### 配色

| Token | 值 | 用途 |
|-------|-----|------|
| `--el-color-primary` | `#7ec8a0` | 主色（青灰绿） |
| `--el-color-primary-light-3` | `#a5dbbf` | 浅主色 |
| `--el-color-primary-light-5` | `#bfe5d2` | 更浅主色 |
| `--el-color-primary-dark-2` | `#5daa80` | 深主色 |
| `--el-bg-color-page` | `#f5f7fa` | 页面背景 |
| `--el-border-color-base` | `#dce8e3` | 边框色 |
| `--el-border-color-light` | `#e8edf2` | 浅边框色 |
| `--el-border-radius-base` | `10px` | 基础圆角 |
| `--el-box-shadow-light` | `0 2px 12px rgba(0,0,0,0.05)` | 卡片阴影 |

### 导航栏渐变

```
background: linear-gradient(135deg, #7ec8a0 0%, #6db3b8 50%, #7ea8c8 100%);
```

### 按钮渐变

```
background: linear-gradient(135deg, #7ec8a0, #6db3b8);
```

---

## 动画定义

| 动画名 | 用途 | 时长 |
|--------|------|------|
| `fade-in-up` | 卡片/结果区域入场，从下方 16px 淡入 | 0.4s |
| `hover-lift` | 按钮悬停上浮 2px + 阴影增强 | 0.25s |
| `pulse-glow` | 加载状态脉冲发光环 | 1.5s 循环 |
| `spin` | 旋转加载指示器 | 0.8s 循环 |
| `wave` | 三点波浪加载动画 | 1.2s 循环 |

---

## 各组件改动要点

### App.vue — 导航栏

- 背景从白色 → 青绿渐变
- 路由链接从蓝底方块 → 白色半透明胶囊切换器
- 增加 `position: sticky; top: 0; z-index: 100` 吸顶效果
- `router-link-active` 高亮态：白色半透明底 + 粗体

### NoticeGenerator.vue

- 输入卡片：圆角 14px，柔和阴影，标题加 📝 emoji
- 生成按钮：渐变背景 + 圆角 20px + 悬停上浮 `hover-lift`
- 标签页：选中态颜色映射主色，底部指示器圆角胶囊
- 结果区：卡片 `fade-in-up` 入场动画
- 设置按钮：齿轮改用 Element Plus 图标，hover 旋转
- 审核按钮：主色自动映射，无需额外处理

### TalkRecordGenerator.vue

- 与 NoticeGenerator 统一配色和圆角
- 风险标签保留 low/mid/high 映射逻辑，颜色适配新体系
- 结果选项卡入场动画

### CounselorDrawer.vue

- 保存按钮使用主色渐变
- 表单标签色柔和化

### PreGenerateDialog.vue

- 弹窗入场 `scale-in` 动画
- 确认按钮渐变统一

---

## 实施顺序

1. 新建 `src/styles/variables.css`
2. 新建 `src/styles/animations.css`
3. 修改 `src/main.ts` 引入样式
4. 修改 `src/App.vue` 导航栏
5. 修改 `src/pages/NoticeGenerator.vue`
6. 修改 `src/pages/TalkRecordGenerator.vue`
7. 微调 `src/components/CounselorDrawer.vue`
8. 微调 `src/components/PreGenerateDialog.vue`

---

## 成功标准

- [ ] 两个页面的导航栏显示渐变背景 + 胶囊切换器
- [ ] 按钮悬停时有上浮动效
- [ ] 卡片/结果区入场有淡入动效
- [ ] 加载状态显示波浪点动画
- [ ] 所有 Element Plus 组件配色自动适配新主色
- [ ] 谈心谈话页面风格与通知生成器统一
- [ ] 无控制台报错
- [ ] 构建成功
