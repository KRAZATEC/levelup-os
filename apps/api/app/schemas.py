from datetime import date, datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field
QuestType = Literal["main", "side", "daily", "challenge"]
QuestStatus = Literal["pending", "in_progress", "completed", "skipped", "archived"]
Priority = Literal["low", "medium", "high", "urgent"]
class QuestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    quest_type: QuestType = "side"
    category: str | None = Field(default=None, max_length=100)
    priority: Priority = "medium"
    difficulty: int = Field(default=1, ge=1, le=5)
    estimated_minutes: int | None = Field(default=None, gt=0, le=1440)
    scheduled_date: date | None = None
    deadline: datetime | None = None
    source: Literal["manual", "ai", "voice", "imported"] = "manual"
    skill_slugs: list[str] = Field(default_factory=list, max_length=5)
class QuestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: QuestStatus | None = None
    quest_type: QuestType | None = None
    category: str | None = Field(default=None, max_length=100)
    priority: Priority | None = None
    difficulty: int | None = Field(default=None, ge=1, le=5)
    estimated_minutes: int | None = Field(default=None, gt=0, le=1440)
    scheduled_date: date | None = None
    deadline: datetime | None = None
    skill_slugs: list[str] | None = Field(default=None, max_length=5)
class QuestResponse(BaseModel):
    id: UUID; user_id: UUID; title: str; description: str | None = None; quest_type: QuestType; status: QuestStatus; category: str | None = None; priority: Priority; difficulty: int; estimated_minutes: int | None = None; scheduled_date: date | None = None; deadline: datetime | None = None; completed_at: datetime | None = None; source: str; created_at: datetime; updated_at: datetime
