# SPEC: Notice Generator v2 (通知生成器增强)

## Summary

在 task-001 通知生成器基础上增加：4 种场景模板快速填充、AI 润色通知文本、一键复制功能。减少用户输入负担，提升通知质量。

## Motivation

当前通知生成器需要用户手动输入完整事件描述。辅导员日常工作有高度重复的场景（安全通知、学风提醒等），应提供场景化快速入口和 AI 润色能力。

## Input

- 用户选择场景类型（安全/学风/活动/催办）
- 用户填入少量关键信息（年级、班级、时间、地点）
- 已有通知文本（润色场景）

## Output

- 场景模板自动拼接为完整 event 描述 → 调用已有 generate API
- AI 润色：对已有通知文本进行语言优化 → 返回润色后文本
- 一键复制：四个版本通知各自可复制到剪贴板

## Functional Requirements

### FR-001: Scene Quick Templates
- 输入区域上方新增"场景模板"快捷按钮组：安全通知、学风提醒、活动通知、事务催办
- 点击场景按钮 → event textarea 预填场景模板
- 模板包含 `[年级]`、`[班级]`、`[时间]`、`[地点]` 等占位符，用户替换即可

### FR-002: Scene Templates Defined
四个场景模板定义在 `backend/app/prompts/scenes.py`：
- **安全通知**: "面向[年级][班级]全体学生，开展[安全主题]安全教育。时间：[时间]，地点：[地点]。请全体学生准时参加。"
- **学风提醒**: "面向[年级][班级]学生，提醒[学风事项]。涉及课程：[课程名称]，要求：[具体要求]。"
- **活动通知**: "组织[活动名称]活动。时间：[时间]，地点：[地点]，参与对象：[参与对象]。[活动简介]。"
- **事务催办**: "请[年级][班级]学生在[截止时间]前，完成[事项名称]。涉及材料：[材料清单]。逾期将[后果说明]。"

### FR-003: AI Polish
- 每个通知 tab（正式/微信/家长/短信）下方增加"AI 润色"按钮
- 点击 → `POST /api/notices/polish` → 返回润色后文本替换当前 tab 内容
- 润色规则：修正表达、优化措辞、保留原意，不改变通知结构
- 加载时按钮显示 loading 状态

### FR-004: Copy to Clipboard
- 每个通知 tab 右上角增加"复制"按钮
- 点击 → 将当前 tab 的通知文本复制到剪贴板 → ElMessage.success('已复制')
- 使用 `navigator.clipboard.writeText()`

### FR-005: Existing Flow Unchanged
- 事件输入、模板选择、批量生成、OCR、审核、PDF 导出、微信发送保持原样
- 新增 UI 元素不破坏旧功能

## API Contract

### POST /api/notices/polish

Request:
```json
{
  "content": "需要润色的通知文本",
  "style": "formal | wechat | parent | sms"
}
```

Response:
```json
{
  "polished_content": "润色后的通知文本",
  "model": "deepseek-chat",
  "token_usage": 150
}
```

### GET /api/scenes

Response:
```json
[
  {
    "id": "safety",
    "name": "安全通知",
    "description": "用于安全教育、防诈骗、假期安全等通知",
    "template": "面向[年级][班级]全体学生，开展[安全主题]安全教育。..."
  }
]
```

## Frontend / Backend Boundary

| 层 | 文件 | 操作 | 说明 |
|----|------|------|------|
| Backend Prompt | `backend/app/prompts/polish.py` | NEW | 润色 prompt |
| Backend Prompt | `backend/app/prompts/scenes.py` | NEW | 场景模板数据 |
| Backend API | `backend/app/api/scenes.py` | NEW | GET /api/scenes |
| Backend API | `backend/app/api/notices.py` | MODIFY | 新增 POST /polish 端点 |
| Backend Router | `backend/app/main.py` | MODIFY | 注册 scenes 路由 |
| Frontend Page | `frontend/src/pages/NoticeGenerator.vue` | MODIFY | 场景按钮、润色、复制 |
| Backend Test | `backend/tests/test_api/test_notices_v2.py` | NEW | polish + scenes 测试 |

## Acceptance Criteria

- [ ] AC-001: 页面展示 4 个场景快捷按钮，点击后 textarea 预填模板
- [ ] AC-002: GET /api/scenes 返回 4 个场景模板
- [ ] AC-003: 每个通知 tab 有"AI 润色"按钮，点击后文本被润色
- [ ] AC-004: POST /api/notices/polish 返回润色后文本且保留原意
- [ ] AC-005: 每个通知 tab 有"复制"按钮，点击后文本进入剪贴板
- [ ] AC-006: 旧功能（生成、模板、批量、审核、PDF、微信）不受影响
- [ ] AC-007: AI 润色失败时提示用户"润色失败"

## Constraints

- 不引入新第三方依赖
- 润色 Prompt 放在 `backend/app/prompts/polish.py`
- 场景模板放在 `backend/app/prompts/scenes.py`
- 复用已有 AIService.chat()
- 润色不改变通知 JSON 结构，只修改文本内容

## Affected Files (Builder 可修改)

### 新建文件
- `backend/app/prompts/polish.py`
- `backend/app/prompts/scenes.py`
- `backend/app/api/scenes.py`
- `backend/tests/test_api/test_notices_v2.py`

### 可修改文件
- `backend/app/api/notices.py` — 新增 polish 端点
- `backend/app/main.py` — 注册 scenes 路由
- `frontend/src/pages/NoticeGenerator.vue` — 场景按钮、润色、复制

### 冲突标记文件 (与 B-002 共享)
- `backend/app/main.py` — **冲突风险**，B-002 也需在此注册 workbench 路由，合并时需同时包含两处修改

## Forbidden Files

- `backend/app/tasks/notice_task.py` — 只读，润色是独立端点不修改 task
- `backend/app/workflows/`
- `backend/app/services/ai/client.py`
- `backend/app/engine/`
- `frontend/src/components/PreGenerateDialog.vue`
- `frontend/src/pages/MonthlyWorkbench.vue` — B-002 的文件，不要碰
- `frontend/src/stores/notice.ts` — 复用即可

## Test Plan

| 测试 | 内容 |
|------|------|
| test_list_scenes | GET /api/scenes 返回 4 个场景 |
| test_polish_success | POST /api/notices/polish 返回润色后文本 |
| test_polish_invalid_style | style=invalid 返回 422 |
| test_polish_empty_content | content="" 返回 422 |
| test_scene_template_format | 每个场景模板含占位符 |
| test_copy_button | 前端：复制按钮可见，点击触发 clipboard API |
