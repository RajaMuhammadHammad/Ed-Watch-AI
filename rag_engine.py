import os
import pickle
import faiss
import numpy as np
import google.generativeai as genai

# -------------------------
# Paths
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_PATH = os.path.join(BASE_DIR, "documents.pkl")
FAISS_PATH = os.path.join(BASE_DIR, "faiss_index.faiss")

# -------------------------
# Load documents
# -------------------------
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)

# -------------------------
# Gemini API setup
# -------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # ✅ Use Render environment variable

def embed_query(query: str) -> np.ndarray:
    """Convert a query into an embedding using Gemini API."""
    result = genai.embed_content(
        model="models/embedding-001",
        content=query
    )
    return np.array(result["embedding"], dtype="float32")

# -------------------------
# FAISS Index
# -------------------------
def load_or_rebuild_faiss():
    """Load FAISS index if exists, otherwise rebuild from stored embeddings."""
    index = None

    if os.path.exists(FAISS_PATH):
        try:
            index = faiss.read_index(FAISS_PATH)
            print("✅ FAISS index loaded.")
        except Exception as e:
            print("⚠️ Failed to load FAISS index:", e)

    if index is None:
        print("🔄 Rebuilding FAISS index from stored embeddings...")
        embeddings = []
        for doc in documents:
            embeddings.append(np.array(doc["embedding"], dtype="float32"))
        embeddings = np.stack(embeddings)
        d = embeddings.shape[1]

        index = faiss.IndexFlatL2(d)
        index.add(embeddings)
        faiss.write_index(index, FAISS_PATH)
        print(f"✅ FAISS index rebuilt and saved. Dimension: {d}")

    return index

# Load FAISS index at startup
faiss_index = load_or_rebuild_faiss()

# -------------------------
# Retrieval Function
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
                "content": doc["content"],
                "score": float(score)
            })

    return results
