from typing import Any

from openai import AsyncOpenAI

from ..config import get_settings


QUEST_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "clarification_needed": {"type": "boolean"},
        "clarification_question": {"type": ["string", "null"]},
        "quests": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "quest_type": {"type": "string", "enum": ["main", "side", "daily", "challenge"]},
                    "category": {"type": ["string", "null"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                    "difficulty": {"type": "integer", "minimum": 1, "maximum": 5},
                    "estimated_minutes": {"type": ["integer", "null"]},
                    "scheduled_date": {"type": ["string", "null"]},
                    "deadline": {"type": ["string", "null"]},
                    "skill_slugs": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "description", "quest_type", "category", "priority", "difficulty", "estimated_minutes", "scheduled_date", "deadline", "skill_slugs"]
            }
        }
    },
    "required": ["summary", "clarification_needed", "clarification_question", "quests"]
}


def system_prompt(now: str, timezone: str) -> str:
    return f"""You are QuestFlow, a task-structuring assistant. Current time: {now}. User timezone: {timezone}.
Convert messy user intentions into realistic quests. Never invent a deadline. Use null when information is missing. Ask for clarification for ambiguous dates. Split large goals into actionable quests. Use only these skill slugs when relevant: ai-ml, backend-engineering, full-stack, cybersecurity, cloud-devops, dsa, communication, health, finance, discipline. Return only the requested structured object."""


async def parse_with_openai(text: str, now: str, timezone: str) -> dict:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "system", "content": system_prompt(now, timezone)}, {"role": "user", "content": text}],
        response_format={"type": "json_schema", "json_schema": {"name": "questflow_output", "strict": True, "schema": QUEST_SCHEMA}},
    )
    import json
    return json.loads(response.choices[0].message.content)


async def parse_with_groq(text: str, now: str, timezone: str) -> dict:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "system", "content": system_prompt(now, timezone)}, {"role": "user", "content": text}],
        response_format={"type": "json_object"},
    )
    import json
    return json.loads(response.choices[0].message.content)


async def parse_with_gemini(text: str, now: str, timezone: str) -> dict:
    settings = get_settings()
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model, generation_config={"response_mime_type": "application/json"})
    response = await model.generate_content_async(f"{system_prompt(now, timezone)}\n\nUser input:\n{text}")
    import json
    return json.loads(response.text)
