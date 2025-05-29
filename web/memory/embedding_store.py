# Basic in-memory embedding store with toggleable usage

from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

MAX_EMBEDDINGS = 1000
use_store = os.getenv("USE_EMBED_STORE", "true").lower() == "true"

embedding_db: Dict[str, Tuple[List[float], str]] = {}

def set_use_store(value: bool) -> None:
    global use_store
    use_store = value
    logger.info(f"[EMBEDDING TOGGLE] Embedding store enabled: {use_store}")

def add_embedding(identifier: str, vector: List[float]) -> None:
    if not use_store:
        return

    if not isinstance(vector, list) or not all(isinstance(v, (int, float)) for v in vector):
        raise ValueError("Embedding vector must be a list of numbers.")

    if len(embedding_db) >= MAX_EMBEDDINGS:
        oldest_id = next(iter(embedding_db))
        logger.warning(f"[EMBEDDING WARNING] Max limit reached. Removing oldest entry: {oldest_id}")
        del embedding_db[oldest_id]

    timestamp = datetime.utcnow().isoformat()
    embedding_db[identifier] = (vector, timestamp)

def get_embedding(identifier: str) -> Optional[List[float]]:
    if not use_store:
        return None

    entry = embedding_db.get(identifier)
    return entry[0] if entry else None

def get_all_embeddings() -> List[Tuple[str, List[float]]]:
    if not use_store:
        return []

    return [(k, v[0]) for k, v in embedding_db.items()]

def clear_embeddings() -> None:
    if not use_store:
        return

    embedding_db.clear()

def get_store_summary() -> Dict[str, int]:
    return {
        "enabled": int(use_store),
        "count": len(embedding_db),
        "max": MAX_EMBEDDINGS
    }