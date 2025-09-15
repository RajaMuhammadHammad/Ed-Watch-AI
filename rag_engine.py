# rag_engine.py
import os
import pickle
import numpy as np

# Use faiss-cpu on most hosts; on Linux with GPU you could use faiss-gpu
import faiss

# Sentence Transformers for local embeddings
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_PATH = os.path.join(BASE_DIR, "documents.pkl")
FAISS_PATH = os.path.join(BASE_DIR, "faiss_index.faiss")

# If you have small/medium dataset, 'all-MiniLM-L6-v2' is fast and accurate.
EMBED_MODEL_NAME = os.environ.get("SENTENCE_EMBED_MODEL", "all-MiniLM-L6-v2")

# Load local sentence-transformers model (downloads once, caches in ~/.cache)
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

def load_documents():
    if not os.path.exists(DOCS_PATH):
        raise FileNotFoundError(f"documents.pkl not found at {DOCS_PATH}")
    with open(DOCS_PATH, "rb") as f:
        docs = pickle.load(f)
    return docs

def build_faiss_index(documents, index_path=FAISS_PATH):
    """
    Build FAISS index from documents. Expects `documents` list of dicts or strings.
    Each document should have a text field or be a string.
    """
    # Convert documents to simple text list
    texts = []
    for d in documents:
        if isinstance(d, dict):
            # adjust according to your stored structure (e.g., {'text': '...'})
            texts.append(d.get("text") or d.get("content") or str(d))
        else:
            texts.append(str(d))

    # Compute embeddings in batches
    batch_size = 64
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        emb = embed_model.encode(batch_texts, show_progress_bar=False, convert_to_numpy=True)
        embeddings.append(emb.astype("float32"))
    embeddings = np.vstack(embeddings)

    # Normalize for cosine search (optional but recommended)
    faiss.normalize_L2(embeddings)

    # Create index: IndexFlatIP for cosine (dot product on normalized vectors)
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)

    # Save index
    faiss.write_index(index, index_path)
    return index

# Load documents and index (build if missing)
documents = load_documents()

if os.path.exists(FAISS_PATH):
    try:
        faiss_index = faiss.read_index(FAISS_PATH)
    except Exception as e:
        print("Failed to read FAISS index, rebuilding:", e)
        faiss_index = build_faiss_index(documents)
else:
    print("FAISS index not found — building new index (this may take a moment)...")
    faiss_index = build_faiss_index(documents)

def embed_query_local(text):
    vec = embed_model.encode([text], convert_to_numpy=True)[0].astype("float32")
    faiss.normalize_L2(vec.reshape(1, -1))
    return vec

def retrieve_context(query, k=5):
    """
    Returns list of top-k documents (as stored in `documents`).
    """
    query_vec = embed_query_local(query).reshape(1, -1)
    scores, indices = faiss_index.search(query_vec, k)
    results = []
    for idx in indices[0]:
        if idx < 0 or idx >= len(documents):
            continue
        results.append(documents[idx])
    return results
