import time
import asyncio
import redis
from rate_limit.rate_limiter import SlidingWindowRateLimiter

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
limiter = SlidingWindowRateLimiter(r, limit=5, window_seconds=10)

for key in r.keys('ratelimit:user_123:*'):
    r.delete(key)


async def fire_request(i: int):
    allowed = await asyncio.to_thread(limiter.is_allowed, 'user_123')
    print(f"request {i+1}: {'ALLOWED' if allowed else 'BLOCKED'}")

async def main():
    results = await asyncio.gather(*[fire_request(i) for i in range(20)])
    print(results)
    # allowed_count = sum(results)
    # print("\nTotal allowed: {allowed_count} (limit was 5)")

asyncio.run(main())



# for i in range(20):
#     if i + 1 == 6:
#         time.sleep(12)
#     allowed = limiter.is_allowed('user_123')
#     print(f"request {i+1}: {'ALLOWED' if allowed else 'BLOCKED'}")