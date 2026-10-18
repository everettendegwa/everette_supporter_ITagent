from typing import Literal

from pydantic import BaseModel, Field


class GuideSource(BaseModel):
    title: str
    url: str
    publisher: str


class GuideSummary(BaseModel):
    guide_id: str
    title: str
    category: str
    applicable_os: str
    summary: str
    status: str
    sources: list[GuideSource]


class GuideDetail(GuideSummary):
    symptoms: list[str]
    steps: list[str]
    cautions: list[str]
    escalation: str
    tags: list[str]


class GuideSearchResponse(BaseModel):
    query: str
    results: list[GuideSummary]


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=12)
    include_web_search: bool = False


class WebCitation(BaseModel):
    title: str
    url: str


class ChatResponse(BaseModel):
    answer: str
    guide_sources: list[GuideSource]
    web_citations: list[WebCitation]
    web_search_used: bool
    disclaimer: str

