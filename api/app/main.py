from fastapi import FastAPI

from app.routers import health

app = FastAPI(title="zw-blog")
app.include_router(health.router)
