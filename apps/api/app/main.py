import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.quests import router as quests_router

app = FastAPI(title="LevelUpOS API", version="0.2.0")

origins = [origin.strip() for origin in os.getenv("API_CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(quests_router)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "levelup-os-api", "version": "0.2.0"}
