import os
import pickle
import faiss
import requests
import numpy as np

# -------------------------
# Paths
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_PATH = os.path.join(BASE_DIR, "documents.pkl")
FAISS_PATH = os.path.join(BASE_DIR, "faiss_index.faiss")
IDX_PATH = os.path.join(BASE_DIR, "faiss_index.idx")

DOCS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/documents.pkl"
IDX_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/faiss_index.idx"

# -------------------------
# Download helper
# -------------------------
def download_file(url, dest):
    if not os.path.exists(dest):
        print(f"⬇️ Downloading {os.path.basename(dest)} ...")
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"✅ Downloaded {os.path.basename(dest)}")
    else:
        print(f"✅ Found cached {os.path.basename(dest)}")

# -------------------------
# Ensure files exist
# -------------------------
download_file(DOCS_URL, DOCS_PATH)

# Prefer .faiss, otherwise convert from .idx
if not os.path.exists(FAISS_PATH):
    download_file(IDX_URL, IDX_PATH)
    print("🔄 Converting .idx → .faiss ...")
    idx_index = faiss.read_index(IDX_PATH)
    faiss.write_index(idx_index, FAISS_PATH)
    print("✅ Converted and saved as faiss_index.faiss")

# -------------------------
# Load documents + FAISS
# -------------------------
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)

faiss_index = faiss.read_index(FAISS_PATH)

print(f"📂 Loaded {len(documents)} documents")
print(f"📦 FAISS index dimension: {faiss_index.d}")

# -------------------------
# Retrieval
# -------------------------
def retrieve_context(query_vec: np.ndarray, k: int = 5):
    """Retrieve top-k docs given an embedding vector."""
    scores, indices = faiss_index.search(query_vec.reshape(1, -1), k)
    results = []
    for idx, score in zip(indices[0], scores[0]):
        if idx < len(documents):
            results.append({
                "content": documents[idx]["content"],
                "score": float(score)
            })
    return results
