from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db: Session):
        super().__init__(Document, db)

    def list_all(self, category: str | None = None, search: str | None = None):
        stmt = select(self.model)
        if category:
            stmt = stmt.where(Document.category == category)
        if search:
            stmt = stmt.where(
                (Document.title.contains(search)) |
                (Document.content.contains(search)) |
                (Document.tags.contains(search))
            )
        stmt = stmt.order_by(Document.created_at.desc())
        return self.db.scalars(stmt).all()

    def search_relevant(self, query: str, limit: int = 5) -> list[Document]:
        """关键词匹配检索，返回相关文档。"""
        stmt = select(self.model).where(
            (Document.title.contains(query)) |
            (Document.content.contains(query)) |
            (Document.tags.contains(query))
        ).order_by(Document.created_at.desc()).limit(limit)
        results = self.db.scalars(stmt).all()
        if len(results) < limit:
            # 如果匹配不够，补充同类别的文档
            all_docs = self.db.scalars(select(self.model).order_by(Document.created_at.desc())).all()
            for doc in all_docs:
                if doc not in results and any(kw in doc.title + doc.tags for kw in query[:4]):
                    results.append(doc)
                if len(results) >= limit:
                    break
        return results[:limit]
