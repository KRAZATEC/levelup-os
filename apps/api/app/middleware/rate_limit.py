import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from ..config import get_settings

_windows: dict[str, deque[float]] = defaultdict(deque)

async def ai_rate_limit(request: Request):
    if not request.url.path.startswith("/api/v1/questflow"):
        return
    key = request.headers.get("authorization", request.client.host if request.client else "unknown")
    now = time.monotonic(); window = _windows[key]
    while window and now - window[0] > 60: window.popleft()
    if len(window) >= get_settings().ai_rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="AI request rate limit exceeded")
    window.append(now)
