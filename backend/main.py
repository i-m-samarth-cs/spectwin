from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, AsyncSessionLocal
from app.models import *
from app.database import Base
from app.services.auth import seed_demo_users
from app.routes import auth, projects, artifacts, twin, analysis, admin, evaluation
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_demo_users(db)
    yield

app = FastAPI(
    title="SpecTwin API",
    description="Agentic specification intelligence platform for software teams",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(artifacts.router)
app.include_router(twin.router)
app.include_router(analysis.router)
app.include_router(admin.router)
app.include_router(evaluation.router)

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "mock" if settings.MOCK_MODE else "real", "version": "1.0.0"}
