from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from ..dependencies import get_current_user_id, supabase_request
from ..schemas import CompleteQuestResponse, QuestCreate, QuestResponse, QuestUpdate
from ..services.xp import level_from_xp, quest_xp

router = APIRouter(prefix="/api/v1/quests", tags=["quests"])
UserId = Annotated[UUID, Depends(get_current_user_id)]


def parse_rows(response) -> list[dict]:
    if response.status_code >= 400:
        detail = response.text or "Supabase request failed"
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json() if response.content else []


@router.get("", response_model=list[QuestResponse])
async def list_quests(
    user_id: UserId,
    authorization: Annotated[str | None, Header()] = None,
    quest_status: str | None = Query(default=None, alias="status"),
    scheduled_date: str | None = None,
):
    params = {"user_id": f"eq.{user_id}", "select": "*", "order": "created_at.desc"}
    if quest_status:
        params["status"] = f"eq.{quest_status}"
    if scheduled_date:
        params["scheduled_date"] = f"eq.{scheduled_date}"
    response = await supabase_request("GET", "/quests", user_id, params=params, token=authorization.split(" ", 1)[1])
    return parse_rows(response)


@router.post("", response_model=QuestResponse, status_code=status.HTTP_201_CREATED)
async def create_quest(
    payload: QuestCreate,
    user_id: UserId,
    authorization: Annotated[str | None, Header()] = None,
):
    response = await supabase_request(
        "POST", "/quests", user_id,
        json={**payload.model_dump(mode="json"), "user_id": str(user_id)},
        params={"select": "*"},
        headers={"Prefer": "return=representation"},
        token=authorization.split(" ", 1)[1],
    )
    rows = parse_rows(response)
    if not rows:
        raise HTTPException(status_code=500, detail="Quest was not returned")
    return rows[0]


@router.patch("/{quest_id}", response_model=QuestResponse)
async def update_quest(
    quest_id: UUID,
    payload: QuestUpdate,
    user_id: UserId,
    authorization: Annotated[str | None, Header()] = None,
):
    values = payload.model_dump(exclude_unset=True, mode="json")
    if not values:
        raise HTTPException(status_code=400, detail="No fields to update")
    values["updated_at"] = datetime.now(timezone.utc).isoformat()
    response = await supabase_request(
        "PATCH", "/quests", user_id,
        params={"id": f"eq.{quest_id}", "user_id": f"eq.{user_id}", "select": "*"},
        json=values,
        headers={"Prefer": "return=representation"},
        token=authorization.split(" ", 1)[1],
    )
    rows = parse_rows(response)
    if not rows:
        raise HTTPException(status_code=404, detail="Quest not found")
    return rows[0]


@router.delete("/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quest(
    quest_id: UUID,
    user_id: UserId,
    authorization: Annotated[str | None, Header()] = None,
):
    response = await supabase_request(
        "DELETE", "/quests", user_id,
        params={"id": f"eq.{quest_id}", "user_id": f"eq.{user_id}"},
        token=authorization.split(" ", 1)[1],
    )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@router.post("/{quest_id}/complete", response_model=CompleteQuestResponse)
async def complete_quest(
    quest_id: UUID,
    user_id: UserId,
    authorization: Annotated[str | None, Header()] = None,
):
    token = authorization.split(" ", 1)[1]
    response = await supabase_request(
        "GET", "/quests", user_id,
        params={"id": f"eq.{quest_id}", "user_id": f"eq.{user_id}", "select": "*"},
        token=token,
    )
    rows = parse_rows(response)
    if not rows:
        raise HTTPException(status_code=404, detail="Quest not found")
    quest = rows[0]
    if quest["status"] == "completed":
        raise HTTPException(status_code=409, detail="Quest already completed")

    xp = quest_xp(quest["difficulty"], quest.get("estimated_minutes"))
    completed_at = datetime.now(timezone.utc).isoformat()
    update = await supabase_request(
        "PATCH", "/quests", user_id,
        params={"id": f"eq.{quest_id}", "user_id": f"eq.{user_id}", "select": "*"},
        json={"status": "completed", "completed_at": completed_at, "updated_at": completed_at},
        headers={"Prefer": "return=representation"},
        token=token,
    )
    updated_rows = parse_rows(update)
    if not updated_rows:
        raise HTTPException(status_code=500, detail="Quest completion failed")

    profile_response = await supabase_request(
        "GET", "/profiles", user_id,
        params={"id": f"eq.{user_id}", "select": "*"},
        token=token,
    )
    profiles = parse_rows(profile_response)
    if not profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile = profiles[0]
    total_xp = profile["total_xp"] + xp
    level = level_from_xp(total_xp)
    profile_update = await supabase_request(
        "PATCH", "/profiles", user_id,
        params={"id": f"eq.{user_id}"},
        json={"total_xp": total_xp, "level": level, "updated_at": completed_at},
        token=token,
    )
    if profile_update.status_code >= 400:
        raise HTTPException(status_code=profile_update.status_code, detail=profile_update.text)

    transaction = await supabase_request(
        "POST", "/xp_transactions", user_id,
        json={"user_id": str(user_id), "quest_id": str(quest_id), "amount": xp, "reason": f"Completed quest: {quest['title']}"},
        headers={"Prefer": "return=minimal"},
        token=token,
    )
    if transaction.status_code >= 400:
        raise HTTPException(status_code=transaction.status_code, detail=transaction.text)

    return {"quest": updated_rows[0], "xp_awarded": xp, "level": level, "total_xp": total_xp}
