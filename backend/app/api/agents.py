from fastapi import APIRouter
from app.agents.registry import registry
import app.agents.defined_agents  # noqa: F401 — 触发注册

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("")
def list_agents():
    return {"agents": registry.list_agents()}


@router.get("/match")
def match_agent(description: str):
    agent = registry.find_agent(description)
    if agent:
        return {"matched": agent.name, "description": agent.description, "tools": agent.tools}
    return {"matched": None, "error": "未找到合适的 Agent"}
