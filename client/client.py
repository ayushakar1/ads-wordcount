import os
import time
import rpyc

TARGET_HOST = os.getenv("TARGET_HOST", "server")
TARGET_PORT = int(os.getenv("TARGET_PORT", 18861))

def query(keyword: str, filename: str = "alice.txt"):
    # Connect with permission to inspect object attributes over RPC
    conn = rpyc.connect(
        TARGET_HOST, 
        TARGET_PORT, 
        config={"allow_public_attrs": True}
    )
    
    start_time = time.perf_counter()
    result = conn.root.get_word_count(keyword, filename)
    end_time = time.perf_counter()
    
    # Extract values from the remote object BEFORE closing the connection
    server_id = result.get("server_id")
    count = result.get("count")
    cached = result.get("cached")
    err = result.get("error")
    
    # Safely close the RPC connection
    conn.close()
    
    latency_ms = (end_time - start_time) * 1000
    
    if err:
        print(f"[{server_id}] Error: {err}")
    else:
        print(f"[{server_id}] Keyword: '{keyword}' | Count: {count} | "
              f"Cached: {cached} | Latency: {latency_ms:.2f} ms")

if __name__ == "__main__":
    time.sleep(2)  # Wait for server readiness
    print(f"Connecting to {TARGET_HOST}:{TARGET_PORT}...")
    
    # 1st query: Cache Miss
    query("alice")
    # 2nd query: Cache Hit
    query("alice")
    # 3rd query: Cache Miss
    query("rabbit")
