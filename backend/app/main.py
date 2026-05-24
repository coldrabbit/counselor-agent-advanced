from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.notices import router as notice_router
from app.api.counselor import router as counselor_router
from app.api.talk_records import router as talk_records_router
from app.api.classes import router as class_router
from app.api.students import router as student_router
from app.api.imports import router as import_router
from app.api.templates import router as template_router
from app.api.risks import router as risk_router
from app.api.analysis import router as analysis_router
from app.api.export import router as export_router
from app.api.ocr import router as ocr_router
from app.api.mcp import router as mcp_router
from app.api.notify import router as notify_router
from app.api.documents import router as document_router
from app.api.agents import router as agent_router
from alembic.config import Config as AlembicConfig
from alembic import command


def create_app() -> FastAPI:
    app = FastAPI(title="Counselor OS - Notification Generator")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(notice_router, prefix="/api")
    app.include_router(counselor_router, prefix="/api")
    app.include_router(talk_records_router, prefix="/api")
    app.include_router(class_router, prefix="/api")
    app.include_router(student_router, prefix="/api")
    app.include_router(import_router, prefix="/api")
    app.include_router(template_router, prefix="/api")
    app.include_router(risk_router, prefix="/api")
    app.include_router(analysis_router, prefix="/api")
    app.include_router(export_router, prefix="/api")
    app.include_router(ocr_router, prefix="/api")
    app.include_router(mcp_router, prefix="/api")
    app.include_router(notify_router, prefix="/api")
    app.include_router(document_router, prefix="/api")
    app.include_router(agent_router, prefix="/api")

    @app.on_event("startup")
    def on_startup():
        import app.tools.builtin_tools  # noqa: F401 — 确保 MCP 工具在启动时注册
        import app.agents.defined_agents  # noqa: F401 — 确保 AI Agent 在启动时注册
        alembic_cfg = AlembicConfig("alembic.ini")
        command.upgrade(alembic_cfg, "head")

    return app


app = create_app()
