## Context

当前系统只有通知生成器模块（Notice）。谈心谈话记录生成是一个全新的模块，但可以复用：
- CounselorProfile（辅导员信息已在前期实现）
- Task 模型（任务追踪日志）
- AIService（DeepSeek 调用封装）
- 审核工作流模式（生成 → 审核 → 保存）
- PreGenerateDialog 模式（生成前补充信息）

## Goals / Non-Goals

**Goals:**
- 辅导员输入学生信息 + 谈话情况，AI 生成谈话记录、风险等级、跟进建议、家校沟通建议
- 支持辅导员审核通过/驳回
- 复用现有 CounselorProfile，自动使用辅导员真实信息
- 所有生成通过独立 Task 追踪（输入/输出/状态/token/耗时）

**Non-Goals:**
- 不实现学生数据库管理（学生信息目前由用户手动输入）
- 不实现自动风险预警（那是 Module 3）
- 不实现谈话记录的全文搜索或导出
- 不改变现有通知模块

## Decisions

| 决策 | 选择 | 原因 |
|------|------|------|
| 数据模型 | TalkRecord 独立表 | 与 Notice 职责不同，字段不同（风险等级、学号等） |
| 风险等级 | 枚举 low/medium/high | 与 PRD 一致，后续可对接风险预警 |
| Prompt 结构 | 独立 `prompts/talk_record.py` | 遵循项目规则：Prompt 与业务逻辑分离 |
| Task 模式 | 复用 Task 模型，type=`generate_talk_record` | 保持全局任务追踪一致性 |
| API 设计 | RESTful，与 notices 模块平行 | `/api/talk-records` 前缀，风格一致 |
| 前端页面 | 新页面 `/talk-record`，独立路由 | 单一职责，不与通知页面耦合 |
| 生成前弹窗 | 复用 PreGenerateDialog 模式 | 学生基本信息（姓名、学号）可在弹窗中补充 |

## Risks / Trade-offs

- [风险] DeepSeek 对风险等级的判断可能不稳定 → Prompt 明确风险判定标准（缺勤次数、心理状态、社交关系等维度）
- [风险] 谈话记录可能包含学生真实隐私信息 → 本地 SQLite 足够（MVP 阶段），后续需考虑数据脱敏
- [取舍] 学生信息采用手动输入而非从 DB 查询 → MVP 阶段无学生数据库，优先可用性
