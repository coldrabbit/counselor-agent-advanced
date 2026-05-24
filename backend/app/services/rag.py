import logging

logger = logging.getLogger(__name__)


class RAGService:
    """RAG 检索增强生成服务。从知识库检索相关文档，构建增强提示词。"""

    def __init__(self, db_session):
        self.db = db_session

    def retrieve_context(self, query: str, limit: int = 3) -> str:
        from app.repositories.document import DocumentRepository
        docs = DocumentRepository(self.db).search_relevant(query, limit=limit)
        if not docs:
            return ""
        parts = []
        for i, doc in enumerate(docs, 1):
            parts.append(f"【参考资料 {i}】{doc.title}\n{doc.content[:800]}")
        return "\n\n".join(parts)

    def augment_prompt(self, system_prompt: str, user_message: str) -> tuple[str, str]:
        """用知识库内容增强 system prompt。"""
        context = self.retrieve_context(user_message, limit=3)
        if context:
            augmented = (
                f"{system_prompt}\n\n---\n"
                f"以下是与当前任务相关的参考资料，请参考其中的政策、规定和风格：\n\n"
                f"{context}\n---\n"
                f"请基于以上参考资料，结合你的专业知识完成任务。"
            )
            return augmented, user_message
        return system_prompt, user_message
