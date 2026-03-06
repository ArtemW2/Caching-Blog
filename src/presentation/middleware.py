import json
import time
from collections import defaultdict
from typing import Any

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int, period: int) -> None:
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.records: defaultdict[Any, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        ip = request.client.host
        now = time.time()

        self.records[ip] = [t for t in self.records[ip] if t > now - self.period]

        if len(self.records[ip]) >= self.calls:
            return Response(
                content=json.dumps({"detail": "Превышено число запросов"}),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
            )

        self.records[ip].append(now)
        response: Response = await call_next(request)

        return response
