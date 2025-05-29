from web.memory.vector_index import VectorIndex  # Ensure FAISS is correctly installed and imported
from sentence_transformers import SentenceTransformer
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from web.memory.summarizer_engine import Summarizer
from web.utils.logger import log_to_file

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "user_log.jsonl"

class MemoryManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name, device="cpu")
        self.index = VectorIndex(dim=self.model.get_sentence_embedding_dimension())
        self.summarizer = Summarizer()

    def encode_text(self, text: str) -> np.ndarray:
        return self.model.encode(text, convert_to_numpy=True)

    def store_text(self, identifier: str, text: str):
        vector = self.encode_text(text)
        self.index.add(vector, identifier)
        self.index.save()

    def retrieve_similar(self, query: str, top_k=5):
        query_vector = self.encode_text(query)
        return self.index.query(query_vector, top_k=top_k)

    def reset_memory(self):
        self.index = VectorIndex(dim=self.model.get_sentence_embedding_dimension())
        self.index.save()

    def store_log_entry(self, log_entry: dict):
        if "timestamp" not in log_entry:
            log_entry["timestamp"] = datetime.utcnow().isoformat()

        text = log_entry.get("text", "")
        if not text:
            return

        identifier = log_entry["timestamp"]

        try:
            log_entry["summary"] = self.summarizer.summarize(text)
            log_entry["intent"] = self.classify_intent(text)
            vector = self.encode_text(text)
            self.index.add(vector, identifier)
            self.index.save()
        except Exception as e:
            log_entry["summary"] = "summarization_failed"
            log_entry["intent"] = "unknown"
            log_entry["error"] = str(e)

        log_to_file(log_entry, filename="user_log.jsonl")

    def get_index_size(self) -> int:
        return len(self.index.id_map)
    def classify_intent(self, text: str) -> str:
        text = text.lower()
        if "how do" in text or "how to" in text:
            return "question"
        elif "error" in text or "failed" in text:
            return "error"
        elif "fix" in text or "update" in text:
            return "instruction"
        return "note"

    def search_by_summary(self, query: str, top_k=5):
        query_vector = self.encode_text(query)
        return self.index.query(query_vector, top_k=top_k)

    def get_log_entries(self, limit=100):
        if not LOG_PATH.exists():
            return []
        with LOG_PATH.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f.readlines()[-limit:]]

if __name__ == "__main__":
    try:
        import faiss
        print("FAISS successfully imported. Version:", faiss.__version__)
    except ImportError as e:
        print("FAISS import failed:", e)