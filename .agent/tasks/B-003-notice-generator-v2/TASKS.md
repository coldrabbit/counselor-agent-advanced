# TASKS: Notice Generator v2 (通知生成器增强)

## Dependencies

- 依赖 task-001 的 NoticeGenerator.vue 基座
- 依赖 task-001 的 `/api/notices/generate` 端点（不改它）
- 与 B-002 共享 `backend/app/main.py` 路由注册（冲突文件，需协调合并顺序）

---

## Step 1: Backend — 场景模板 Prompts

**Files:**
- `backend/app/prompts/scenes.py` — NEW

**Description:**
定义 4 个场景模板的静态数据（存储在 Python 模块中而非数据库，MVP 保持简单）：

```python
SCENES = [
    {"id": "safety", "name": "安全通知", "description": "...", "template": "..."},
    {"id": "study", "name": "学风提醒", ...},
    {"id": "activity", "name": "活动通知", ...},
    {"id": "reminder", "name": "事务催办", ...},
]
```

每个 template 包含 `[年级]`、`[班级]`、`[时间]`、`[地点]` 等占位符，供前端填充。

**Verify:**
- `python -c "from app.prompts.scenes import SCENES; print(len(SCENES))"` → 4

---

## Step 2: Backend — 润色 Prompt

**Files:**
- `backend/app/prompts/polish.py` — NEW

**Description:**
```python
def build_polish_prompt(style: str) -> str:
    return f"""你是高校辅导员通知润色助手。
请对以下通知文本进行润色，使其更符合'{style}'风格。
- 正式通知：规范严谨，措辞得体
- 微信群通知：亲切活泼，善用分段
- 家长通知：温和正式，体现关怀
- 短信简版：高度凝练，70字以内
保持原意不改变，只优化表达。输出润色后的纯文本，不要JSON。"""
```

**Verify:**
- `python -c "from app.prompts.polish import build_polish_prompt; print('ok')"`

---

## Step 3: Backend — API 端点

**Files:**
- `backend/app/api/scenes.py` — NEW
- `backend/app/api/notices.py` — MODIFY（新增 polish 端点）
- `backend/app/main.py` — MODIFY（注册 scenes 路由）

**Description:**

### GET /api/scenes
```python
@router.get("")
def list_scenes():
    return SCENES  # 从 prompts/scenes.py 导入
```

### POST /api/notices/polish
```python
class PolishRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    style: str = Field(..., pattern="^(formal|wechat|parent|sms)$")

@router.post("/polish")
def polish_notice(req: PolishRequest):
    system_prompt = build_polish_prompt(req.style)
    ai = AIService()
    result = ai.chat(system_prompt=system_prompt, user_message=req.content, max_retries=1)
    if result["success"]:
        return {"polished_content": result["content"], "model": result["model"], "token_usage": result["token_usage"]}
    raise HTTPException(status_code=500, detail="润色失败")
```

**Verify:**
- `curl http://localhost:8000/api/scenes` 返回 4 个场景
- `curl -X POST http://localhost:8000/api/notices/polish -H 'Content-Type: application/json' -d '{"content":"测试通知","style":"formal"}'` 返回润色后文本

---

## Step 4: Frontend — NoticeGenerator.vue 增强

**Files:**
- `frontend/src/pages/NoticeGenerator.vue` — MODIFY

**Description:**

### 1. 场景快捷按钮
在 `<el-input v-model="event">` 上方增加：
```vue
<div class="scene-buttons">
  <el-button v-for="scene in scenes" :key="scene.id"
    size="small" @click="applyScene(scene)">
    {{ scene.name }}
  </el-button>
</div>
```
- `onMounted` 中加载场景：`axios.get('/api/scenes')`
- `applyScene(scene)`: `event.value = scene.template`

### 2. AI 润色按钮
在每个 `<el-tab-pane>` 内部 `<div class="notice-content">` 下方增加：
```vue
<el-button size="small" :loading="polishing[style]" @click="polishContent(style)">
  ✨ AI 润色
</el-button>
```
- `polishContent(style)`: 调用 `POST /api/notices/polish`，替换 `store.currentNotice[style]`
- 使用 `polishing` ref (Record<string, boolean>) 控制 loading

### 3. 复制按钮
在每个 `<el-tab-pane>` 的 label 右侧增加复制图标：
```vue
<el-tab-pane>
  <template #label>
    正式通知
    <el-button link size="small" @click="copyContent('formal_notice')">
      <el-icon><CopyDocument /></el-icon>
    </el-button>
  </template>
  ...
</el-tab-pane>
```
- `copyContent(field)`: `navigator.clipboard.writeText(text)` → `ElMessage.success('已复制')`

**Verify:**
- 浏览器中看到 4 个场景按钮
- 点击"安全通知" → textarea 填充模板
- 生成通知后，点击"AI 润色" → 文本变化
- 点击"复制" → 剪贴板有对应文本

---

## Step 5: Backend — 测试

**Files:**
- `backend/tests/test_api/test_notices_v2.py` — NEW

**Description:**
- `test_list_scenes`: 返回 4 个场景，字段完整
- `test_polish_success`: 返回 polished_content
- `test_polish_invalid_style`: style=invalid → 422
- `test_polish_empty_content`: content="" → 422
- `test_scene_template_placeholders`: 每个 template 含至少一个 `[xxx]` 占位符

**Verify:**
- `pytest backend/tests/test_api/test_notices_v2.py -v` 全部通过
- `pytest backend/tests/ -v` 回归全部通过

---

## Verification Gates

```bash
# 1. Lint
ruff check backend/app/api/scenes.py backend/app/prompts/polish.py backend/app/prompts/scenes.py backend/app/api/notices.py
cd frontend && npm run lint -- src/pages/NoticeGenerator.vue

# 2. Typecheck
python -c "from app.api.scenes import router; from app.prompts.polish import build_polish_prompt; from app.prompts.scenes import SCENES; print('ok')"
cd frontend && vue-tsc --noEmit

# 3. Test
pytest backend/tests/test_api/test_notices_v2.py -v
pytest backend/tests/ -v  # 回归

# 4. Build
cd frontend && npm run build
```
