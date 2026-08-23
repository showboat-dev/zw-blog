import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse

from app.config import settings
from app.deps import require_admin
from app.errors import AppError

router = APIRouter()

ALLOWED = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}
MAX_BYTES = 5_242_880


@router.post("/api/admin/uploads", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    _admin: dict = Depends(require_admin),
) -> dict:
    content_type = file.content_type or ""
    if content_type not in ALLOWED:
        raise AppError(422, "VALIDATION_ERROR", "不支持的文件类型")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise AppError(422, "VALIDATION_ERROR", "文件太大")
    folder = Path(settings.upload_dir)
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ALLOWED[content_type]}"
    (folder / name).write_bytes(data)
    return {"url": f"/api/uploads/{name}"}


@router.get("/api/uploads/{filename}")
def get_upload(filename: str) -> FileResponse:
    path = Path(settings.upload_dir) / filename
    if not path.is_file():
        raise AppError(404, "NOT_FOUND", "文件不存在")
    return FileResponse(path)
