import json
import logging

from app.prompts.talk_record import build_talk_record_prompt
from app.services.ai.client import AIService
from app.db.database import SessionLocal
from app.services.rag import RAGService

logger = logging.getLogger(__name__)


def generate_talk_record_task(
    student_name: str,
    student_id: str,
    situation: str,
    counselor_profile: dict | None = None,
) -> dict:
    """
    独立的谈话记录生成任务。

    Input:  student_name, student_id, situation, counselor_profile
    Output: {conversation_record, risk_level, follow_up_advice, parent_advice,
             model, token_usage, duration_ms, success, error}
    """
    logger.info(f"Starting talk record generation, student={student_name}")

    system_prompt = build_talk_record_prompt(counselor_profile)

    user_message = f"请为以下学生生成谈话记录：\n\n学生姓名：{student_name}\n学号：{student_id}\n情况描述：{situation}"

    ai = AIService()

    # RAG 知识库检索增强
    db = SessionLocal()
    try:
        rag = RAGService(db)
        system_prompt, user_message = rag.augment_prompt(system_prompt, user_message)
    finally:
        db.close()

    result = ai.chat(
        system_prompt=system_prompt,
        user_message=user_message,
    )

    if not result["success"]:
        return {
            "success": False,
            "conversation_record": "",
            "risk_level": "",
            "follow_up_advice": "",
            "parent_advice": "",
            "model": result.get("model", ""),
            "token_usage": result.get("token_usage", 0),
            "duration_ms": result.get("duration_ms", 0),
            "error": result.get("error", "Unknown error"),
        }

    try:
        record_data = json.loads(result["content"])
    except json.JSONDecodeError:
        clean = result["content"].strip().removeprefix("```json").removesuffix("```").strip()
        try:
            record_data = json.loads(clean)
        except json.JSONDecodeError:
            return {
                "success": False,
                "conversation_record": "",
                "risk_level": "",
                "follow_up_advice": "",
                "parent_advice": "",
                "model": result["model"],
                "token_usage": result["token_usage"],
                "duration_ms": result["duration_ms"],
                "error": "Failed to parse AI output",
            }

    risk_level = record_data.get("risk_level", "medium")
    if risk_level not in ("low", "medium", "high"):
        risk_level = "medium"

    logger.info(f"Talk record generation success: student={student_name}, risk={risk_level}")

    return {
        "success": True,
        "conversation_record": record_data.get("conversation_record", ""),
        "risk_level": risk_level,
        "follow_up_advice": record_data.get("follow_up_advice", ""),
        "parent_advice": record_data.get("parent_advice", ""),
        "model": result["model"],
        "token_usage": result["token_usage"],
        "duration_ms": result["duration_ms"],
        "error": "",
    }
