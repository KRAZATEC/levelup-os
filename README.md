# LevelUpOS

AI-powered gamified personal operating system combining Life RPG, QuestFlow, and Skill Tree.

## Phase 1

This repository contains the initial Next.js, FastAPI, Docker, and Supabase foundation.

## Structure

- `apps/web`: Next.js frontend
- `apps/api`: FastAPI backend
- `supabase/migrations`: PostgreSQL migrations and RLS policies

## Local setup

1. Copy `.env.example` to `.env`.
2. Add Supabase and AI provider credentials.
3. Start the stack:

```bash
docker compose up --build
```

4. Open the frontend at `http://localhost:3000`.
5. Open the API docs at `http://localhost:8000/docs`.

## AI providers

The application is designed to support OpenAI, Groq, and Gemini through a provider abstraction. Phase 1 includes configuration placeholders; QuestFlow integration will be added in a later phase.
