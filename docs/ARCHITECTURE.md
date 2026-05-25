# Counselor OS — System Architecture

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Software Factory                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Planner  │  │ Builder  │  │   QA     │  │ Reviewer │   │
│  │ (Claude) │→│ (Codex)  │→│(OpenCode)│→│ (Claude) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│       │              │              │              │         │
│       ▼              ▼              ▼              ▼         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Artifact Store (.agent/)                │   │
│  │  tasks/{id}/SPEC.md  TASKS.md                        │   │
│  │  reports/{id}/QA_REPORT.md  REVIEW.md                │   │
│  │  status/current.json                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Counselor OS Runtime                       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Vue 3   │  │  FastAPI │  │PostgreSQL│  │ DeepSeek │   │
│  │ Frontend │→│ Backend  │→│ Database │  │    AI    │   │
│  │  :80     │  │  :8000   │  │  :5432   │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Workflow Engine                      │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │   │
│  │  │ Notice │ │  Talk  │ │  Risk  │ │Activity│        │   │
│  │  │  Gen   │ │ Record │ │Analysis│ │ Plan   │        │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 技术栈

### Frontend (frontend/)

| 层 | 技术 |
|----|------|
| 框架 | Vue 3 (Composition API) |
| 构建 | Vite |
| 语言 | TypeScript |
| UI 库 | Element Plus |
| 状态管理 | Pinia |
| 路由 | Vue Router |

目录结构：

```
frontend/src/
├── pages/           # 页面组件
├── components/      # 可复用组件
├── stores/          # Pinia stores
├── api/             # HTTP 请求封装
├── router/          # 路由配置
└── styles/          # 全局样式
```

### Backend (backend/)

| 层 | 技术 |
|----|------|
| 框架 | FastAPI |
| ORM | SQLAlchemy |
| 迁移 | Alembic |
| 数据库 | PostgreSQL |
| AI | DeepSeek API |

目录结构：

```
backend/app/
├── api/             # FastAPI 路由
├── services/        # 业务逻辑层
│   ├── ai/          # AI 调用封装
│   └── notify/      # 通知服务
├── workflows/       # 工作流定义
├── tasks/           # 任务定义
├── prompts/         # AI Prompt 模板
├── models/          # SQLAlchemy 模型
├── schemas/         # Pydantic 模型
├── repositories/    # 数据访问层
├── agents/          # Agent 注册与定义
├── tools/           # MCP 工具系统
├── engine/          # 工作流引擎
└── db/              # 数据库配置
```

## 核心模块

### Module 1: 通知生成器 (Notice Generator) — Phase 1 MVP

```
Input → Processing → Output → State

User Input (event description)
  → AI generates 4 notice variants (formal/wechat/parent/sms)
  → Counselor reviews & edits
  → Save to database
  → Optional: Send
```

### Module 2: 谈心谈话记录 (Talk Record)

```
Student situation input
  → AI generates conversation record
  → Risk level assessment
  → Follow-up advice
  → Counselor review
  → Archive
```

### Module 3: 风险预警 (Risk Dashboard)

```
Data import (attendance/grades/leave)
  → Risk scoring
  → AI analysis report
  → Risk student list
  → Counselor confirmation
  → Track task creation
```

### Module 4: 学情分析 (Academic Analysis)

```
Excel upload
  → Data parsing
  → AI analysis
  → Report generation
  → PDF export
```

### Module 5: 活动策划 (Activity Planner)

```
Activity parameters
  → AI generates plan/schedule/speech
  → Counselor review
  → Save & export
```

### Module 6: 就业管理 (Employment Tracker)

```
Job/internship data
  → Track offers and interviews
  → Resume advice
  → Employment statistics
```

## 数据模型

```
users ────── counselors
  │
  ├── notices
  ├── talk_records
  ├── activities
  ├── employments
  ├── documents
  │
students ─── classes
  │
  ├── risk_records
  ├── conversations
  │
workflows ─── tasks
templates
```

## 工作流引擎

### 状态定义

```
PENDING → RUNNING → SUCCESS
                  → FAILED → RETRYING → RUNNING
                  → WAITING_APPROVAL → SUCCESS
                  → CANCELLED
```

### 引擎特性

- **Durable Execution**: 工作流状态持久化到 PostgreSQL
- **Checkpointing**: 每个步骤完成后保存状态，支持恢复
- **Conditional Branching**: 支持基于结果的条件分支
- **Approval Gates**: 关键操作前必须人工审核

## 部署

```
┌─────────────┐   ┌─────────────┐
│  Frontend   │   │   Backend   │
│  Container  │   │  Container  │
│   :80       │   │   :8000     │
└──────┬──────┘   └──────┬──────┘
       │                 │
       └────────┬────────┘
                │
       ┌────────┴────────┐
       │   PostgreSQL    │
       │   Container     │
       │    :5432        │
       └─────────────────┘
```

## 禁止引入的架构

以下技术在当前 Phase 明确禁止，除非经过 Planner 重新评估并获 Human 批准：

- LangGraph / LangChain
- CrewAI / AutoGen / 多 Agent 自主协作框架
- Kubernetes (k8s)
- 事件总线 / 消息队列 (RabbitMQ/Kafka)
- 微服务拆分
- CQRS / Event Sourcing
- DDD 战术模式
- 向量数据库 (Pinecone/Milvus)
- RAG (检索增强生成)
- 自主规划 Agent
