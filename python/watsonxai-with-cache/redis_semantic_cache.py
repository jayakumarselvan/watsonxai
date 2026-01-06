import redis
import time
import os
from dotenv import load_dotenv
from langchain_core.globals import set_llm_cache
from langchain_redis import RedisSemanticCache
from watsonx_ai import WatsonxAiService
from embedding import MPNetEmbeddings

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.from_url(REDIS_URL)
print(redis_client.ping())


embeddings = MPNetEmbeddings()

semantic_cache = RedisSemanticCache(
    redis_url=REDIS_URL, embeddings=embeddings, distance_threshold=0.2
)
set_llm_cache(semantic_cache)

watsonx_service = WatsonxAiService()
watsonx_llm = watsonx_service.get_watsonx_llm()
print("\n")


def execute_with_timing(prompt):
    start_time = time.time()
    result = watsonx_llm.invoke(prompt)
    end_time = time.time()
    return result, end_time - start_time


# Clear the cache
semantic_cache.clear()

# First call (not cached)
prompt1 = "What is the capital of France?"
result1, time1 = execute_with_timing(prompt1)
print("-" * 40)
print(f"\nFirst call (not cached) - prompt : ", prompt1)
print(f"\nTime: {time1:.2f} seconds\n")
print("-" * 40)

# Second call (should be cached)
time.sleep(2)
prompt2 = "Can you tell me the capital city of France?"
result2, time2 = execute_with_timing(prompt2)
print(f"\nSecond call (cached)- prompt : ", prompt2)
print(f"\nTime: {time2:.2f} seconds\n")
print("-" * 40)
print(f"Speed improvement: {time1 / time2:.2f}x faster")
print("-" * 40)
