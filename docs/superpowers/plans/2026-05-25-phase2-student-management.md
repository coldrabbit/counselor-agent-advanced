# Phase 2 — 学生数据管理 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）逐任务实现。步骤使用复选框（`- [ ]`）语法跟踪进度。

**目标：** 实现学生和班级 CRUD 管理，支持按班级筛选和姓名/学号搜索

**架构：** 后端新增 Class/Student 模型、Repository、API 路由，遵循现有分层模式；前端新增 StudentManagement 页面（el-table + 筛选栏 + el-dialog 弹窗），Pinia store 管理状态。

**技术栈：** FastAPI + SQLAlchemy + Alembic + Vue 3 + Element Plus + Pinia

---

### 任务 1：创建 Class + Student 数据库模型和迁移

**文件：**
- 创建：`backend/app/models/class.py`
- 创建：`backend/app/models/student.py`
- 修改：`backend/app/models/__init__.py`
- 生成：`backend/alembic/versions/002_students_classes.py`

- [ ] **步骤 1：编写测试（先确认当前 16 个测试通过）**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/ -q
```
预期：16 passed

- [ ] **步骤 2：创建 class.py 模型**

```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    grade: Mapped[str] = mapped_column(String(32), default="")
    major: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

- [ ] **步骤 3：创建 student.py 模型**

```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    student_id: Mapped[str] = mapped_column(String(64), nullable=False)
    class_id: Mapped[str] = mapped_column(String(36), ForeignKey("classes.id"), nullable=True)
    phone: Mapped[str] = mapped_column(String(32), default="")
    risk_level: Mapped[str] = mapped_column(String(16), default="low")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

- [ ] **步骤 4：更新 models/__init__.py**

在现有 import 末尾添加：
```python
from app.models.class_model import Class
from app.models.student import Student
```

- [ ] **步骤 5：更新 alembic/env.py 导入新模型**

在 `backend/alembic/env.py` 中，添加：
```python
from app.models.class_model import Class  # noqa: F401
from app.models.student import Student  # noqa: F401
```

- [ ] **步骤 6：生成并运行迁移**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
alembic revision --autogenerate -m "002_students_classes"
alembic upgrade head
```
预期：Running upgrade → 002_students_classes

- [ ] **步骤 7：验证模型可导入**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -c "from app.models import Class, Student; print('OK')"
```
预期：OK

- [ ] **步骤 8：Commit**

```bash
git add backend/app/models/ backend/alembic/
git commit -m "feat: add Class and Student models with migration"
```

---

### 任务 2：创建 Schema + Repository + API 路由（后端全部代码）

**文件：**
- 创建：`backend/app/schemas/class.py`
- 创建：`backend/app/schemas/student.py`
- 创建：`backend/app/repositories/class.py`
- 创建：`backend/app/repositories/student.py`
- 创建：`backend/app/api/classes.py`
- 创建：`backend/app/api/students.py`
- 修改：`backend/app/main.py`（注册路由）
- 修改：`backend/app/repositories/__init__.py`
- 修改：`backend/app/schemas/__init__.py`

- [ ] **步骤 1：创建 schemas/class.py**

```python
from pydantic import BaseModel


class ClassCreate(BaseModel):
    name: str
    grade: str = ""
    major: str = ""


class ClassResponse(BaseModel):
    id: str
    name: str
    grade: str
    major: str
    model_config = {"from_attributes": True}
```

- [ ] **步骤 2：创建 schemas/student.py**

```python
from pydantic import BaseModel


class StudentCreate(BaseModel):
    name: str
    student_id: str
    class_id: str | None = None
    phone: str = ""
    risk_level: str = "low"


class StudentUpdate(BaseModel):
    name: str | None = None
    student_id: str | None = None
    class_id: str | None = None
    phone: str | None = None
    risk_level: str | None = None


class StudentResponse(BaseModel):
    id: str
    name: str
    student_id: str
    class_id: str | None = None
    phone: str
    risk_level: str
    created_at: str | None = None
    updated_at: str | None = None
    model_config = {"from_attributes": True}
