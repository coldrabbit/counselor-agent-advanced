## ADDED Requirements

### Requirement: 辅导员可审核谈话记录
系统 SHALL 支持辅导员对生成的谈话记录进行审核，通过后状态变为 APPROVED，驳回后返回 DRAFT 状态。

#### Scenario: 审核通过
- **WHEN** 辅导员点击 "审核通过" 按钮
- **THEN** 谈话记录状态从 WAITING_APPROVAL 变为 APPROVED

#### Scenario: 驳回
- **WHEN** 辅导员点击 "驳回" 按钮
- **THEN** 谈话记录状态从 WAITING_APPROVAL 变为 DRAFT

### Requirement: 谈话记录可查阅
系统 SHALL 提供谈话记录列表接口，按创建时间倒序排列。

#### Scenario: 查询记录列表
- **WHEN** 辅导员访问记录列表页
- **THEN** 系统返回所有谈话记录，包含 id、student_name、risk_level、status、created_at
