# Counselor OS - Claude Code Engineering Rules

# Project Overview

This project is an AI Workflow Operating System for university counselors.

The system is NOT a chatbot.

The system is a deterministic workflow-driven AI platform for counselor daily operations.

Core goals:

- workflow automation
- task execution
- student management
- risk analysis
- document generation
- workflow recovery
- human approval
- observability

The system is inspired by:

- Harness
- Temporal
- workflow orchestration systems

NOT inspired by:

- AutoGPT
- autonomous agents
- infinite-loop agents

---

# Core Engineering Principles

## 1. Workflow First

All features must be designed as:

Input
→ Processing
→ Output
→ State

Do NOT design free-form autonomous agents.

---

## 2. Task Isolation

Every task must be:

- independent
- retryable
- observable
- recoverable
- single responsibility

Never create giant agents.

Never create giant services.

---

## 3. Human In The Loop

AI can suggest.

Humans must approve critical operations.

Critical operations include:

- notifications
- parent communication
- risk escalation
- psychological content

---

## 4. Deterministic Workflow

Prefer deterministic workflows over autonomous reasoning.

Avoid:

- autonomous planning
- self-loop agents
- uncontrolled agent behavior

---

## 5. Small Iterations

Build features incrementally.

Never generate the whole system at once.

Always:

- implement
- test
- verify
- iterate

---

# Current Development Phase

CURRENT PHASE:

Notification Generator MVP

Only implement:

- notification generation
- review workflow
- task status
- PostgreSQL persistence
- DeepSeek integration

Do NOT implement:

- LangGraph
- multi-agent systems
- vector databases
- RAG
- autonomous planning
- event-driven architecture
- microservices
- kubernetes

---

# Tech Stack

Frontend:

- Vue 3
- Vite
- TypeScript
- Element Plus
- Pinia

Backend:

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic

AI:

- DeepSeek API

Deployment:

- Docker
- Railway/VPS

---

# Backend Architecture Rules

Use this structure:

backend/app/
api/
services/
tasks/
workflows/
prompts/
models/
repositories/
schemas/
db/

---

# Frontend Architecture Rules

Use this structure:

frontend/src/
pages/
components/
stores/
api/
router/

---

# AI Engineering Rules

## Prompt Management

Prompts must NOT be hardcoded inside business logic.

All prompts must be stored in:

backend/app/prompts/

---

## AI Output Rules

All AI outputs must:

- be structured
- be reviewable
- support retry
- support logging

Never allow AI to directly execute sensitive actions.

---

# Task System Rules

Every task must include:

- input
- output
- status
- retry_count
- logs
- timestamps

Supported statuses:

- PENDING
- RUNNING
- SUCCESS
- FAILED
- RETRYING
- WAITING_APPROVAL
- CANCELLED

---

# Workflow Rules

Workflows must:

- be resumable
- support state tracking
- support approval checkpoints

Never design workflows as uncontrolled loops.

---

# Database Rules

Prefer:

- normalized schema
- explicit relations
- auditability

Avoid:

- premature optimization
- overly generic schemas

---

# Code Style Rules

- use explicit typing
- keep functions small
- single responsibility only
- avoid over abstraction
- avoid magic behavior
- avoid hidden state

Maximum preferred file size:

- 300 lines

---

# Forbidden Engineering Decisions

Do NOT introduce:

- LangGraph
- CrewAI
- AutoGen
- autonomous agents
- kubernetes
- event bus
- distributed systems
- microservices
- CQRS
- DDD
- over-engineering

without explicit approval.

---

# Current Priority

Priority #1:

Build a stable Notification Generator MVP.

Success criteria:

- counselor can input event
- AI generates notification
- counselor reviews notification
- notification is saved
- workflow state is tracked

Nothing else matters yet.

---

# Claude Code Behavior Rules

Before writing code:

1. explain design briefly
2. keep implementation minimal
3. avoid speculative abstractions
4. prioritize maintainability
5. prefer explicit logic over cleverness

When uncertain:

- ask for clarification
- do NOT invent architecture

---

# Long-Term Vision

This system will eventually evolve into:

Counselor OS

including:

- workflow engine
- student risk management
- conversation records
- parent communication workflows
- activity planning
- employment management
- AI memory
- MCP tool integrations

BUT:
Do not build future abstractions prematurely.
Build only what is required now.

<!-- superpowers-zh:begin (do not edit between these markers) -->
# Superpowers-ZH 中文增强版