```

- [ ] **步骤 3：创建 repositories/class.py**

```python
from sqlalchemy.orm import Session
from app.models.class_model import Class
from app.repositories.base import BaseRepository


class ClassRepository(BaseRepository[Class]):
    def __init__(self, db: Session):
        super().__init__(Class, db)

    def list_all(self):
        return super().list_all(order_by=Class.created_at.asc())
```

- [ ] **步骤 4：创建 repositories/student.py**

```python
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.student import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, db: Session):
        super().__init__(Student, db)

    def list_all(self, class_id: str | None = None, search: str | None = None):
        stmt = select(self.model)
        if class_id:
            stmt = stmt.where(Student.class_id == class_id)
        if search:
            stmt = stmt.where(
                (Student.name.contains(search)) | (Student.student_id.contains(search))
            )
        stmt = stmt.order_by(Student.created_at.desc())
        return self.db.scalars(stmt).all()
```

- [ ] **步骤 5：创建 api/classes.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.class_model import ClassCreate, ClassResponse
from app.repositories.class_model import ClassRepository

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("", response_model=list[ClassResponse])
def list_classes(db: Session = Depends(get_db)):
    return ClassRepository(db).list_all()


@router.post("", response_model=ClassResponse)
def create_class(req: ClassCreate, db: Session = Depends(get_db)):
    return ClassRepository(db).create(name=req.name, grade=req.grade, major=req.major)
```

