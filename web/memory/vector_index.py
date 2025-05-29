import faiss
import numpy as np
import os
import pickle
from typing import List, Tuple

INDEX_PATH = "web/memory/faiss_index.index"
ID_MAP_PATH = "web/memory/id_map.pkl"

class VectorIndex:
    def __init__(self, dim: int):
        self.dim = dim
        base_index = faiss.IndexFlatIP(dim)
        self.index = faiss.IndexIDMap(base_index)
        self.id_map = []  # Track string IDs
        self.reverse_id_map = {}  # string ID -> numeric ID
        self.next_id = 0
        if os.path.exists(INDEX_PATH) and os.path.exists(ID_MAP_PATH):
            self.load()

    def add(self, vector: np.ndarray, id_str: str):
        if id_str in self.reverse_id_map:
            print(f"[VectorIndex] Duplicate ID '{id_str}' — skipping.")
            return
        norm_vector = vector / (np.linalg.norm(vector) + 1e-10)
        numeric_id = self.next_id
        self.index.add_with_ids(norm_vector.reshape(1, -1), np.array([numeric_id]))
        self.reverse_id_map[id_str] = numeric_id
        self.id_map.append(id_str)
        self.next_id += 1

    def query(self, vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        norm_vector = vector / (np.linalg.norm(vector) + 1e-10)
        scores, indices = self.index.search(norm_vector.reshape(1, -1), top_k)
        results = []
        for idx, numeric_id in enumerate(indices[0]):
            if numeric_id == -1:
                continue
            if numeric_id < len(self.id_map):
                results.append((self.id_map[numeric_id], float(scores[0][idx])))
        return results

    def save(self):
        faiss.write_index(self.index, INDEX_PATH)
        with open(ID_MAP_PATH, "wb") as f:
            pickle.dump((self.id_map, self.reverse_id_map, self.next_id), f)

    def load(self):
        loaded_index = faiss.read_index(INDEX_PATH)
        if not isinstance(loaded_index, faiss.IndexIDMap):
            raise RuntimeError("Expected an IndexIDMap instance in saved index.")
        self.index = loaded_index
        with open(ID_MAP_PATH, "rb") as f:
            self.id_map, self.reverse_id_map, self.next_id = pickle.load(f)
