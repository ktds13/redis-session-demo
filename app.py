from flask import Flask, request, jsonify
import redis
import json

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.route('/chat', methods=['POST'])
def chat():
    
    session_id = request.json['session_id']
    message = request.json['message']

    key = f"session:{session_id}"
    
    history = r.get(key)

    if history:
        history = json.loads(history)
    else:
        history = []

    history.append(message)
    r.set(key, json.dumps(history), ex=3600)

    return jsonify({
        "session": session_id,
        "history": history
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)