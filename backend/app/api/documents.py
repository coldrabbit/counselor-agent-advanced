from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.document import DocumentCreate, DocumentResponse
from app.repositories.document import DocumentRepository

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    category: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return DocumentRepository(db).list_all(category=category, search=search)


@router.post("", response_model=DocumentResponse)
def create_document(req: DocumentCreate, db: Session = Depends(get_db)):
    return DocumentRepository(db).create(
        title=req.title, content=req.content, category=req.category, tags=req.tags
    )


@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(doc_id: str, req: DocumentCreate, db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    doc = repo.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return repo.update(doc, title=req.title, content=req.content, category=req.category, tags=req.tags)


@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    doc = repo.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    repo.delete(doc)
    return {"ok": True}


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = DocumentRepository(db).get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc
