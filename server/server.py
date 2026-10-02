import os
import re
import redis
import rpyc
from rpyc.utils.server import ThreadedServer

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
SERVER_ID = os.getenv("SERVER_ID", "server-1")

r_cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

class WordCountService(rpyc.Service):
    def exposed_get_word_count(self, keyword: str, filename: str) -> dict:
        keyword = keyword.strip().lower()
        cache_key = f"{filename}:{keyword}"
        
        # 1. Check Redis Cache
        cached_count = r_cache.get(cache_key)
        if cached_count is not None:
            return {
                "server_id": SERVER_ID,
                "count": int(cached_count),
                "cached": True
            }
        
        # 2. Cache Miss: Compute from file
        file_path = os.path.join("/data", filename)
        if not os.path.exists(file_path):
            return {"server_id": SERVER_ID, "error": f"File '{filename}' not found."}
        
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read().lower()
            tokens = re.findall(r"\b\w+\b", text)
            count = tokens.count(keyword)
        
        # Save to Redis
        r_cache.set(cache_key, count)
        
        return {
            "server_id": SERVER_ID,
            "count": count,
            "cached": False
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 18861))
    print(f"[{SERVER_ID}] Starting RPyC Server on port {port}...")
    server = ThreadedServer(WordCountService, port=port, protocol_config={"allow_public_attrs": True})
    server.start()

