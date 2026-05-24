"""预定义的状态图工作流。"""
from app.engine.graph import StateGraph


def create_risk_workflow() -> StateGraph:
    """创建风险处理工作流：发现 → 审核 → 谈话 → 联系家长 → 跟进 → 解决。"""

    def discover_risks(state: dict) -> dict:
        state["step_result"] = "风险数据已采集"
        state["risk_level"] = state.get("risk_level", "medium")
        return state

    def review_risk(state: dict) -> dict:
        state["step_result"] = "人工审核完成"
        return state

    def conduct_interview(state: dict) -> dict:
        state["step_result"] = "已进行谈话"
        return state

    def contact_parents(state: dict) -> dict:
        state["step_result"] = "已联系家长"
        return state

    def follow_up(state: dict) -> dict:
        state["step_result"] = "跟进中"
        return state

    def resolve(state: dict) -> dict:
        state["step_result"] = "已解决"
        state["resolved"] = True
        return state

    def end(state: dict) -> dict:
        return state

    def route_by_risk(state: dict) -> str:
        level = state.get("risk_level", "medium")
        if level == "high":
            return "contact_parents"
        return "conduct_interview"

    wf = StateGraph("risk_workflow")
    wf.add_node("discover", discover_risks, "发现风险")
    wf.add_node("review", review_risk, "人工审核")
    wf.add_node("conduct_interview", conduct_interview, "进行谈话")
    wf.add_node("contact_parents", contact_parents, "联系家长")
    wf.add_node("follow_up", follow_up, "跟进观察")
    wf.add_node("resolve", resolve, "已解决")
    wf.add_node("__end__", end, "结束")
    wf.set_entry_point("discover")
    wf.add_edge("discover", "review")
    wf.add_conditional_edges("review", route_by_risk, {
        "contact_parents": "contact_parents",
        "conduct_interview": "conduct_interview",
    })
    wf.add_edge("conduct_interview", "follow_up")
    wf.add_edge("contact_parents", "follow_up")
    wf.add_edge("follow_up", "resolve")
    wf.add_edge("resolve", "__end__")
    return wf


def create_notice_workflow_graph() -> StateGraph:
    """通知生成工作流：输入事件 → AI生成 → 人工审核 → 完成。"""

    def input_event(state: dict) -> dict:
        state["step_result"] = "事件已录入"
        return state

    def ai_generate(state: dict) -> dict:
        state["step_result"] = "AI 已生成通知"
        state["generated"] = True
        return state

    def human_review(state: dict) -> dict:
        state["step_result"] = "等待人工审核"
        return state

    def approved(state: dict) -> dict:
        state["step_result"] = "审核通过"
        state["approved"] = True
        return state

    def rejected(state: dict) -> dict:
        state["step_result"] = "退回修改"
        return state

    def end(state: dict) -> dict:
        return state

    def route_review(state: dict) -> str:
        """路由审核结果。无操作时返回空字符串触发暂停等待。"""
        action = state.get("__action__")
        if action == "approve":
            return "approved"
        elif action == "reject":
            return "rejected"
        return ""  # 不在 targets 中 → _get_next 返回 None → WAITING_APPROVAL

    wf = StateGraph("notice_workflow")
    wf.add_node("input", input_event, "输入事件")
    wf.add_node("generate", ai_generate, "AI生成")
    wf.add_node("review", human_review, "人工审核")
    wf.add_node("approved", approved, "已通过")
    wf.add_node("rejected", rejected, "已退回")
    wf.add_node("__end__", end, "结束")
    wf.set_entry_point("input")
    wf.add_edge("input", "generate")
    wf.add_edge("generate", "review")
    wf.add_conditional_edges("review", route_review,
        {"approved": "approved", "rejected": "rejected"}
    )
    wf.add_edge("approved", "__end__")
    wf.add_edge("rejected", "generate")  # 退回到 AI 重新生成
    return wf
