import json
import logging

from app.prompts.activity import build_activity_planning_prompt
from app.services.ai.client import AIService

logger = logging.getLogger(__name__)


def generate_activity_plan(
    theme: str,
    budget: str = "",
    participants: str = "",
    counselor_profile: dict | None = None,
) -> dict:
    """
    独立的活动策划任务。

    Input:  theme (活动主题), budget (预算), participants (参与人数), counselor_profile (辅导员信息)
    Output: {title, plan, schedule, host_script, promotion, summary_template,
             model, token_usage, duration_ms, success, error}
    """
    logger.info(f"Activity planning started: theme={theme}")

    system_prompt = build_activity_planning_prompt(counselor_profile)

    user_message = (
        f"请为以下活动策划方案：\n"
        f"主题：{theme}\n"
        f"预算：{budget or '未指定'}\n"
        f"参与人数：{participants or '未指定'}"
    )

    ai = AIService()
    result = ai.chat(system_prompt=system_prompt, user_message=user_message)

    if not result.get("success"):
        return {
            "success": False,
            "title": "",
            "plan": "",
            "schedule": "",
            "host_script": "",
            "promotion": "",
            "summary_template": "",
            "model": result.get("model", ""),
            "token_usage": result.get("token_usage", 0),
            "duration_ms": result.get("duration_ms", 0),
            "error": result.get("error", "AI generation failed"),
        }

    # 解析 AI 返回的 JSON
    content = result["content"]
    try:
        plan = json.loads(content)
    except json.JSONDecodeError:
        clean = content.strip().removeprefix("```json").removesuffix("```").strip()
        try:
            plan = json.loads(clean)
        except json.JSONDecodeError:
            return {
                "success": False,
                "title": "",
                "plan": "",
                "schedule": "",
                "host_script": "",
                "promotion": "",
                "summary_template": "",
                "model": result["model"],
                "token_usage": result["token_usage"],
                "duration_ms": result["duration_ms"],
                "error": "Failed to parse AI output",
            }

    logger.info(f"Activity planning success: title={plan.get('title', '')}")

    return {
        "success": True,
        "title": plan.get("title", ""),
        "plan": plan.get("plan", ""),
        "schedule": plan.get("schedule", ""),
        "host_script": plan.get("host_script", ""),
        "promotion": plan.get("promotion", ""),
        "summary_template": plan.get("summary_template", ""),
        "model": result["model"],
        "token_usage": result["token_usage"],
        "duration_ms": result["duration_ms"],
        "error": "",
    }
