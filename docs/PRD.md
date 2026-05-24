# 辅导员 AI Agent 工作流平台 PRD（Claude Code 开发版）

# 一、项目背景

本项目目标是：

# 构建一个面向高校辅导员日常工作的 AI Agent 工作流平台（Counselor OS）

该系统基于真实《高校辅导员全周期月度工作清单》设计，覆盖：

- 大一 ~ 大四
- 全学年周期
- 安全管理
- 学风管理
- 心理健康
- 家校沟通
- 资助管理
- 实习就业
- 活动组织
- 党团建设
- 谈心谈话

系统目标不是简单聊天机器人，而是：

# 面向高校辅导员的 AI Workflow Operating System

核心能力：

- 工作流编排
- AI 文书生成
- 风险预警
- 任务执行
- 学生管理
- 状态跟踪
- 可恢复执行
- 人工审核
- 全周期任务管理

---

# 二、核心设计思想（必须遵守）

# 1. Workflow First

系统核心是工作流，而不是聊天。

所有功能都必须以：

```txt
输入
→ 处理
→ 输出
→ 状态
```

方式设计。

禁止：

- Autonomous Agent
- 无限循环 Agent
- AutoGPT 风格系统
- 不可控 Agent 行为

---

# 2. Task Isolation（重要）

所有任务必须独立执行。

禁止：

- 多任务共享上下文污染
- 巨型 Agent
- 单函数处理所有业务

每个 Task 必须：

- 独立输入
- 独立输出
- 独立日志
- 独立状态
- 可重试
- 可恢复

---

# 3. Human In The Loop

所有关键操作必须支持人工确认。

例如：

- 通知发送
- 风险上报
- 家校沟通
- 心理相关内容

AI 只能建议。

最终决定权属于辅导员。

---

# 4. Deterministic Workflow

优先确定性工作流。

禁止过早引入：

- 多 Agent 自主规划
- 动态推理路由
- 自治系统

系统前期必须：

# 可控
# 可解释
# 可恢复

---

# 三、系统目标用户

## Primary User

高校辅导员

---

## Future User

- 学院副书记
- 学工处
- 班主任
- 学生助理
- 心理老师
- 就业老师

---

# 四、系统核心模块

# Module 1：通知 Agent（第一优先级）

## 功能目标

帮助辅导员快速生成标准化通知。

---

## 输入

例如：

```txt
明天下午 3 点召开防诈骗班会
地点 A203
全员参加
```

---

## 输出

自动生成：

- 正式通知版
- 微信群通知版
- 家长通知版
- 短信简版
- 标题

---

## Workflow

```txt
输入事件
→ AI 生成通知
→ 辅导员审核
→ 保存记录
→ 发送
```

---

## Task Definition

### generate_notice_task

Input:

```json
{
  "event": "string"
}
```

Output:

```json
{
  "formal_notice": "string",
  "wechat_notice": "string",
  "parent_notice": "string",
  "sms_notice": "string"
}
```

---

# Module 2：谈心谈话 Agent

## 功能目标

自动生成谈话记录与跟进建议。

---

## 输入

```txt
学生近期旷课两次
情绪低落
与室友关系紧张
```

---

## 输出

- 谈话记录
- 风险等级
- 后续建议
- 家校沟通建议

---

## Workflow

```txt
输入情况
→ AI 分析
→ 生成谈话记录
→ 辅导员审核
→ 保存档案
```

---

## Task Definition

### generate_conversation_record_task

Input:

```json
{
  "student_id": "string",
  "situation": "string"
}
```

Output:

```json
{
  "conversation_record": "string",
  "risk_level": "low | medium | high",
  "follow_up_advice": "string"
}
```

---

# Module 3：学生风险预警 Agent

## 功能目标

自动发现重点风险学生。

---

## 风险来源

- 缺勤
- 晚归
- 心理异常
- 成绩下降
- 高频请假
- 实习异常

---

## Workflow

```txt
导入数据
→ 风险评分
→ AI 分析
→ 生成风险报告
→ 辅导员确认
→ 建立跟踪任务
```

---

## 风险状态机

```txt
NEW
↓
REVIEWING
↓
INTERVIEWED
↓
PARENT_CONTACTED
↓
FOLLOWING
↓
RESOLVED
```

---

## Task Definition

### risk_analysis_task

Input:

```json
{
  "attendance": [],
  "grades": [],
  "leave_records": []
}
```

Output:

```json
{
  "risk_students": [],
  "risk_reports": []
}
```

---

# Module 4：学情分析 Agent

## 功能目标

自动生成学情分析报告。

---

## 输入

- 成绩
- 考勤
- 晚自习
- 请假

