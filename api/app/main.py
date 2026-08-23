from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.errors import register_exception_handlers
from app.routers import auth, health

app = FastAPI(title="zw-blog")
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.public_web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(auth.router)
