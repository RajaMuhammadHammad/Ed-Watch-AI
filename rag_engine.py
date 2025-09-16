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
FAISS_PATH = os.path.join(BASE_DIR, "faiss_index.faiss")

DOCS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/documents.pkl"
FAISS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/faiss_index.idx"

# -------------------------
# Helpers
# -------------------------
def download_if_missing(url: str, path: str) -> None:
    if not os.path.exists(path):
        print(f"Downloading {os.path.basename(path)} from {url} ...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)

# Ensure required files exist
download_if_missing(DOCS_URL, DOCS_PATH)
download_if_missing(FAISS_URL, FAISS_PATH)

# -------------------------
# Load documents
# -------------------------
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)

# -------------------------
# Embedding
# -------------------------
def embed_query(text: str) -> np.ndarray:
    """Embed a query using Gemini embeddings API."""
    res = genai.embed_content(model="models/embedding-001", content=text)
    return np.array(res["embedding"], dtype="float32")

# -------------------------
# Load or rebuild FAISS index
# -------------------------
def load_or_rebuild_faiss():
    """Load FAISS index, rebuild if dimension mismatch."""
    try:
        index = faiss.read_index(FAISS_PATH)
        print("FAISS index loaded.")
    except Exception as e:
        print("Failed to load FAISS index:", e)
        index = None

    # Check dimension
    if index is not None:
        sample_vec = embed_query("test").reshape(1, -1)
        if sample_vec.shape[1] != index.d:
            print("FAISS index dimension mismatch. Rebuilding index...")
            index = None

    # Rebuild if needed
    if index is None:
        embeddings = []
        for doc in documents:
            # Make sure each doc has 'embedding' precomputed or compute now
            if "embedding" in doc:
                embeddings.append(np.array(doc["embedding"], dtype="float32"))
            else:
                embeddings.append(embed_query(doc["text"]))  # fallback
        embeddings = np.stack(embeddings)
        d = embeddings.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(embeddings)
        faiss.write_index(index, FAISS_PATH)
        print(f"FAISS index rebuilt and saved. Dimension: {d}")

    return index

faiss_index = load_or_rebuild_faiss()

# -------------------------
# Retrieval
# -------------------------
def retrieve_context(query: str, k: int = 5):
    """Retrieve top-k most relevant documents for a query."""
    query_vec = embed_query(query).reshape(1, -1)

    # Safety check
    if query_vec.shape[1] != faiss_index.d:
        raise ValueError(
            f"Query vector dimension {query_vec.shape[1]} does not match FAISS index dimension {faiss_index.d}"
        )

    scores, indices = faiss_index.search(query_vec, k)
    return [documents[i] for i in indices[0] if i < len(documents)]
