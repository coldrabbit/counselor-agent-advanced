import logging
from dataclasses import dataclass, field
from typing import Callable, Any

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    name: str
    description: str
    role: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    handler: Callable | None = None


class AgentRegistry:
    _instance = None
    _agents: dict[str, Agent] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents = {}
        return cls._instance

    def register(self, agent: Agent):
        self._agents[agent.name] = agent
        logger.info(f"Agent registered: {agent.name} ({agent.description})")

    def get(self, name: str) -> Agent | None:
        return self._agents.get(name)

    def list_agents(self) -> list[dict]:
        return [
            {"name": a.name, "description": a.description, "role": a.role, "tools": a.tools}
            for a in self._agents.values()
        ]

    def find_agent(self, task_description: str) -> Agent | None:
        """根据任务描述自动匹配合适的 Agent（简单关键词匹配）。"""
        keywords_map = {
            "通知": "notice_agent", "生成通知": "notice_agent",
            "谈话": "talk_agent", "谈心": "talk_agent", "记录": "talk_agent",
            "风险": "risk_agent", "预警": "risk_agent", "安全": "risk_agent",
            "学情": "academic_agent", "成绩": "academic_agent", "学业": "academic_agent",
            "心理": "counseling_agent", "健康": "counseling_agent",
            "就业": "employment_agent", "实习": "employment_agent", "招聘": "employment_agent",
        }
        for keyword, agent_name in keywords_map.items():
            if keyword in task_description:
                return self._agents.get(agent_name)
        return self._agents.get("notice_agent")  # 默认


registry = AgentRegistry()
