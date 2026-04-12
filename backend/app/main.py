from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import admin, health, lessons, pets, profiles, sessions
from app.bootstrap import bootstrap_app
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title="HappyEllie API", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bootstrap_app()
app.mount("/assets", StaticFiles(directory=settings.asset_dir), name="assets")

app.include_router(health.router, prefix="/api/v1")
app.include_router(lessons.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(pets.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {
        "name": "HappyEllie API",
        "env": settings.app_env,
        "docs": "/docs",
        "health": "/api/v1/health",
        "profile": f"/api/v1/profiles/{settings.default_student_id}",
    }
