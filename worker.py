import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
print("Worker started...")

while True:
    job = r.brpop("queue:jobs")
    data = json.loads(job[1])
    session_id = data['session_id']
    message = data['message']
    print(f"Processing job for session {session_id} with message: {message}")

    # Simulate processing time
    time.sleep(2)
    response = f"AI response to: {message}"
    cache_key = f"cache:{message}"
    r.set(cache_key, response, ex=3600)
    print(f"Job for session {session_id} completed with response: {response}")