本项目已安装 superpowers-zh 技能框架（20 个 skills）。

## 核心规则

1. **收到任务时，先检查是否有匹配的 skill** — 哪怕只有 1% 的可能性也要检查
2. **设计先于编码** — 收到功能需求时，先用 brainstorming skill 做需求分析
3. **测试先于实现** — 写代码前先写测试（TDD）
4. **验证先于完成** — 声称完成前必须运行验证命令

## 可用 Skills

Skills 位于 `.claude/skills/` 目录，每个 skill 有独立的 `SKILL.md` 文件。

- **brainstorming**: 在任何创造性工作之前必须使用此技能——创建功能、构建组件、添加功能或修改行为。在实现之前先探索用户意图、需求和设计。
- **chinese-code-review**: 中文 review 沟通参考——话术模板、分级标注（必须修复/建议修改/仅供参考）、国内团队常见反模式应对。仅在用户显式 /chinese-code-review 时调用，不要根据上下文自动触发。
- **chinese-commit-conventions**: 中文 commit 与 changelog 配置参考——Conventional Commits 中文适配、commitlint/husky/commitizen 中文模板、conventional-changelog 中文配置。仅在用户显式 /chinese-commit-conventions 时调用，不要根据上下文自动触发。
- **chinese-documentation**: 中文文档排版参考——中英文空格、全半角标点、术语保留、链接格式、中文文案排版指北约定。仅在用户显式 /chinese-documentation 时调用，不要根据上下文自动触发。
- **chinese-git-workflow**: 国内 Git 平台配置参考——Gitee、Coding.net、极狐 GitLab、CNB 的 SSH/HTTPS/凭据/CI 接入差异与镜像同步配置。仅在用户显式 /chinese-git-workflow 时调用，不要根据上下文自动触发。
- **dispatching-parallel-agents**: 当面对 2 个以上可以独立进行、无共享状态或顺序依赖的任务时使用
- **executing-plans**: 当你有一份书面实现计划需要在单独的会话中执行，并设有审查检查点时使用
- **finishing-a-development-branch**: 当实现完成、所有测试通过、需要决定如何集成工作时使用——通过提供合并、PR 或清理等结构化选项来引导开发工作的收尾
- **mcp-builder**: MCP 服务器构建方法论 — 系统化构建生产级 MCP 工具，让 AI 助手连接外部能力
- **receiving-code-review**: 收到代码审查反馈后、实施建议之前使用，尤其当反馈不明确或技术上有疑问时——需要技术严谨性和验证，而非敷衍附和或盲目执行
- **requesting-code-review**: 完成任务、实现重要功能或合并前使用，用于验证工作成果是否符合要求
- **subagent-driven-development**: 当在当前会话中执行包含独立任务的实现计划时使用
- **systematic-debugging**: 遇到任何 bug、测试失败或异常行为时使用，在提出修复方案之前执行
- **test-driven-development**: 在实现任何功能或修复 bug 时使用，在编写实现代码之前
- **using-git-worktrees**: 当需要开始与当前工作区隔离的功能开发，或在执行实现计划之前使用——通过原生工具或 git worktree 回退机制确保隔离工作区存在
- **using-superpowers**: 在开始任何对话时使用——确立如何查找和使用技能，要求在任何响应（包括澄清性问题）之前调用 Skill 工具
- **verification-before-completion**: 在宣称工作完成、已修复或测试通过之前使用，在提交或创建 PR 之前——必须运行验证命令并确认输出后才能声称成功；始终用证据支撑断言
- **workflow-runner**: 在 Claude Code / OpenClaw / Cursor 中直接运行 agency-orchestrator YAML 工作流——无需 API key，使用当前会话的 LLM 作为执行引擎。当用户提供 .yaml 工作流文件或要求多角色协作完成任务时触发。
- **writing-plans**: 当你有规格说明或需求用于多步骤任务时使用，在动手写代码之前
- **writing-skills**: 当创建新技能、编辑现有技能或在部署前验证技能是否有效时使用

## 如何使用

当任务匹配某个 skill 时，使用 `Skill` 工具加载对应 skill 并严格遵循其流程。绝不要用 Read 工具读取 SKILL.md 文件。

如果你认为哪怕只有 1% 的可能性某个 skill 适用于你正在做的事情，你必须调用该 skill 检查。
<!-- superpowers-zh:end -->
