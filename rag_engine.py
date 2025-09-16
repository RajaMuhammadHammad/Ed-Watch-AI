import os
import pickle
import faiss
import numpy as np

# -------------------------
# Paths
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_PATH = os.path.join(BASE_DIR, "documents.pkl")   # stores (text, embedding)
FAISS_PATH = os.path.join(BASE_DIR, "faiss_index.idx")  # FAISS index file

# -------------------------
# Load Documents & Index
# -------------------------
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)   # list of dicts: {"text": str, "embedding": np.array}

faiss_index = faiss.read_index(FAISS_PATH)

# Extract embeddings into array (needed for retrieval)
embeddings = np.array([doc["embedding"] for doc in documents], dtype="float32")


# -------------------------
# Retrieval Function
# -------------------------
def retrieve_context(query_vector, top_k=3):
    """
    Retrieve top_k most relevant docs based on vector similarity.
    query_vector: np.array of shape (d,) already precomputed
    """
    if not isinstance(query_vector, np.ndarray):
        query_vector = np.array(query_vector, dtype="float32")

    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)

    # Search in FAISS
    distances, indices = faiss_index.search(query_vector, top_k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(documents):
            results.append(documents[idx]["text"])
    return results
