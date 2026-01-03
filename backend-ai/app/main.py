"""FastAPI main application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import Base, async_engine
from app.api import ingest_router, assign_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create tables if needed
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown: Cleanup
    await async_engine.dispose()


app = FastAPI(
    title="AI Document Assignment System",
    description="ระบบจำแนกและมอบหมายเอกสารอัตโนมัติด้วย AI",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest_router, prefix="/api/v1")
app.include_router(assign_router, prefix="/api/v1")

# Mount static files for document preview
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

# Go up from app/main.py to root, then to doc
# Current: app/main.py -> parent=app -> parent=backend-ai -> doc is sibling of app?
# Based on ingest.py: DOC_STORAGE_PATH = Path(__file__).parent.parent.parent / "doc"
# ingest.py is in app/api/, so parent.parent.parent is root.
# main.py is in app/, so parent.parent is root.

BASE_DIR = Path(__file__).resolve().parent.parent
DOC_DIR = BASE_DIR / "doc"
DOC_DIR.mkdir(exist_ok=True)

app.mount("/api/v1/files", StaticFiles(directory=str(DOC_DIR)), name="files")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Document Assignment System",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
