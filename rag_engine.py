import os
import pickle
import requests
import faiss
import numpy as np
import google.generativeai as genai

# -------------------------
# Paths & URLs
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCS_PATH = os.path.join(BASE_DIR, "documents.pkl")
FAISS_PATH = os.path.join(BASE_DIR, "faiss_index.idx")  # match your uploaded file extension

DOCS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/documents.pkl"
FAISS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/faiss_index.idx"

# -------------------------
# Auto-download helper
# -------------------------
def download_if_missing(url: str, path: str) -> None:
    """Download a file if it's missing."""
    if not os.path.exists(path):
        print(f"⬇️ Downloading {os.path.basename(path)} ...")
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"✅ Downloaded {os.path.basename(path)}")

# Ensure files exist
download_if_missing(DOCS_URL, DOCS_PATH)
download_if_missing(FAISS_URL, FAISS_PATH)

# -------------------------
# Load documents & FAISS index
# -------------------------
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)

faiss_index = faiss.read_index(FAISS_PATH)

# -------------------------
# Gemini API setup
# -------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def embed_query(query: str) -> np.ndarray:
    """Convert a query into an embedding using Gemini API."""
    result = genai.embed_content(
        model="models/embedding-001",
        content=query
    )
    return np.array(result["embedding"], dtype="float32")

# -------------------------
# Retrieval
# -------------------------
def retrieve_context(query: str, k: int = 5):
    """Retrieve top-k most relevant documents for a query."""
    query_vec = embed_query(query).reshape(1, -1)
    scores, indices = faiss_index.search(query_vec, k)

    results = []
    for idx, score in zip(indices[0], scores[0]):
        if idx < len(documents):
            doc = documents[idx]
            results.append({
                "content": doc.get("content", ""),
                "score": float(score)
            })
    return results
