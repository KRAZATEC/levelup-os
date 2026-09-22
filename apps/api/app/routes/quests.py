from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from ..dependencies import get_access_token, get_current_user_id, supabase_request
from ..schemas import QuestCreate, QuestResponse, QuestUpdate
router = APIRouter(prefix="/api/v1/quests", tags=["quests"])
UserId = Annotated[UUID, Depends(get_current_user_id)]
Token = Annotated[str, Depends(get_access_token)]

def parse_rows(response) -> list[dict]:
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json() if response.content else []

async def resolve_skill_links(skill_slugs: list[str], user_id: UUID, token: str) -> list[dict]:
    if not skill_slugs:
        return []
    response = await supabase_request("GET", "/skills", user_id, params={"slug": f"in.({','.join(skill_slugs)})", "select": "id,slug"}, token=token)
    skills = parse_rows(response)
    return [{"skill_id": skill["id"], "xp_reward": 25} for skill in skills]

async def insert_skill_links(quest_id: str, links: list[dict], user_id: UUID, token: str) -> None:
    if not links:
        return
    response = await supabase_request("POST", "/quest_skills", user_id, json=[{"quest_id": quest_id, **link} for link in links], token=token)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@router.get("", response_model=list[QuestResponse])
async def list_quests(user_id: UserId, token: Token, quest_status: str | None = Query(default=None, alias="status"), scheduled_date: str | None = None):
    params = {"user_id": f"eq.{user_id}", "select": "*", "order": "created_at.desc"}
    if quest_status: params["status"] = f"eq.{quest_status}"
    if scheduled_date: params["scheduled_date"] = f"eq.{scheduled_date}"
    return parse_rows(await supabase_request("GET", "/quests", user_id, params=params, token=token))

@router.post("", response_model=QuestResponse, status_code=status.HTTP_201_CREATED)
async def create_quest(payload: QuestCreate, user_id: UserId, token: Token):
    data = payload.model_dump(mode="json")
    skill_slugs = data.pop("skill_slugs", [])
    response = await supabase_request("POST", "/quests", user_id, json={**data, "user_id": str(user_id)}, params={"select": "*"}, headers={"Prefer": "return=representation"}, token=token)
    rows = parse_rows(response)
    if not rows: raise HTTPException(status_code=500, detail="Quest was not returned")
    await insert_skill_links(str(rows[0]["id"]), await resolve_skill_links(skill_slugs, user_id, token), user_id, token)
    return rows[0]

@router.patch("/{quest_id}", response_model=QuestResponse)
async def update_quest(quest_id: UUID, payload: QuestUpdate, user_id: UserId, token: Token):
    values = payload.model_dump(exclude_unset=True, mode="json")
    if not values: raise HTTPException(status_code=400, detail="No fields to update")
    values["updated_at"] = datetime.now(timezone.utc).isoformat()
    rows = parse_rows(await supabase_request("PATCH", "/quests", user_id, params={"id": f"eq.{quest_id}", "user_id": f"eq.{user_id}", "select": "*"}, json=values, headers={"Prefer": "return=representation"}, token=token))
    if not rows: raise HTTPException(status_code=404, detail="Quest not found")
    return rows[0]

@router.delete("/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quest(quest_id: UUID, user_id: UserId, token: Token):
    response = await supabase_request("DELETE", "/quests", user_id, params={"id": f"eq.{quest_id}", "user_id": f"eq.{user_id}"}, token=token)
    if response.status_code >= 400: raise HTTPException(status_code=response.status_code, detail=response.text)

@router.post("/{quest_id}/complete")
async def complete_quest(quest_id: UUID, user_id: UserId, token: Token):
    response = await supabase_request("POST", "/rpc/complete_quest_atomic", user_id, json={"p_quest_id": str(quest_id), "p_user_id": str(user_id)}, token=token)
    if response.status_code >= 400:
        detail = response.text
        if "already completed" in detail: raise HTTPException(status_code=409, detail="Quest already completed")
        if "not found" in detail: raise HTTPException(status_code=404, detail="Quest not found")
        raise HTTPException(status_code=response.status_code, detail=detail)
    rows = response.json() if response.content else []
    result = rows[0] if isinstance(rows, list) and rows else rows
    return {"quest": result["quest"], "xp_awarded": result["xp_awarded"], "total_xp": result["total_xp"], "level": result["level"]}
