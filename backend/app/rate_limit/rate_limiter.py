import time
import redis

class SlidingWindowRateLimiter:
    def __init__(self, redis_client: redis.Redis, limit: int, window_seconds: int = 60):
        self.redis = redis_client
        self.limit = limit
        self.window_seconds = window_seconds

    def _key(self, user_id: str, window_epoch: int) -> str:
        return f"ratelimit: {user_id} : {window_epoch}"

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        current_window = int(now // self.window_seconds)
        previous_window = current_window - 1

        elapsed_in_current = (now % self.window_seconds) / self.window_seconds
        overlap = 1.0 - elapsed_in_current

        current_count = int(self.redis.get(self._key(user_id, current_window)) or 0)
        previous_count = int(self.redis.get(self._key(user_id, previous_window)) or 0)

        weighted_count = current_count + previous_count * overlap

        if weighted_count >= self.limit:
            return False

        new_count = self.redis.incr(self._key(user_id, current_window))
        if new_count == 1:
            self.redis.expire(self._key(user_id, current_window), self.window_seconds * 2)

        return True
        