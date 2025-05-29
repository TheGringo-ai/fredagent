from fastapi import APIRouter, Request
from sentence_transformers import SentenceTransformer
import json
import os
import numpy as np
from web.memory.vector_index import VectorIndex

router = APIRouter()

model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FAISS-backed VectorIndex after model definition
index = VectorIndex(dim=model.get_sentence_embedding_dimension())

# Load logs and their embeddings at startup
log_file_paths = ['logs/chat_logs.jsonl', 'logs/user_log.jsonl']
logs = []

for path in log_file_paths:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    text = log_entry.get('text') or log_entry.get('prompt') or json.dumps(log_entry)
                    if text:
                        logs.append({
                            "text": text,
                            "source": path,
                            "timestamp": log_entry.get("timestamp", "unknown")
                        })
                except json.JSONDecodeError:
                    continue

if logs:
    for i, entry in enumerate(logs):
        vector = model.encode(entry["text"], convert_to_numpy=True)
        index.add(vector, str(i))
    index.save()

def retrieve_similar_logs(prompt, top_k=5):
    if not logs:
        return []

    prompt_embedding = model.encode([prompt], convert_to_numpy=True)[0]
    results = index.query(prompt_embedding, top_k=top_k)

    formatted = []
    for id_str, score in results:
        idx = int(id_str)
        entry = logs[idx]
        formatted.append({
            "text": entry["text"],
            "score": score,
            "source": entry["source"],
            "timestamp": entry["timestamp"]
        })
    return formatted

@router.post("/vector/query")
async def query_vector_memory(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    if not prompt:
        return {"error": "No prompt provided."}

    results = retrieve_similar_logs(prompt)
    return {"matches": results}