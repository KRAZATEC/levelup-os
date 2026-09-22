from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class QuestFlowRequest(BaseModel):
    text: str = Field(min_length=3, max_length=10000)
    timezone: str = "Asia/Kolkata"
    provider: Literal["openai", "groq", "gemini"] | None = None
    now: datetime | None = None


class QuestFlowResponse(BaseModel):
    summary: str
    clarification_needed: bool
    clarification_question: str | None = None
    quests: list[dict]
