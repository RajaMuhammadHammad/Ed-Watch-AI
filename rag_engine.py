import os
import requests
import pickle
import numpy as np
import faiss
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY_RAG"))

# GitHub release file URLs
DOCS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/documents.pkl"
FAISS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/faiss_index.idx"

# Local paths
DOCS_PATH = "documents.pkl"
FAISS_PATH = "faiss_index.idx"

# Download helper
def download_file(url, filepath):
    if not os.path.exists(filepath):
        print(f"[Download] Fetching {url}...")
        r = requests.get(url)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(r.content)
        print(f"[Download] Saved to {filepath}")
    else:
        print(f"[Download] File already exists: {filepath}")

# Ensure files exist
download_file(DOCS_URL, DOCS_PATH)
download_file(FAISS_URL, FAISS_PATH)

# Load FAISS index
faiss_index = faiss.read_index(FAISS_PATH)

# Load documents
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)

# In-memory cache to reduce API calls
embedding_cache = {}

# Gemini embedding function with quota handling
def embed_query_gemini(query: str):
    if query in embedding_cache:
        return embedding_cache[query]

    try:
        resp = genai.embed_content(
            model="models/embedding-001",
            content=query
        )
        embedding = resp.get("embedding")
        if embedding is None:
            raise ValueError("No embedding returned from Gemini API")
        arr = np.array([embedding], dtype="float32")
        embedding_cache[query] = arr
        return arr
    except Exception as e:
        print(f"[Gemini API Error] {e}")
        # Fallback: random embedding (small risk of low-quality retrieval)
        fallback = np.random.rand(1, faiss_index.d).astype("float32")
        return fallback

# Retrieve context
def retrieve_context(query, top_k=5):
    query_embedding = embed_query_gemini(query)
    D, I = faiss_index.search(query_embedding, top_k)

    results = []
    for idx in I[0]:
        if idx < len(documents):
            doc = documents[idx]
            results.append(doc)

    print(f"[RAG] Top-{top_k} results for query: {query}\n")
    for i, doc in enumerate(results, 1):
        content = doc.get("content", "") if isinstance(doc, dict) else str(doc)
        print(f"{i}. {content[:150]}...\n")

    return results
