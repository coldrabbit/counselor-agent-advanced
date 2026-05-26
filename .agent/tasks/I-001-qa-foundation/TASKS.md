# TASKS: QA Foundation (QA 基础设施)

## Dependencies

- 无业务依赖。独立可完成。
- 与 B-002、B-003 零代码冲突（I-001 只加配置/脚本，不碰业务代码）

---

## Step 1: Backend — Lint 配置文件

**Files:**
- `backend/ruff.toml` — NEW

**Description:**
创建 ruff 配置文件，统一后端代码风格：

```toml
target-version = "py311"
line-length = 120

[lint]
select = ["E", "F", "W", "I"]  # pycodestyle, pyflakes, isort

[format]
quote-style = "double"
indent-style = "space"
```

不修改 `pyproject.toml`（如果存在）。

**Verify:**
- `ruff check backend/` 使用配置规则（检查输出包含 "ruff.toml" 或规则编号正确）

---

## Step 2: Frontend — ESLint 配置

**Files:**
- `frontend/eslint.config.js` — NEW
- `frontend/package.json` — MODIFY（scripts + devDependencies）

**Description:**
```bash
cd frontend
npm install -D eslint @eslint/js typescript-eslint eslint-plugin-vue
```

创建 flat config：
```js
import js from '@eslint/js'
import ts from 'typescript-eslint'
import vue from 'eslint-plugin-vue'

export default [
  js.configs.recommended,
  ...ts.configs.recommended,
  ...vue.configs['flat/recommended'],
  {
    rules: {
      'no-console': 'warn',
      '@typescript-eslint/no-unused-vars': 'warn',
      'vue/multi-word-component-names': 'off',
    }
  }
]
```

package.json scripts 增加：`"lint": "eslint src/ --ext .ts,.vue"`

**Verify:**
- `cd frontend && npm run lint` 可执行，最多 warn 级别输出
- `cd frontend && npm run build` 仍然成功（ESLint 不影响构建）

---

## Step 3: Frontend — Vitest 测试框架

**Files:**
- `frontend/vitest.config.ts` — NEW
- `frontend/src/__tests__/example.test.ts` — NEW
- `frontend/package.json` — MODIFY（scripts + devDependencies）

**Description:**
```bash
cd frontend
npm install -D vitest @vue/test-utils jsdom
```

vitest.config.ts：
```ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
```

example.test.ts：
```ts
import { describe, it, expect } from 'vitest'

describe('QA Foundation', () => {
  it('vitest is configured', () => {
    expect(true).toBe(true)
  })
})
```

package.json scripts 增加：`"test": "vitest run"`, `"test:watch": "vitest"`

**Verify:**
- `cd frontend && npm run test` 示例测试通过

---

## Step 4: E2E 基础结构

**Files:**
- `e2e/playwright.config.ts` — NEW
- `e2e/tests/example.spec.ts` — NEW
- `frontend/package.json` — MODIFY（scripts + devDependencies）

**Description:**
```bash
npm install -D @playwright/test
npx playwright install chromium --with-deps  # 仅安装 chromium
```

playwright.config.ts：
```ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  webServer: {
    command: 'cd ../frontend && npm run dev',
    port: 5173,
    reuseExistingServer: true,
  },
  use: {
    baseURL: 'http://localhost:5173',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['iPhone 13'] } },
  ],
})
```

example.spec.ts：
```ts
import { test, expect } from '@playwright/test'

test('homepage loads', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toContainText('工作台')
})
```

package.json scripts 增加：`"e2e": "playwright test"`

**Verify:**
- `cd e2e && npx playwright test` 示例 E2E 可执行（依赖 dev server）

---

## Step 5: 移动端 + 控制台检查脚本

**Files:**
- `scripts/check-mobile.sh` — NEW
- `scripts/check-console.sh` — NEW

**Description:**

### check-mobile.sh
```bash
#!/bin/bash
# 移动端页面检查：对关键页面在 375px 视口截图
PAGES=("/" "/notices" "/talk-record" "/students" "/risks")
mkdir -p e2e/screenshots
for path in "${PAGES[@]}"; do
  echo "Checking mobile: $path"
  npx playwright screenshot --viewport-size=375,812 "http://localhost:5173$path" "e2e/screenshots/mobile-${path//\//_}.png"
done
```

### check-console.sh
```bash
#!/bin/bash
# 控制台错误检查：启动页面，监听 console.error
# 使用 Playwright script 收集 console 消息
npx playwright test e2e/tests/console-check.spec.ts
```

console-check.spec.ts（配套 E2E 测试）：
```ts
test('no console errors on key pages', async ({ page }) => {
  const errors: string[] = []
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text())
  })
  const pages = ['/', '/notices', '/talk-record']
  for (const path of pages) {
    await page.goto(path)
    await page.waitForLoadState('networkidle')
  }
  expect(errors).toEqual([])
})
```

**Verify:**
- `bash scripts/check-mobile.sh` 可运行（需 dev server 运行中）
- `bash scripts/check-console.sh` 可运行

---

## Step 6: CI 配置

**Files:**
- `.github/workflows/ci.yml` — NEW

**Description:**
```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install ruff
      - run: ruff check backend/

  lint-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd frontend && npm ci && npm run lint

  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env: { POSTGRES_DB: test, POSTGRES_PASSWORD: test }
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/ -v
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd frontend && npm ci && npm run test

  build-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd frontend && npm ci && npm run build
```

**Verify:**
- `.github/workflows/ci.yml` YAML 语法正确
- 如果本地有 `act`：`act --dryrun` 成功

---

## Step 7: 全量回归验证

**Description:**
运行全部已有测试，确保新增配置和依赖未破坏任何业务功能。

**Verify:**
- `pytest backend/tests/ -v` 全部通过（60+ tests）
- `cd frontend && npm run build` 成功
- `docker compose build` 成功（可选）

---

## Verification Gates

```bash
# 1. Lint
ruff check backend/
cd frontend && npm run lint

# 2. Typecheck
cd frontend && vue-tsc --noEmit

# 3. Test
pytest backend/tests/ -v
cd frontend && npm run test

# 4. Build
cd frontend && npm run build

# 5. CI Syntax
# 将 ci.yml 粘贴到 GitHub Actions web validator 或使用 act --dryrun

# 6. No Business Code Touched
git diff --stat main -- 'backend/app/' 'frontend/src/pages/' 'frontend/src/components/' 'frontend/src/stores/' 'frontend/src/router/'
# 预期输出：空（无变更）
```
