

from pathlib import Path
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_similar_documents(prompt: str, top_k: int = 3):
    doc_dir = Path("uploads/processed")
    doc_texts = []
    doc_sources = []

    for txt_file in doc_dir.glob("*.txt"):
        try:
            content = txt_file.read_text(encoding="utf-8")
            doc_texts.append(content)
            doc_sources.append(txt_file.name)
        except Exception:
            continue

    if not doc_texts:
        return []

    doc_embeddings = model.encode(doc_texts, convert_to_tensor=True)
    query_embedding = model.encode(prompt, convert_to_tensor=True)

    scores = util.cos_sim(query_embedding, doc_embeddings)[0]
    top_indices = scores.topk(k=top_k).indices.tolist()

    return [{"filename": doc_sources[i], "content": doc_texts[i]} for i in top_indices]