from typing import Annotated
from uuid import UUID
import httpx
import jwt
from fastapi import Depends, Header, HTTPException, status
from .config import get_settings

async def get_current_user_id(authorization: Annotated[str | None, Header()] = None) -> UUID:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization.split(" ", 1)[1].strip()
    settings = get_settings()
    try:
        payload = jwt.decode(token, options={"verify_signature": False, "verify_exp": True})
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing subject")
        return UUID(user_id)
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from exc

async def get_access_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    return authorization.split(" ", 1)[1].strip()

async def supabase_request(method: str, path: str, user_id: UUID, **kwargs) -> httpx.Response:
    settings = get_settings()
    token = kwargs.pop("token", None)
    if not token:
        raise HTTPException(status_code=401, detail="Access token unavailable")
    headers = kwargs.pop("headers", {})
    headers.update({"apikey": settings.supabase_publishable_key, "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    async with httpx.AsyncClient(base_url=f"{settings.supabase_url}/rest/v1", timeout=15) as client:
        return await client.request(method, path, headers=headers, **kwargs)
