import time
import redis

class SlidingWindowRateLimiter:

    LUA_SCRIPT = """
    local current_key = KEYS[1]
    local previous_key = KEYS[2]
    local limit = tonumber(ARGV[1])
    local overlap = tonumber(ARGV[2])
    local window_seconds = tonumber(ARGV[3])

    local current_count = tonumber(redis.call('GET', current_key) or '0')
    local previous_count = tonumber(redis.call('GET', previous_key) or '0')

    local weighted_count = current_count + (previous_count * overlap)

    if weighted_count >= limit then
        return 0
    end

    local new_count = redis.call('INCR', current_key)
    if new_count == 1 then
        redis.call('EXPIRE', current_key, window_seconds * 2)
    end

    return 1
    """

    def __init__(self, redis_client: redis.Redis, limit: int, window_seconds: int = 60):
        self.redis = redis_client
        self.limit = limit
        self.window_seconds = window_seconds
        self.script = self.redis.register_script(self.LUA_SCRIPT)

    def _key(self, user_id: str, window_epoch: int) -> str:
        return f"ratelimit: {user_id} : {window_epoch}"

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        current_window = int(now // self.window_seconds)
        previous_window = current_window - 1

        elapsed_in_current = (now % self.window_seconds) / self.window_seconds
        overlap = 1.0 - elapsed_in_current

        # current_count = int(self.redis.get(self._key(user_id, current_window)) or 0)
        # previous_count = int(self.redis.get(self._key(user_id, previous_window)) or 0)

        # weighted_count = current_count + previous_count * overlap

        # if weighted_count >= self.limit:
        #     return False

        # new_count = self.redis.incr(self._key(user_id, current_window))
        # if new_count == 1:
        #     self.redis.expire(self._key(user_id, current_window), self.window_seconds * 2)

        # return True
        
        result = self.script(
            keys=[self._key(user_id, current_window), self._key(user_id, previous_window)],
            args=[self.limit, overlap, self.window_seconds]
        )
        return result == 1