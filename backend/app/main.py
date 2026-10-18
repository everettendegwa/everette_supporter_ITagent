from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, APIStatusError, RateLimitError

from .assistant import AssistantService
from .config import get_settings
from .guides import GuideRepository
from .schemas import ChatRequest, ChatResponse, GuideDetail, GuideSearchResponse


settings = get_settings()
guide_repository = GuideRepository(settings.guide_database_path, include_drafts=settings.serve_draft_guides)
assistant_service = AssistantService(settings, guide_repository)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not settings.guide_database_path.exists():
        raise RuntimeError(f"Guide database not found: {settings.guide_database_path}")
    yield


app = FastAPI(
    title="Windows Support Agent API",
    description="Guide search and chat API for the first Windows troubleshooting agent prototype.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "windows-support-agent-api"}


@app.get("/api/v1/guides/search", response_model=GuideSearchResponse)
def search_guides(q: str = Query(min_length=1, max_length=300), limit: int = Query(default=8, ge=1, le=20)):
    try:
        results = guide_repository.search(q, limit=limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Guide database is unavailable") from exc
    return {"query": q, "results": results}


@app.get("/api/v1/guides/{guide_id}", response_model=GuideDetail)
def get_guide(guide_id: str):
    try:
        guide = guide_repository.get(guide_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Guide database is unavailable") from exc
    if guide is None:
        raise HTTPException(status_code=404, detail="Guide not found")
    return guide


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    history = [turn.model_dump() for turn in request.history]
    try:
        result = assistant_service.answer(request.message, history, request.include_web_search)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RateLimitError as exc:
        raise HTTPException(status_code=503, detail="AI provider rate limit reached; try again shortly") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=502, detail="Could not connect to the AI provider") from exc
    except APIStatusError as exc:
        raise HTTPException(status_code=502, detail="The AI provider returned an error") from exc
    return {
        **result,
        "disclaimer": "This prototype provides instructions only. It cannot inspect or change your computer. Review each step before doing it.",
    }

