# Vector store for memory

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(384)

def is_duplicate(lead, threshold=0.85):
    vec = model.encode([lead["name"] + lead["address"]]).astype("float32")
    if index.ntotal == 0:
        index.add(vec)
        return False

    D, _ = index.search(vec, 1)
    similarity = 1 / (1 + D[0][0])

    if similarity > threshold:
        return True

    index.add(vec)
    return False
