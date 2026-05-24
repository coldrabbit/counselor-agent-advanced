# Phase 2 — 学生数据管理 设计文档

**日期**：2026-05-25
**状态**：已确认
**版本**：1.0

---

## 目标

实现学生和班级数据管理功能，为后续 Excel 导入、批量通知、风险预警打基础。

范围：学生 CRUD + 班级 CRUD + 按班级筛选 + 姓名/学号搜索 + 风险等级标签。

---

## 数据模型

### classes

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 主键 |
| name | String(128) | 班级名称（如"2024级软件1班"） |
| grade | String(32) | 年级（如"2024"） |
| major | String(128) | 专业（如"软件工程"） |
| created_at | DateTime | 创建时间 |

### students

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 主键 |
| name | String(64) | 学生姓名 |
| student_id | String(64) | 学号 |
| class_id | FK → classes.id | 所属班级 |
| phone | String(32) | 手机号 |
| risk_level | String(16) | 风险等级：low/medium/high |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

---

## API 设计

### 班级

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /api/classes | 班级列表 |
| POST | /api/classes | 创建班级 |

### 学生

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /api/students?class_id=&search= | 学生列表（可选筛选+搜索） |
| POST | /api/students | 创建学生 |
| PUT | /api/students/{id} | 更新学生 |
| DELETE | /api/students/{id} | 删除学生 |

---

## 前端页面

路由：`/students` — StudentManagement.vue

布局：顶部筛选栏（班级下拉 + 搜索框 + 添加按钮）+ el-table 列表 + 添加/编辑 el-dialog 弹窗

风险等级：low=绿、medium=橙、high=红（el-tag）

---

## 文件变更

### 后端（新建 8 个文件 + 修改 1 个）

| 文件 | 操作 |
|------|------|
| `models/class.py` | **新建** |
| `models/student.py` | **新建** |
| `schemas/class.py` | **新建** |
| `schemas/student.py` | **新建** |
| `repositories/class.py` | **新建** |
| `repositories/student.py` | **新建** |
| `api/classes.py` | **新建** |
| `api/students.py` | **新建** |
| `main.py` | 修改 — 注册路由 + 迁移 |

### 前端（新建 3 个文件 + 修改 1 个）

| 文件 | 操作 |
|------|------|
| `pages/StudentManagement.vue` | **新建** |
| `stores/student.ts` | **新建** |
| `api/students.ts` | **新建** |
| `router/index.ts` | 修改 — 添加 /students 路由 |

### 数据库迁移

- `alembic/versions/002_students_classes.py` — 新增 classes + students 表

---

## 不在本次范围

- Excel 导入（下一个功能）
- 批量通知（后续功能）
- 成绩/考勤关联（Phase 3 学情分析）
- 学生详情页（当前列表即可满足需求）
