import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1 import documents, search
from app.core.config import settings
from app.core.elasticsearch import init_elasticsearch, close_elasticsearch
from app.core.redis import init_redis, close_redis

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up...")
    await init_elasticsearch()
    await init_redis()
    yield
    logging.info("Shutting down...")
    await close_elasticsearch()
    await close_redis()

app = FastAPI(
    title="University Knowledge Search",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.get("/")
async def root():
    return {"message": "University Knowledge Search API"}

@app.get("/health")
async def health():
    return {"status": "ok"}