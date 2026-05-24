"""轻量级状态图引擎 — LangGraph 模式实现。

支持：
- 有向图工作流定义（节点 + 条件边）
- 状态持久化和恢复（Durable Execution）
- 条件分支路由
- 人工审核检查点
"""

import json
import logging
from datetime import datetime
from typing import Any, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Node:
    name: str
    handler: Callable[[dict], dict]
    description: str = ""


@dataclass
class Edge:
    source: str
    target: str | None = None
    condition: Callable[[dict], str] | None = None


@dataclass
class GraphState:
    data: dict = field(default_factory=dict)
    current_node: str = ""
    history: list[str] = field(default_factory=list)
    checkpoints: list[dict] = field(default_factory=list)
    status: str = "PENDING"
    error: str | None = None


class StateGraph:
    """有向状态图工作流引擎。"""

    def __init__(self, name: str):
        self.name = name
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.state = GraphState()

    def add_node(self, name: str, handler: Callable[[dict], dict], description: str = ""):
        self.nodes[name] = Node(name=name, handler=handler, description=description)
        return self

    def add_edge(self, source: str, target: str):
        self.edges.append(Edge(source=source, target=target))
        return self

    def add_conditional_edges(self, source: str, condition: Callable[[dict], str], targets: dict[str, str]):
        self.edges.append(Edge(source=source, condition=condition))
        setattr(self, f"_{source}_targets", targets)
        return self

    def set_entry_point(self, node_name: str):
        self._entry = node_name
        return self

    def _get_next(self, current: str) -> str | None:
        for edge in self.edges:
            if edge.source == current:
                if edge.target:
                    return edge.target
                elif edge.condition:
                    targets = getattr(self, f"_{current}_targets", {})
                    result = edge.condition(self.state.data)
                    return targets.get(result)
        return None

    def checkpoint(self):
        """保存当前状态为检查点（持久化快照）。"""
        cp = {
            "node": self.state.current_node,
            "data": json.loads(json.dumps(self.state.data, default=str)),
            "history": list(self.state.history),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.state.checkpoints.append(cp)
        logger.info(f"[{self.name}] checkpoint at: {self.state.current_node}")
        return cp

    def restore(self, checkpoint: dict):
        """从检查点恢复。"""
        self.state.current_node = checkpoint["node"]
        self.state.data = checkpoint["data"]
        self.state.history = checkpoint["history"]
        logger.info(f"[{self.name}] restored to: {self.state.current_node}")

    def run(self, initial_data: dict | None = None) -> dict:
        """执行状态图直到完成。"""
        if initial_data:
            self.state.data.update(initial_data)

        self.state.status = "RUNNING"
        if not self.state.current_node:
            self.state.current_node = self._entry

        try:
            while self.state.current_node:
                node = self.nodes.get(self.state.current_node)
                if not node:
                    self.state.error = f"Node not found: {self.state.current_node}"
                    self.state.status = "FAILED"
                    break

                logger.info(f"[{self.name}] running node: {node.name}")
                self.state.data = node.handler(self.state.data)
                self.state.history.append(self.state.current_node)

                if node.name == "__end__":
                    self.state.status = "SUCCESS"
                    break

                next_node = self._get_next(self.state.current_node)
                if next_node is None and node.name != "__end__":
                    self.state.status = "WAITING_APPROVAL"
                    logger.info(f"[{self.name}] paused at: {node.name} (waiting for approval)")
                    break

                self.state.current_node = next_node

        except Exception as e:
            logger.exception(f"[{self.name}] execution error")
            self.state.status = "FAILED"
            self.state.error = str(e)

        return {
            "status": self.state.status,
            "current_node": self.state.current_node,
            "history": self.state.history,
            "data": self.state.data,
            "error": self.state.error,
        }

    def resume(self, action: str | None = None) -> dict:
        """从中断点恢复执行（用于人工审核后继续）。"""
        if action:
            self.state.data["__action__"] = action
        if self.state.status == "WAITING_APPROVAL":
            next_node = self._get_next(self.state.current_node)
            if next_node:
                self.state.current_node = next_node
                return self.run()
        return self.run()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.state.status,
            "current_node": self.state.current_node,
            "history": self.state.history,
            "nodes": list(self.nodes.keys()),
            "checkpoints": len(self.state.checkpoints),
        }
