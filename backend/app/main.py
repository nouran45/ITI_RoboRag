from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.query import router as query_router
from .core.config import settings
from .services.generation import GenerationService
from .services.retrieval import RetrievalService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load expensive RAG resources once when the API starts.
    """

    print("Loading RoboRAG services...")

    app.state.retrieval_service = RetrievalService()
    app.state.generation_service = GenerationService()

    print("RoboRAG services loaded successfully.")

    yield

    print("RoboRAG API shutting down.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


# CORS
origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


app.include_router(query_router)