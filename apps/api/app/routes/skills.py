from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException

from ..dependencies import get_current_user_id, supabase_request

router = APIRouter(prefix="/api/v1/skills", tags=["skills"])
UserId = Annotated[UUID, Depends(get_current_user_id)]


def rows(response) -> list[dict]:
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json() if response.content else []


@router.get("/progress")
async def skill_progress(user_id: UserId, authorization: Annotated[str | None, Header()] = None):
    token = authorization.split(" ", 1)[1]
    response = await supabase_request(
        "GET", "/user_skills", user_id,
        params={"user_id": f"eq.{user_id}", "select": "*,skills(*)", "order": "xp.desc"},
        token=token,
    )
    return rows(response)


@router.get("")
async def list_skills(user_id: UserId, authorization: Annotated[str | None, Header()] = None):
    token = authorization.split(" ", 1)[1]
    response = await supabase_request("GET", "/skills", user_id, params={"select": "*", "order": "name.asc"}, token=token)
    return rows(response)
