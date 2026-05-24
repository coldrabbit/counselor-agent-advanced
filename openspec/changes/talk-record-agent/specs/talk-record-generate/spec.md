## ADDED Requirements

### Requirement: 辅导员可生成谈话记录
系统 SHALL 接收学生基本信息（姓名、学号）和谈话情况描述，调用 DeepSeek 生成结构化谈话记录，包含：正式谈话记录、风险等级（low/medium/high）、后续跟进建议、家校沟通建议。

#### Scenario: 成功生成谈话记录
- **WHEN** 辅导员输入学生信息 "姓名：李明，学号：20240101001" 和情况 "近期旷课两次，情绪低落，与室友关系紧张"
- **THEN** 系统返回包含 conversation_record、risk_level、follow_up_advice、parent_advice 四个字段的 JSON

#### Scenario: 无辅导员信息时生成
- **WHEN** 辅导员信息未配置
- **THEN** 系统仍可正常生成，但谈话记录落款使用通用表述

#### Scenario: AI 调用失败
- **WHEN** DeepSeek API 超时或返回错误
- **THEN** 系统返回失败状态，并在 Task 中记录错误信息

### Requirement: 谈话记录包含风险等级
系统 SHALL 对每次谈话情况输出风险等级，枚举值为 low（低风险）、medium（中风险）、high（高风险）。

#### Scenario: 高风险判定
- **WHEN** 情况描述包含 "自残倾向" 或 "严重心理问题"
- **THEN** 系统输出 risk_level 为 "high"

#### Scenario: 低风险判定
- **WHEN** 情况描述为一般学业问题
- **THEN** 系统输出 risk_level 为 "low"

### Requirement: 生成任务可追踪
系统 SHALL 为每次生成创建 Task 记录，包含：输入、输出、模型、token 消耗、耗时、状态。

#### Scenario: Task 记录完整
- **WHEN** 生成完成后
- **THEN** Task 表存在一条 type="generate_talk_record" 的记录，包含 input/output/model/token_usage/duration_ms
