from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.templates import TemplateCreate, TemplateUpdate, TemplateResponse
from app.repositories.templates import TemplateRepository

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateResponse])
def list_templates(category: str | None = Query(None), db: Session = Depends(get_db)):
    return TemplateRepository(db).list_all(category=category)


@router.post("", response_model=TemplateResponse)
def create_template(req: TemplateCreate, db: Session = Depends(get_db)):
    return TemplateRepository(db).create(name=req.name, category=req.category, content=req.content)


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: str, req: TemplateUpdate, db: Session = Depends(get_db)):
    repo = TemplateRepository(db)
    tmpl = repo.get_by_id(template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    return repo.update(tmpl, **update_data)


@router.delete("/{template_id}")
def delete_template(template_id: str, db: Session = Depends(get_db)):
    repo = TemplateRepository(db)
    tmpl = repo.get_by_id(template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    repo.delete(tmpl)
    return {"ok": True}
