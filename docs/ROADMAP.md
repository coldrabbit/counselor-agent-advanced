# Counselor OS — Development Roadmap

## 总体路线

```
Phase 1         Phase 2          Phase 3          Phase 4          Phase 5
[ MVP ]    →   [ 增强 ]     →   [ 引擎 ]     →   [ 集成 ]     →   [ 智能 ]
 Notify        Templates        Risk Engine      MCP Tools        RAG
 Generator     Batch Ops        Talk Records     WeChat           Multi-Agent
               Student Mgmt     Analysis         OCR/PDF          LangGraph
               Login/Auth       Workflow Engine  Approval Flow    Long Running
```

---

## Phase 1: AI Software Factory + Notification MVP（当前）

**时间**: 2026 Q2

### 目标

1. 建立 AI 软件工厂流水线（Planner → Builder → QA → Reviewer）
2. 完成通知生成器 MVP

### AI 工厂建设

- [x] Agent 角色定义 (Planner/Builder/QA/Reviewer)
- [x] Agent prompt 模板
- [x] Artifact 规范 (SPEC/TASKS/QA_REPORT/REVIEW)
- [ ] Gate 自动化 (lint/typecheck/test/build)
- [ ] 自动修复循环 (max 3 rounds)

### 通知生成器

- [x] 事件输入界面
- [x] AI 生成 4 种通知格式
- [x] 辅导员审核界面
- [x] 通知保存到 PostgreSQL
- [x] 工作流状态跟踪
- [ ] 微信通知发送 (Hermes 接入)

### 基础设施

- [x] FastAPI 后端框架
- [x] PostgreSQL 数据库 + Alembic 迁移
- [x] DeepSeek API 集成
- [x] Docker Compose 部署
- [ ] CI/CD 流水线

### 不在此阶段

- LangGraph / 多 Agent 系统
- RAG / 向量数据库
- 自主规划
- 微服务 / K8s
- 事件驱动架构

---

## Phase 2: 模板与批量操作

**时间**: 2026 Q3

### 目标

- 通知模板库管理
- Excel 批量导入学生数据
- 批量通知生成
- 学生数据管理完善
- 模板 CRUD

### 已有基础

- [x] 通知模板表
- [x] Excel 导入/导出
- [x] 学生管理 CRUD
- [x] 批量通知生成接口
- [x] 用户登录注册 (JWT)

### 待完成

- [ ] 模板版本管理
- [ ] 批量操作进度追踪
- [ ] 导入错误处理与回滚

---

## Phase 3: 风险预警与工作流引擎

**时间**: 2026 Q4

### 目标

- 风险预警引擎完善
- 谈心谈话记录系统
- 学情分析报告
- 工作流引擎增强 (checkpoint/resume)

### 已有基础

- [x] 风险记录表
- [x] 谈心谈话记录表
- [x] 学情分析接口
- [x] StateGraph 工作流引擎
- [x] 条件分支与 checkpoint

### 待完成

- [ ] 风险评分算法优化
- [ ] 自动风险触发规则
- [ ] 工作流可视化监控
- [ ] 恢复点自动保存

---

## Phase 4: MCP 工具与外部集成

**时间**: 2027 Q1

### 目标

- MCP Tool System 扩展
- 企业微信接入
- OCR 识别
- PDF 导出完善
- 审批流完善

### 已有基础

- [x] MCP Tool Registry
- [x] 内置工具 (student lookup/risk overview/class listing)
- [x] OCR 接口 (Tesseract)
- [x] PDF 导出
- [x] 审批时间戳

### 待完成

- [ ] 企业微信 Bot 接入
- [ ] MCP 外部工具扩展
- [ ] OCR 识别准确率优化
- [ ] 审批流多级审核

---

## Phase 5: 智能增强

**时间**: 2027 Q2+

### 目标

- RAG 知识库
- 多 Agent 协作
- LangGraph 集成
- 长期运行工作流
- Durable Execution

### 已有基础

- [x] RAG 知识库基础
- [x] 多 Agent 定义
- [x] LangGraph 占位

### 待规划

- [ ] RAG 向量检索升级
- [ ] Agent 间通信协议
- [ ] 长时间任务恢复
- [ ] 分布式任务执行

---

## AI 工厂成熟度模型

| 等级 | 名称 | 特征 |
|------|------|------|
| L1 | Manual | 人工写代码 + 人工测试 + 人工合并 |
| L2 | Assisted | AI 辅助编码 + 人工审查 |
| L3 | Gated | **← 当前目标** SPEC → BUILD → QA → REVIEW → Human Merge |
| L4 | Automated | 自动 Gate + 自动修复 + 人工最终确认 |
| L5 | Autonomous | 自动规划 + 自动实现 + 自动合并 (需 Human 设定边界) |

当前从 L1 向 L3 过渡。Phase 1 目标达到 L3。
