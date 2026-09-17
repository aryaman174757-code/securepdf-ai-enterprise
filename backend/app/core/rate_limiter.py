import time
from typing import Dict, Tuple
from fastapi import HTTPException, status
from app.core.config import settings

class InMemoryRateLimiter:
    """
    Tiered Token-Bucket Rate Limiter with memory auto-pruning.
    Supports Free (5 req/min, 3 heavy/day) and Pro (60 req/min, 200 heavy/day).
    """

    def __init__(self):
        # Key: client_id -> list of timestamps
        self.requests: Dict[str, list[float]] = {}
        # Key: client_id -> list of timestamps for heavy jobs
        self.heavy_jobs: Dict[str, list[float]] = {}

    def check_rate_limit(self, client_id: str, is_pro: bool = False, is_heavy: bool = False) -> bool:
        now = time.time()
        minute_ago = now - 60
        day_ago = now - 86400

        # General request limit
        max_per_min = settings.PRO_RATE_LIMIT_PER_MIN if is_pro else settings.FREE_RATE_LIMIT_PER_MIN
        user_reqs = [ts for ts in self.requests.get(client_id, []) if ts > minute_ago]
        
        if len(user_reqs) >= max_per_min:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: Maximum {max_per_min} requests per minute on your plan."
            )
        
        user_reqs.append(now)
        self.requests[client_id] = user_reqs

        # Heavy job limit
        if is_heavy:
            max_heavy = settings.PRO_HEAVY_JOBS_PER_DAY if is_pro else settings.FREE_HEAVY_JOBS_PER_DAY
            user_heavy = [ts for ts in self.heavy_jobs.get(client_id, []) if ts > day_ago]
            if len(user_heavy) >= max_heavy:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Heavy job limit reached: Maximum {max_heavy} heavy operations per day."
                )
            user_heavy.append(now)
            self.heavy_jobs[client_id] = user_heavy

        return True

rate_limiter = InMemoryRateLimiter()
