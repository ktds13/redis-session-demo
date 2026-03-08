from flask import Flask, request, jsonify
import redis
import json
from vector_memory import search_memory

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

RATE_LIMIT = 5  # messages per minute
RATE_WINDOW = 60  # seconds

def check_rate_limit(user_id):
    
    key = f"rate:{user_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, RATE_WINDOW)
    if count > RATE_LIMIT:
        return False
    return True

@app.route('/chat', methods=['POST'])
def chat():
    
    session_id = request.json['session_id']
    user_id = request.json['user_id']
    message = request.json['message']

    if not check_rate_limit(user_id):
        return jsonify({
            "error": "Rate limit exceeded"
        }), 429

    session_key = f"session:{session_id}"
    cache_key = f"cache:{message}"

    cached = r.get(cache_key)
    if cached:
        return jsonify({
            "cached": True,
            "response": cached
        })
    
    r.rpush(session_key, message)

    # keep only last 20 messages
    r.ltrim(session_key, -20, -1)
    
    history = r.lrange(session_key, 0, -1)

    job = {
        "session_id": session_id,
        "message": message
    }

    r.lpush("queue:jobs", json.dumps(job))
    context = search_memory(message)
    return jsonify({
        "status": "job queued",
        "context_found": context
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)