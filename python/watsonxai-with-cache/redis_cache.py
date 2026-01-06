import redis
import time
import os
from dotenv import load_dotenv
from langchain_core.globals import set_llm_cache
from langchain_redis import RedisCache
from watsonx_ai import WatsonxAiService


load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.from_url(REDIS_URL)
print(redis_client.ping())


redis_cache = RedisCache(redis_url=REDIS_URL)
set_llm_cache(redis_cache)

watsonx_service = WatsonxAiService()
watsonx_llm = watsonx_service.get_watsonx_llm()
print("\n")
print("-" * 40)


def execute_with_timing(prompt):
    start_time = time.time()
    result = watsonx_llm.invoke(prompt)
    end_time = time.time()
    return result, end_time - start_time


# Clear the cache
redis_cache.clear()
# print("Cache cleared")

# First call (not cached)
prompt = "Explain the concept of caching in three sentences."
result1, time1 = execute_with_timing(prompt)
print("-" * 40)
print(f"\nFirst call (not cached) - prompt : ", prompt)
print(f"\nTime: {time1:.2f} seconds\n")
print("-" * 40)

# Second call (should be cached)
time.sleep(2)
result2, time2 = execute_with_timing(prompt)
print(f"\nSecond call (cached)- prompt : ", prompt)
print(f"\nTime: {time2:.2f} seconds\n")
print("-" * 40)
print(f"Speed improvement: {time1 / time2:.2f}x faster")
print("-" * 40)
