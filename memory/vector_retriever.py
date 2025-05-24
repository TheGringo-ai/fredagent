import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "chat_logs.jsonl"

model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_similar_logs(current_prompt: str, top_k: int = 3):
    if not LOG_FILE.exists():
        return []

    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not logs:
        return []

    prompts = [entry["prompt"] for entry in logs]
    prompt_embeddings = model.encode(prompts, convert_to_tensor=True)
    current_embedding = model.encode(current_prompt, convert_to_tensor=True)

    scores = util.cos_sim(current_embedding, prompt_embeddings)[0]
    top_indices = scores.topk(k=top_k).indices

    return [logs[i] for i in top_indices]
