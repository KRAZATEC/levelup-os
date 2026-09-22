from datetime import datetime

from fastapi import HTTPException

from .providers import parse_with_gemini, parse_with_groq, parse_with_openai
from ..config import get_settings


async def parse_quest_input(text: str, now: datetime, timezone: str, provider: str | None = None) -> dict:
    settings = get_settings()
    selected = provider or settings.ai_default_provider
    parsers = {"openai": parse_with_openai, "groq": parse_with_groq, "gemini": parse_with_gemini}
    parser = parsers.get(selected)
    if parser is None:
        raise HTTPException(status_code=400, detail="Unsupported AI provider")
    try:
        return await parser(text, now.isoformat(), timezone)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI provider failed: {selected}") from exc
