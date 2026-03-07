from flask import Flask, request, jsonify
import redis
import json

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.route('/chat', methods=['POST'])
def chat():
    
    session_id = request.json['session_id']
    message = request.json['message']

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

    response = f"AI response to: {message}"

    # Cache the response for 1 hour
    r.set(cache_key, response, ex=3600)

    return jsonify({
        "cached": False,
        "response": response,
        "history": history
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)