---

## 输出

- 班级分析
- 异常学生
- 学风建议
- 学业预警

---

## Workflow

```txt
上传 Excel
→ 数据解析
→ AI 分析
→ 生成报告
→ 导出 PDF
```

---

# Module 5：活动策划 Agent

## 功能目标

自动生成活动方案。

---

## 输入

```txt
防诈骗主题活动
预算 500
人数 50
```

---

## 输出

- 活动方案
- 流程表
- 主持稿
- 宣传文案
- 总结模板

---

# Module 6：就业与实习 Agent

## 功能目标

辅助大三大四就业管理。

---

## 功能

- 招聘信息管理
- 实习巡查记录
- offer 跟踪
- 简历建议
- 就业统计

---

# 五、系统整体架构

# Frontend

技术栈：

- Vue 3
- Vite
- TypeScript
- Pinia
- Vue Router
- Element Plus

---

# Backend

技术栈：

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic

---

# AI Layer

模型：

- DeepSeek API

统一 AI Service：

```txt
services/ai/
```

统一管理：

- prompt
- model
- retry
- logging
- token usage

---

# Workflow Layer（核心）

目录：

```txt
backend/app/workflows/
```

每个工作流：

- 独立状态
- 独立日志
- 独立恢复

---

# Task Layer

目录：

```txt
backend/app/tasks/
```

任务必须：

- 单一职责
- 独立执行
- 可重试
- 可观测

---

# 六、数据库设计（第一阶段）

# users

```sql
id
name
role
college
```

---

# classes

```sql
id
name
grade
major
```

---

# students

```sql
id
name
class_id
phone
risk_level
```

---

# notices

```sql
id
title
content
status
created_by
created_at
```

---

# tasks

```sql
id
type
status
input
output
retry_count
created_at
```

---

# workflows

```sql
id
type
status
current_step
created_at
```

---

# risk_records

```sql
id
student_id
risk_level
reason
status
created_at
```

---

# conversations

```sql
id
student_id
content
risk_level
follow_up
created_at
```

---

# 七、系统状态设计

所有任务必须支持：

```txt
PENDING
RUNNING
SUCCESS
FAILED
RETRYING
WAITING_APPROVAL
CANCELLED
```

---

# 八、日志与可观测性（必须实现）

每个 Task 必须记录：

- input
- output
- model
- token
- duration
- retry_count
- error

---

# 九、Prompt System（重要）

目录：

```txt
backend/app/prompts/
```

每种业务独立 Prompt：

- notice_prompt
- risk_prompt
- parent_prompt
- conversation_prompt

禁止：

- Prompt 写死在业务代码里

---

# 十、系统阶段规划

# Phase 1（当前）

目标：

# 通知生成器 MVP

功能：

- 输入事件
- AI 输出通知
- 辅导员审核
- 保存记录

禁止开发：

- 多 Agent
- LangGraph
- RAG
- 向量数据库
- 自动规划

---

# Phase 2

增加：

- 模板库
- Excel 导入
- 批量通知
- 学生数据管理

---

# Phase 3

增加：

- 风险预警
- 谈话记录
- 学情分析
- Workflow Engine

---

# Phase 4

增加：

- MCP Tool System
- 企业微信
- OCR
- PDF 导出
- 审批流

---

# Phase 5

增加：

- RAG
- 多 Agent
- LangGraph
- Durable Execution
- Long Running Workflow

---

# 十一、Claude Code 开发原则（必须遵守）

Claude Code 必须：

# 1. 小步迭代

禁止一次生成完整系统。

---

# 2. 先实现 MVP

先可运行。

后优化。

---

# 3. 禁止过度工程化

禁止：

- 微服务
- DDD
- Kubernetes
- Event Bus
- 复杂抽象

---

# 4. 所有模块必须单一职责

禁止：

- 巨型 Service
- 巨型 Agent
- 超长函数

---

# 5. 所有 AI 输出必须支持人工审核

AI 不允许直接执行关键操作。

---

# 6. 所有 Workflow 必须支持恢复

系统重启后：

- Workflow 可恢复
- Task 可重试

---

# 十二、项目目录结构（推荐）

```txt
frontend/
├── src/
│   ├── pages/
│   ├── components/
│   ├── stores/
│   ├── api/
│   └── router/

backend/
├── app/
│   ├── api/
│   ├── services/
│   ├── workflows/
│   ├── tasks/
│   ├── prompts/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   └── db/
```

---

# 十三、当前开发任务（立即开始）

# 第一阶段只实现：

# 通知生成器

包括：

- Vue 页面
- FastAPI API
- DeepSeek 调用