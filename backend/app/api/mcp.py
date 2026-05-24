from fastapi import APIRouter
from pydantic import BaseModel
from app.tools.registry import registry
import app.tools.builtin_tools  # noqa: F401 — 触发工具注册

router = APIRouter(prefix="/mcp", tags=["mcp"])


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict = {}


@router.get("/tools")
def list_tools():
    return {"tools": registry.list_tools()}


@router.post("/call")
async def call_tool(req: ToolCallRequest):
    return await registry.call_tool(req.name, req.arguments)
