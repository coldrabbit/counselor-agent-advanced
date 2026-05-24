import json
import logging

from app.prompts.notice import build_notice_prompt
from app.services.ai.client import AIService

logger = logging.getLogger(__name__)


def generate_notice_task(
    event: str,
    time: str | None = None,
    location: str | None = None,
    participants: str | None = None,
    counselor_profile: dict | None = None,
) -> dict:
    """
    独立的通知生成任务。

    Input:  event (事件描述), time/location/participants (可选结构化字段), counselor_profile (辅导员信息)
    Output: {title, formal_notice, wechat_notice, parent_notice, sms_notice,
             model, token_usage, duration_ms, success, error}
    """
    logger.info(f"Starting notice generation task, event length={len(event)}")

    system_prompt = build_notice_prompt(counselor_profile)

    user_message = f"请为以下事件生成通知：\n\n{event}"
    if time or location or participants:
        user_message += "\n\n补充信息（必须使用，不要编造或修改）："
        if time:
            user_message += f"\n- 时间：{time}"
        if location:
            user_message += f"\n- 地点：{location}"
        if participants:
            user_message += f"\n- 参加人员：{participants}"

    ai = AIService()
    result = ai.chat(
        system_prompt=system_prompt,
        user_message=user_message,
    )

    if not result["success"]:
        return {
            "success": False,
            "title": "",
            "formal_notice": "",
            "wechat_notice": "",
            "parent_notice": "",
            "sms_notice": "",
            "model": result.get("model", ""),
            "token_usage": result.get("token_usage", 0),
            "duration_ms": result.get("duration_ms", 0),
            "error": result.get("error", "Unknown error"),
        }

    try:
        notice_data = json.loads(result["content"])
    except json.JSONDecodeError:
        clean = result["content"].strip().removeprefix("```json").removesuffix("```").strip()
        try:
            notice_data = json.loads(clean)
        except json.JSONDecodeError:
            return {
                "success": False,
                "title": "",
                "formal_notice": "",
                "wechat_notice": "",
                "parent_notice": "",
                "sms_notice": "",
                "model": result["model"],
                "token_usage": result["token_usage"],
                "duration_ms": result["duration_ms"],
                "error": "Failed to parse AI output",
            }

    logger.info(f"Notice generation success: title={notice_data.get('title', '')}")

    return {
        "success": True,
        "title": notice_data.get("title", ""),
        "formal_notice": notice_data.get("formal_notice", ""),
        "wechat_notice": notice_data.get("wechat_notice", ""),
        "parent_notice": notice_data.get("parent_notice", ""),
        "sms_notice": notice_data.get("sms_notice", ""),
        "model": result["model"],
        "token_usage": result["token_usage"],
        "duration_ms": result["duration_ms"],
        "error": "",
    }
