import redis
import json
import time
from rag_indexer import load_documents, search_documents

from vector_memory import store_memory, search_memory

load_documents()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
print("Worker started...")

while True:
    job = r.brpop("queue:jobs")
    data = json.loads(job[1])
    session_id = data['session_id']
    message = data['message']
    print(f"Processing job for session {session_id} with message: {message}")

    # retrieve similar memories
    context_docs = search_documents(message)
    
    context = "\n".join(context_docs)

    if context:
        context_text = context
    else:
        context_text = ""
    time.sleep(2)  # simulate processing time

    response = f"""Context:{context}
    
                Answer: 
                Based on the knowledge above, here is the answer to your question: {message}"""
                
    cache_key = f"cache:{message}"
    r.set(cache_key, response, ex=3600)  # cache for 1 hour

    store_memory(message)
    print(f"Job completed for session {session_id}. Response: {response}")