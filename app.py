from flask import Flask, request, jsonify, Response
import redis
import json
import time
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

def generate_stream(text):
    words = text.split()
    for word in words:
        yield f"data: {word}\n\n"
        time.sleep(0.3)  # simulate delay

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

@app.route("/stream")
def stream():

    message = request.args.get("message")
    response_text = f"Redis is an in-memory data structure store used as a database, cache, and message broker. It supports various data structures such as strings, hashes, lists, sets, and more. Redis is known for its high performance and is often used for real-time applications, caching, and session management."

    return Response(generate_stream(response_text), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5001)