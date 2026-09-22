from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from ..ai.service import parse_quest_input
from ..dependencies import get_current_user_id
from ..schemas_ai import QuestFlowRequest, QuestFlowResponse

router = APIRouter(prefix="/api/v1/questflow", tags=["questflow"])
UserId = Annotated[UUID, Depends(get_current_user_id)]


@router.post("/parse", response_model=QuestFlowResponse)
async def parse_questflow(payload: QuestFlowRequest, user_id: UserId):
    current = payload.now or datetime.now(timezone.utc)
    result = await parse_quest_input(payload.text, current, payload.timezone, payload.provider)
    return result
