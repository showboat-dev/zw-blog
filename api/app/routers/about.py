from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin
from app.models import AboutPage
from app.services.articles import utcnow

router = APIRouter()


class AboutBody(BaseModel):
    body_md: str


@router.get("/api/about")
def get_about(db: Session = Depends(get_db)) -> dict:
    page = db.scalar(select(AboutPage).where(AboutPage.id == 1))
    return {"body_md": page.body_md if page else ""}


@router.put("/api/admin/about")
def put_about(
    body: AboutBody,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
) -> dict:
    page = db.scalar(select(AboutPage).where(AboutPage.id == 1))
    if page is None:
        page = AboutPage(id=1, body_md=body.body_md, updated_at=utcnow())
        db.add(page)
    else:
        page.body_md = body.body_md
        page.updated_at = utcnow()
    db.commit()
    return {"body_md": page.body_md}
