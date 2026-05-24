# Layer 3：交付准备 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）逐任务实现。步骤使用复选框（`- [ ]`）语法跟踪进度。

**目标：** Docker 部署配置 + 安全加固完善

**架构：** 前端多阶段构建（Node build → nginx serve），后端单阶段（Python + uvicorn），docker-compose 编排两服务。

**技术栈：** Docker, docker-compose, nginx, uvicorn

---

### 任务 1：后端 Dockerfile

**文件：**
- 创建：`backend/Dockerfile`
- 创建：`backend/.dockerignore`

- [ ] **步骤 1：创建 .dockerignore**

```
__pycache__/
*.pyc
*.db
.env
.venv/
venv/
tests/
.git/
*.md
```

- [ ] **步骤 2：创建 Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **步骤 3：验证构建**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
docker build -t counselor-backend .
```
预期：镜像构建成功

- [ ] **步骤 4：Commit**

```bash
git add backend/Dockerfile backend/.dockerignore
git commit -m "feat: add backend Dockerfile"
```

---

### 任务 2：前端 Dockerfile

**文件：**
- 创建：`frontend/Dockerfile`
- 创建：`frontend/.dockerignore`
- 创建：`frontend/nginx.conf`

- [ ] **步骤 1：创建 .dockerignore**

```
node_modules/
dist/
.git/
*.md
```

- [ ] **步骤 2：创建 nginx.conf**

```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

- [ ] **步骤 3：创建 Dockerfile**

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **步骤 4：验证构建**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/frontend
docker build -t counselor-frontend .
```
预期：镜像构建成功

- [ ] **步骤 5：Commit**

```bash
git add frontend/Dockerfile frontend/.dockerignore frontend/nginx.conf
git commit -m "feat: add frontend Dockerfile with nginx"
```

---

### 任务 3：docker-compose 编排

**文件：**
- 创建：`docker-compose.yml`

- [ ] **步骤 1：创建 docker-compose.yml**

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/counselor.db:/app/counselor.db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

- [ ] **步骤 2：Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add docker-compose for backend + frontend"
```

---

### 任务 4：完善 .gitignore（前端 + 根目录补充）

**文件：**
- 修改：`.gitignore`（Layer 1 已创建，追加内容）
- 创建：`frontend/.gitignore`（如果已存在则追加）

- [ ] **步骤 1：在根 .gitignore 追加**

```
# 前端
frontend/dist/
frontend/node_modules/

# Superpowers
.superpowers/
```

- [ ] **步骤 2：确认 frontend/.gitignore 存在**

运行：`ls /Users/songjie/mine/code/counselor-agent-advanced/frontend/.gitignore`

如果不存在则创建：
```
node_modules/
dist/
*.local
```

- [ ] **步骤 3：从 git 清理不应追踪的文件**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced
git rm --cached -r frontend/node_modules 2>/dev/null
git rm --cached -r frontend/dist 2>/dev/null
git rm --cached -r .superpowers 2>/dev/null
```

- [ ] **步骤 4：Commit**

```bash
git add .gitignore frontend/.gitignore
git commit -m "chore: complete .gitignore for all environments"
```

---

### 任务 5：最终验证

- [ ] **步骤 1：全量测试**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/ -v
```
预期：所有测试通过（≥15 tests）

- [ ] **步骤 2：Alembic 迁移验证**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
alembic upgrade head
```
预期：Running upgrade -> 001_initial，无错误

- [ ] **步骤 3：docker-compose 验证**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced
docker compose build
```
预期：两服务均构建成功

- [ ] **步骤 4：Git 状态验证**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced
git status
```
预期：无敏感文件被追踪（.env、*.db、__pycache__ 均不在 staging 区）

- [ ] **步骤 5：Commit**

```bash
git add -A
git commit -m "chore: final verification of Layer 3 deployment setup"
```
