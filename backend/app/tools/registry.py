import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class ToolRegistry:
    """MCP 工具注册中心。"""

    _instance = None
    _tools: dict[str, dict] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register(self, name: str, description: str, input_schema: dict, handler: Callable):
        self._tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "handler": handler,
        }
        logger.info(f"MCP tool registered: {name}")

    def list_tools(self) -> list[dict]:
        return [
            {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
            for t in self._tools.values()
        ]

    async def call_tool(self, name: str, arguments: dict) -> dict:
        if name not in self._tools:
            return {"error": f"Tool not found: {name}"}
        try:
            result = self._tools[name]["handler"](**arguments)
            return {"content": [{"type": "text", "text": str(result)}]}
        except Exception as e:
            logger.exception(f"Tool call failed: {name}")
            return {"error": str(e)}


def tool(name: str, description: str, input_schema: dict):
    """装饰器：将函数注册为 MCP 工具。"""
    def decorator(func):
        ToolRegistry().register(name, description, input_schema, func)
        return func
    return decorator


registry = ToolRegistry()
