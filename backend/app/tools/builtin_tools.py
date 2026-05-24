"""内置 MCP 工具定义。"""

from app.tools.registry import tool


@tool(
    name="lookup_student",
    description="根据姓名或学号搜索学生信息",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "学生姓名或学号"}
        },
        "required": ["query"],
    },
)
def lookup_student(query: str) -> str:
    from app.db.database import SessionLocal
    from app.repositories.students import StudentRepository
    db = SessionLocal()
    try:
        students = StudentRepository(db).list_all(search=query)
        if not students:
            return "未找到匹配的学生"
        return "\n".join([f"- {s.name} ({s.student_id}), 风险等级: {s.risk_level}" for s in students[:10]])
    finally:
        db.close()


@tool(
    name="get_risk_overview",
    description="获取学生风险总览统计",
    input_schema={"type": "object", "properties": {}, "required": []},
)
def get_risk_overview() -> str:
    from app.db.database import SessionLocal
    from app.repositories.risk import RiskRepository
    db = SessionLocal()
    try:
        stats = RiskRepository(db).get_stats()
        return f"高风险: {stats['high']}人, 中风险: {stats['medium']}人, 低风险: {stats['low']}人, 总计: {stats['total']}条记录"
    finally:
        db.close()


@tool(
    name="list_classes",
    description="获取所有班级列表",
    input_schema={"type": "object", "properties": {}, "required": []},
)
def list_classes() -> str:
    from app.db.database import SessionLocal
    from app.repositories.classes import ClassRepository
    db = SessionLocal()
    try:
        classes = ClassRepository(db).list_all()
        return "\n".join([f"- {c.name} ({c.grade}级 {c.major})" for c in classes])
    finally:
        db.close()