- [ ] **步骤 6：创建 api/students.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.repositories.student import StudentRepository

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentResponse])
def list_students(
    class_id: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return StudentRepository(db).list_all(class_id=class_id, search=search)


@router.post("", response_model=StudentResponse)
def create_student(req: StudentCreate, db: Session = Depends(get_db)):
    return StudentRepository(db).create(
        name=req.name,
        student_id=req.student_id,
        class_id=req.class_id,
        phone=req.phone,
        risk_level=req.risk_level,
    )


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: str, req: StudentUpdate, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    student = repo.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    return repo.update(student, **update_data)


@router.delete("/{student_id}")
def delete_student(student_id: str, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    student = repo.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    repo.delete(student)
    return {"ok": True}
```

- [ ] **步骤 7：更新 main.py 注册路由**

在 `create_app()` 中，添加两行 router 注册（与现有路由并列）：
```python
from app.api.classes import router as class_router
from app.api.students import router as student_router

# 在 app.include_router 区域添加：
app.include_router(class_router, prefix="/api")
app.include_router(student_router, prefix="/api")
```

- [ ] **步骤 8：更新 repositories/__init__.py**

添加：
```python
from app.repositories.class_model import ClassRepository
from app.repositories.student import StudentRepository
```
并在 `__all__` 中添加 `"ClassRepository", "StudentRepository"`

- [ ] **步骤 9：更新 schemas/__init__.py**

添加：
```python
from app.schemas.class_model import ClassCreate, ClassResponse
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
```

- [ ] **步骤 10：验证**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -c "from app.main import app; print('OK')"
python -m pytest tests/ -q
```
预期：OK + 16 passed

- [ ] **步骤 11：Commit**

```bash
git add backend/app/schemas/ backend/app/repositories/ backend/app/api/ backend/app/main.py
git commit -m "feat: add Class and Student schemas, repositories, and API routes"
```

---

### 任务 3：编写后端测试

**文件：**
- 创建：`backend/tests/test_api/test_classes.py`
- 创建：`backend/tests/test_api/test_students.py`

- [ ] **步骤 1：编写 test_classes.py**

```python
class TestClassCRUD:
    def test_list_empty(self, client):
        resp = client.get("/api/classes")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_and_list(self, client):
        resp = client.post("/api/classes", json={
            "name": "2024级软件1班", "grade": "2024", "major": "软件工程"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "2024级软件1班"
        assert data["grade"] == "2024"

        resp2 = client.get("/api/classes")
        assert len(resp2.json()) == 1
```

- [ ] **步骤 2：运行班级测试**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/test_api/test_classes.py -v
```
预期：2 passed

- [ ] **步骤 3：编写 test_students.py**

```python
class TestStudentCRUD:
    def test_create_student(self, client):
        cls = client.post("/api/classes", json={
            "name": "2024级软件1班", "grade": "2024", "major": "软件工程"
        }).json()
        resp = client.post("/api/students", json={
            "name": "李明", "student_id": "2024001",
            "class_id": cls["id"], "phone": "13800001111", "risk_level": "low"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "李明"
        assert data["risk_level"] == "low"

    def test_list_with_filters(self, client):
        cls = client.post("/api/classes", json={
            "name": "2024级软件1班", "grade": "2024", "major": "软件工程"
        }).json()
        client.post("/api/students", json={
            "name": "李明", "student_id": "2024001", "class_id": cls["id"]
        })
        client.post("/api/students", json={
            "name": "王红", "student_id": "2024002", "class_id": cls["id"]
        })

        resp = client.get(f"/api/students?class_id={cls['id']}")
        assert len(resp.json()) == 2

        resp = client.get("/api/students?search=李明")
        assert len(resp.json()) == 1

    def test_update_student(self, client):
        cls = client.post("/api/classes", json={"name": "测试班"}).json()
        student = client.post("/api/students", json={
            "name": "测试", "student_id": "0001", "class_id": cls["id"]
        }).json()
        resp = client.put(f"/api/students/{student['id']}", json={"risk_level": "high"})
        assert resp.json()["risk_level"] == "high"

    def test_delete_student(self, client):
        cls = client.post("/api/classes", json={"name": "测试班"}).json()
        student = client.post("/api/students", json={
            "name": "待删除", "student_id": "9999", "class_id": cls["id"]
        }).json()
        resp = client.delete(f"/api/students/{student['id']}")
        assert resp.json() == {"ok": True}

    def test_get_not_found(self, client):
        assert client.get("/api/students/nonexistent").status_code == 404
```

- [ ] **步骤 4：运行全部测试**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/ -v
```
预期：21 passed

- [ ] **步骤 5：Commit**

```bash
git add backend/tests/
git commit -m "test: add student and class API tests"
```

---

### 任务 4：创建前端 Store + API 层

**文件：**
- 创建：`frontend/src/api/students.ts`
- 创建：`frontend/src/stores/student.ts`

- [ ] **步骤 1：创建 api/students.ts**

```typescript
import axios from 'axios'

export interface ClassItem {
  id: string
  name: string
  grade: string
  major: string
}

export interface StudentItem {
  id: string
  name: string
  student_id: string
  class_id: string | null
  phone: string
  risk_level: string
  created_at: string | null
  updated_at: string | null
}

export interface StudentCreate {
  name: string
  student_id: string
  class_id: string | null
  phone: string
  risk_level: string
}

export interface StudentUpdate {
  name?: string
  student_id?: string
  class_id?: string | null
  phone?: string
  risk_level?: string
}

export function listClasses(): Promise<ClassItem[]> {
  return axios.get('/api/classes').then(r => r.data)
}

export function createClass(data: { name: string; grade?: string; major?: string }): Promise<ClassItem> {
  return axios.post('/api/classes', data).then(r => r.data)
}

export function listStudents(params?: { class_id?: string; search?: string }): Promise<StudentItem[]> {
  return axios.get('/api/students', { params }).then(r => r.data)
}

export function createStudent(data: StudentCreate): Promise<StudentItem> {
  return axios.post('/api/students', data).then(r => r.data)
}

export function updateStudent(id: string, data: StudentUpdate): Promise<StudentItem> {
  return axios.put(`/api/students/${id}`, data).then(r => r.data)
}

export function deleteStudent(id: string): Promise<void> {
  return axios.delete(`/api/students/${id}`)
}
```

- [ ] **步骤 2：创建 stores/student.ts**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  listClasses, createClass,
  listStudents, createStudent, updateStudent, deleteStudent,
  type ClassItem, type StudentItem, type StudentCreate, type StudentUpdate,
} from '../api/students'

export const useStudentStore = defineStore('student', () => {
  const classes = ref<ClassItem[]>([])
  const students = ref<StudentItem[]>([])
  const loading = ref(false)

  async function fetchClasses() {
    classes.value = await listClasses()
  }

  async function addClass(name: string, grade: string, major: string) {
    const cls = await createClass({ name, grade, major })
    classes.value.push(cls)
    ElMessage.success('班级添加成功')
    return cls
  }

  async function fetchStudents(classId?: string, search?: string) {
    loading.value = true
    try {
      students.value = await listStudents({ class_id: classId, search })
    } finally {
      loading.value = false
    }
  }

  async function addStudent(data: StudentCreate) {
    await createStudent(data)
    ElMessage.success('学生添加成功')
    await fetchStudents()
  }

  async function editStudent(id: string, data: StudentUpdate) {
    await updateStudent(id, data)
    ElMessage.success('学生更新成功')
    await fetchStudents()
  }

  async function removeStudent(id: string) {
    await deleteStudent(id)
    ElMessage.success('学生已删除')
    await fetchStudents()
  }

  return {
    classes, students, loading,
    fetchClasses, addClass,
    fetchStudents, addStudent, editStudent, removeStudent,
  }
})
```

- [ ] **步骤 3：验证前端构建**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/frontend
npm run build
```
预期：构建成功

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/api/students.ts frontend/src/stores/student.ts
git commit -m "feat: add student store and API layer"
```

---

### 任务 5：创建 StudentManagement.vue 页面 + 路由

**文件：**
- 创建：`frontend/src/pages/StudentManagement.vue`
- 修改：`frontend/src/router/index.ts`

- [ ] **步骤 1：创建页面组件**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useStudentStore } from '../stores/student'
import type { StudentItem } from '../api/students'

const store = useStudentStore()

const filterClassId = ref('')
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('添加学生')
const editingId = ref<string | null>(null)

const showClassDialog = ref(false)
const newClassName = ref('')
const newClassGrade = ref('')
const newClassMajor = ref('')

const form = ref({ name: '', student_id: '', class_id: '', phone: '', risk_level: 'low' })

const riskOptions = [
  { label: '低风险', value: 'low' },
  { label: '中风险', value: 'medium' },
  { label: '高风险', value: 'high' },
]

function riskTagType(level: string) {
  if (level === 'low') return 'success'
  if (level === 'high') return 'danger'
  return 'warning'
}

function riskLabel(level: string) {
  if (level === 'low') return '低'
  if (level === 'high') return '高'
  return '中'
}

onMounted(() => {
  store.fetchClasses()
  store.fetchStudents()
})

function handleSearch() {
  store.fetchStudents(filterClassId.value || undefined, searchQuery.value || undefined)
}

function openCreate() {
  dialogTitle.value = '添加学生'
  editingId.value = null
  form.value = { name: '', student_id: '', class_id: '', phone: '', risk_level: 'low' }
  dialogVisible.value = true
}

function openEdit(student: StudentItem) {
  dialogTitle.value = '编辑学生'
  editingId.value = student.id
  form.value = {
    name: student.name,
    student_id: student.student_id,
    class_id: student.class_id || '',
    phone: student.phone,
    risk_level: student.risk_level,
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (editingId.value) {
    await store.editStudent(editingId.value, { ...form.value })
  } else {
    await store.addStudent({ ...form.value, class_id: form.value.class_id || null })
  }
  dialogVisible.value = false
}

async function handleDelete(id: string, name: string) {
  try {
    await ElMessageBox.confirm(`确定删除学生「${name}」吗？`, '确认删除', { type: 'warning' })
    await store.removeStudent(id)
  } catch { /* cancelled */ }
}

async function handleAddClass() {
  if (!newClassName.value.trim()) return
  await store.addClass(newClassName.value.trim(), newClassGrade.value.trim(), newClassMajor.value.trim())
  showClassDialog.value = false
  newClassName.value = ''
  newClassGrade.value = ''
  newClassMajor.value = ''
}
</script>

<template>
  <div class="student-page">
    <header class="page-header">
      <h1>📋 学生数据管理</h1>
      <p class="subtitle">管理学院学生基本信息，支持按班级筛选和姓名搜索</p>
    </header>

    <!-- Filters -->
    <div class="filter-bar">
      <el-select v-model="filterClassId" placeholder="班级筛选" clearable style="width:200px" @change="handleSearch">
        <el-option v-for="c in store.classes" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-input v-model="searchQuery" placeholder="搜索姓名或学号..." clearable style="width:240px"
        @keyup.enter="handleSearch" @clear="handleSearch">
        <template #prefix>🔍</template>
      </el-input>
      <el-button @click="handleSearch">搜索</el-button>
      <div class="spacer" />
      <el-button type="primary" @click="openCreate">+ 添加学生</el-button>
      <el-button @click="showClassDialog = true">+ 添加班级</el-button>
    </div>

    <!-- Table -->
    <el-table :data="store.students" v-loading="store.loading" class="student-table">
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="student_id" label="学号" width="140" />
      <el-table-column label="班级" width="180">
        <template #default="{ row }">
          {{ store.classes.find(c => c.id === row.class_id)?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机" width="160" />
      <el-table-column label="风险等级" width="120">
        <template #default="{ row }">
          <el-tag :type="riskTagType(row.risk_level)" size="small">{{ riskLabel(row.risk_level) }}风险</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id, row.name)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Student Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="480px">
      <el-form label-position="top">
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" placeholder="学生姓名" />
        </el-form-item>
        <el-form-item label="学号" required>
          <el-input v-model="form.student_id" placeholder="学号" />
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="form.class_id" placeholder="选择班级" clearable style="width:100%">
            <el-option v-for="c in store.classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="form.phone" placeholder="手机号" />
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="form.risk_level" style="width:100%">
            <el-option v-for="o in riskOptions" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- Class Dialog -->
    <el-dialog v-model="showClassDialog" title="添加班级" width="400px">
      <el-form label-position="top">
        <el-form-item label="班级名称" required>
          <el-input v-model="newClassName" placeholder="例如：2024级软件1班" />
        </el-form-item>
        <el-form-item label="年级">
          <el-input v-model="newClassGrade" placeholder="例如：2024" />
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="newClassMajor" placeholder="例如：软件工程" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showClassDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddClass">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.student-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 24px;
}

.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 26px; color: #4a7c6f; margin: 0 0 6px 0; font-weight: 700; }
.subtitle { color: #909399; font-size: 14px; margin: 0; }

.filter-bar {
  display: flex; gap: 12px; align-items: center;
  margin-bottom: 16px; flex-wrap: wrap;
}
.spacer { flex: 1; }

.student-table { border-radius: 12px; overflow: hidden; }
</style>
```

- [ ] **步骤 2：更新路由**

在 `frontend/src/router/index.ts` 中添加：
```typescript
{
  path: '/students',
  name: 'students',
  component: () => import('../pages/StudentManagement.vue'),
}
```

- [ ] **步骤 3：更新 App.vue 导航栏**

在 `frontend/src/App.vue` 的 `<nav>` 中添加导航链接：
```html
<router-link to="/students">学生管理</router-link>
```

- [ ] **步骤 4：验证前端构建**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/frontend
npm run build
```
预期：构建成功

- [ ] **步骤 5：Commit**

```bash
git add frontend/src/pages/StudentManagement.vue frontend/src/router/index.ts frontend/src/App.vue
git commit -m "feat: add StudentManagement page with CRUD and filters"
```

---

### 任务 6：最终验证

- [ ] **步骤 1：全量后端测试**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/ -v
```
预期：21 passed

- [ ] **步骤 2：前端构建**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/frontend
npm run build
```
预期：构建成功

- [ ] **步骤 3：Git 状态**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced
git status
```
预期：干净

- [ ] **步骤 4：Commit**

```bash
git add -A
git commit -m "chore: final verification phase2 student management"
```
