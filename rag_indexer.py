from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

documents = []
vectors = []

def load_documents():

    global documents, vectors
    with open('knowledge_base.txt', 'r') as f:
        texts = f.read().split("\n\n")

    documents = texts
    vectors = [model.encode(text) for text in documents]

def search_documents(query, top_k=2):

    qvec = model.encode(query)

    scores = []

    for i, vec in enumerate(vectors):
        score = np.dot(qvec, vec)
        scores.append((score, documents[i]))
    scores.sort(reverse=True)
    return [doc for _, doc in scores[:top_k]]