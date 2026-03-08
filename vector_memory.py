from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

memory_store = []

def store_memory(text):

    vector = model.encode(text)
    memory_store.append((text, vector))

def search_memory(query, top_k=1):

    if not memory_store:
        return []
    
    qvec = model.encode(query)

    scores = []

    for item in memory_store:
       score = np.dot(qvec, item[1])
       scores.append((score, item[0]))
    scores.sort(reverse=True)
    
    return [text for _, text in scores[:top_k]]