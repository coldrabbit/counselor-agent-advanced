from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.repositories import CounselorRepository
from app.services.ai.client import AIService
from app.services.rag import RAGService
from app.agents.registry import registry
import app.agents.defined_agents  # noqa: F401
import json

router = APIRouter(prefix="/ask", tags=["ask"])


class AskRequest(BaseModel):
    question: str


@router.post("")
def ask(req: AskRequest, db: Session = Depends(get_db)):
    # 匹配最合适的 Agent
    agent = registry.find_agent(req.question)

    # 获取辅导员信息
    profile = CounselorRepository(db).get_first()
    profile_dict = CounselorRepository(db).to_dict(profile) if profile else None

    # RAG 检索相关知识库文档
    rag = RAGService(db)
    context = rag.retrieve_context(req.question, limit=2)

    # 构建系统提示词
    identity = ""
    if profile_dict and profile_dict.get("name"):
        identity = f"你是{profile_dict.get('college', '')}的辅导员{profile_dict['name']}，一位高校学生工作专家。"
    else:
        identity = "你是一位高校辅导员工作助手，Counselor OS 的 AI 助手。"

    system_prompt = f"""{identity}
你可以帮助辅导员完成以下工作：
- 生成通知文书（正式通知、微信群消息、家长通知、短信）
- 撰写谈心谈话记录
- 学生风险分析
- 学情数据分析
- 活动策划
- 就业指导
- 回答学生工作相关问题

{('相关知识库参考：' + context) if context else ''}

请用友好、专业的语气回答。回答简洁实用，2-5句话为宜（除非问题需要详细回答）。
如果问题与辅导员工作无关，礼貌地引导用户回到工作相关话题。"""

    ai = AIService()
    result = ai.chat(system_prompt=system_prompt, user_message=req.question)

    if result.get("success"):
        try:
            content = result["content"]
            try:
                content = json.loads(content)
                if isinstance(content, dict):
                    content = content.get("answer", content.get("response", result["content"]))
            except (json.JSONDecodeError, AttributeError):
                pass
            return {"success": True, "answer": content, "agent": agent.name if agent else "general"}
        except Exception:
            return {"success": True, "answer": result["content"], "agent": agent.name if agent else "general"}
    return {"success": False, "answer": "抱歉，我暂时无法回答这个问题，请稍后再试。"}
