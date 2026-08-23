from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.errors import register_exception_handlers
from app import db as database
from app.routers import admin, articles, auth, health

app = FastAPI(title="zw-blog")
register_exception_handlers(app)


@app.on_event("startup")
def on_startup() -> None:
    if database.SessionLocal is None:
        database.init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.public_web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(admin.router)
