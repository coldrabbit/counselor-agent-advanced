# SPEC: QA Foundation (QA 基础设施)

## Summary

为全项目建立 QA 基础设施，使 OpenCode 能稳定验证每个功能。包括 lint 配置、typecheck 配置、测试框架、E2E 基础结构、移动端检查脚本、控制台错误检查。**不修改任何业务逻辑代码。**

## Motivation

当前项目缺乏标准化 QA 基础设施：
- 无前端 lint 脚本（`npm run lint` 不存在，QA 报告 OBS-004）
- 无前端测试框架配置
- 无 E2E 测试结构
- 无移动端自动化检查
- 无控制台错误自动化检查
- 无 CI 配置文件

## Scope: Infrastructure Only

I-001 严格限制为**基础设施搭建**，不修改任何业务代码：

| 允许 | 禁止 |
|------|------|
| 新增配置文件 | 修改任何 `.vue` 文件 |
| 新增测试脚本 | 修改任何 `.py` 业务文件 |
| 新增 CI 配置 | 修改任何 model/schema/repository |
| 新增测试目录结构 | 修改任何 API 端点 |
| 修改 `package.json` (scripts) | 修改任何 workflow/task/engine |
| 新增 devDependencies | 修改任何 store/router 业务逻辑 |

## Functional Requirements

### FR-001: Frontend Lint 配置
- 安装 ESLint + Vue 3 plugin + TypeScript plugin
- 创建 `frontend/eslint.config.js`
- 在 `package.json` 添加 `"lint": "eslint src/ --ext .ts,.vue"`
- 规则从宽：`warn` 级别为主，不阻塞开发

### FR-002: Frontend Test 框架
- 安装 vitest + @vue/test-utils + jsdom
- 创建 `frontend/vitest.config.ts`
- 在 `package.json` 添加 `"test": "vitest run"` 和 `"test:watch": "vitest"`
- 创建 `frontend/src/__tests__/` 目录 + 示例测试

### FR-003: Backend Lint 强化
- 创建 `backend/ruff.toml` 配置文件
- 设置 max-line-length = 120
- 设置 target-version = "py311"
- `pyproject.toml` 已有则不改，仅在项目根创建 `ruff.toml`

### FR-004: E2E 基础结构
- 安装 Playwright
- 创建 `e2e/` 目录：`playwright.config.ts` + 示例测试
- `e2e/fixtures/` 目录 + `e2e/tests/` 目录
- 在 `package.json` 添加 `"e2e": "playwright test"`
- E2E 示例测试：首页加载 + 导航栏渲染

### FR-005: 移动端检查脚本
- 创建 `scripts/check-mobile.sh`
- 功能：使用 Playwright 对关键页面截取移动端视口截图
- 检查视口宽度 375px 渲染无误
- 输出截图到 `e2e/screenshots/`

### FR-006: 控制台错误检查脚本
- 创建 `scripts/check-console.sh`
- 功能：使用 Playwright 启动页面，监听 console.error
- 任何 console.error → 脚本 exit 1
- 白名单已知的无害 warning（如第三方库）

### FR-007: CI 配置
- 创建 `.github/workflows/ci.yml`
- 包含 job：lint-backend, lint-frontend, test-backend, test-frontend, build-frontend
- 可选：e2e (仅在有 secrets 时运行)
- 触发条件：push 到 main + PR 到 main

### FR-008: 不破坏现有功能
- 新增依赖不影响现有 build
- 新增 lint 规则不导致现有代码 lint 失败（warn 级别）
- 新增测试框架不强制要求已有代码有测试

## Affected Files (Builder 可修改)

### 新建文件（全部为配置/脚本/测试，零业务代码）
- `frontend/eslint.config.js` — ESLint 配置
- `frontend/vitest.config.ts` — Vitest 配置
- `frontend/src/__tests__/example.test.ts` — 示例测试
- `backend/ruff.toml` — ruff 配置
- `e2e/playwright.config.ts` — Playwright 配置
- `e2e/tests/example.spec.ts` — E2E 示例
- `scripts/check-mobile.sh` — 移动端检查脚本
- `scripts/check-console.sh` — 控制台检查脚本
- `.github/workflows/ci.yml` — CI 配置

### 可修改文件（仅 scripts 字段）
- `frontend/package.json` — 新增 lint/test/e2e scripts 和 devDependencies

## Forbidden Files (I-001 严禁触碰)

```yaml
backend/app/:          # 全部业务代码，禁止修改
  api/                 # 禁止
  models/              # 禁止
  schemas/             # 禁止
  repositories/        # 禁止
  services/            # 禁止
  tasks/               # 禁止
  workflows/           # 禁止
  prompts/             # 禁止
  engine/              # 禁止
  main.py              # 禁止

frontend/src/:
  pages/               # 禁止
  components/          # 禁止
  stores/              # 禁止
  router/              # 禁止
  api/                 # 禁止
  App.vue              # 禁止
  main.ts              # 禁止
```

唯一的例外：`frontend/src/__tests__/` 目录（新建，用于测试代码）。

## Acceptance Criteria

- [ ] AC-001: `cd frontend && npm run lint` 可执行，不报致命错误
- [ ] AC-002: `cd frontend && npm run test` 可执行，示例测试通过
- [ ] AC-003: `ruff check backend/` 使用配置文件中定义的规则
- [ ] AC-004: `cd frontend && npm run build` 不受影响，仍然成功
- [ ] AC-005: `npx playwright test` 可执行（E2E 示例）
- [ ] AC-006: `bash scripts/check-mobile.sh` 可运行
- [ ] AC-007: `bash scripts/check-console.sh` 可运行
- [ ] AC-008: `.github/workflows/ci.yml` 语法正确
- [ ] AC-009: 无任何业务代码文件被修改（git diff 验证）
- [ ] AC-010: `pytest backend/tests/ -v` 全量回归通过

## Constraints

- 不修改任何业务逻辑
- ESLint 规则为 warn 级别，不阻塞开发
- vitest 仅配置，不强制迁移已有代码
- E2E 仅搭架子 + 1-2 个示例测试
- 新增 devDependencies: eslint, @eslint/js, typescript-eslint, eslint-plugin-vue, vitest, @vue/test-utils, jsdom, @playwright/test
- 不安装全局工具

## Test Plan

| 测试 | 类型 | 内容 |
|------|------|------|
| example.test.ts | 前端单元 | 示例：true === true |
| example.spec.ts | E2E | 首页加载 → 标题包含 "Counselor OS" |
| check-mobile.sh | 脚本 | 375px 视口截图无报错 |
| check-console.sh | 脚本 | 页面加载无 console.error |
| ci.yml 语法检查 | CI | `act --dryrun` 或 GitHub Actions web validator |
| 回归测试 | 后端 | pytest 全量通过，证明无业务代码被破坏 |
