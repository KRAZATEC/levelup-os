from datetime import datetime
from fastapi import HTTPException
from .providers import parse_with_gemini, parse_with_groq, parse_with_openai
from ..config import get_settings

async def parse_quest_input(text: str, now: datetime, timezone: str, provider: str | None = None) -> dict:
    settings = get_settings()
    parsers = {"openai": (parse_with_openai, settings.openai_api_key), "groq": (parse_with_groq, settings.groq_api_key), "gemini": (parse_with_gemini, settings.gemini_api_key)}
    selected = provider or settings.ai_default_provider
    ordered = [selected] + [name for name in parsers if name != selected]
    errors: list[str] = []
    for name in ordered:
        parser, key = parsers[name]
        if not key:
            errors.append(f"{name}: not configured")
            continue
        try:
            return await parser(text, now.isoformat(), timezone)
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}")
    raise HTTPException(status_code=502, detail={"message": "All configured AI providers failed", "providers": errors})
