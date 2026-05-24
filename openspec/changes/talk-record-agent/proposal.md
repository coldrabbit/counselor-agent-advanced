## Why

辅导员在谈心谈话后需要及时撰写谈话记录、评估风险等级并形成跟进建议。当前这些文书工作全靠手动完成，耗时且格式不统一。本模块将 AI 谈话记录生成纳入平台，复用已有的辅导员信息配置和审核工作流模式。

## What Changes

- 新增 "谈心谈话" 页面，输入学生信息和谈话情况，一键生成谈话记录
- 新增 TalkRecord 模型和 API（CRUD + 审核）
- 新增 talk_record prompt（谈话记录生成、风险评级、跟进建议）
- 新增 generate_talk_record_task 独立任务
- 复用已有的 CounselorProfile 和审核工作流（PENDING → REVIEWING → APPROVED）
- 前端新增 TalkRecordGenerator.vue 页面和路由

## Capabilities

### New Capabilities
- `talk-record-generate`: 输入学生信息和谈话情况，AI 生成谈话记录、风险等级、后续建议、家校沟通建议
- `talk-record-review`: 辅导员审核谈话记录，支持通过/驳回，状态流转

### Modified Capabilities
<!-- No existing capabilities changed -->

## Impact

- **新建文件**: models/talk_record.py, schemas/talk_record.py, api/talk_records.py, prompts/talk_record.py, tasks/talk_record_task.py, pages/TalkRecordGenerator.vue, stores/talk_record.ts, api-client/talk_records.ts
- **修改文件**: main.py (注册路由), router/index.ts (新增路由 `/talk-record`), models/__init__.py (导入新模型)
- **复用**: CounselorProfile, Task 模型, AI 服务, 审核工作流模式
- **无破坏性变更**: notice 模块不受影响
