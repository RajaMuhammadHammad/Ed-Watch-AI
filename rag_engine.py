import faiss
import numpy as np
import requests
import os
import pickle
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# GitHub release file URLs
DOCS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/documents.pkl"
FAISS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/faiss_index.idx"

# Local paths
DOCS_PATH = "documents.pkl"
FAISS_PATH = "faiss_index.idx"

def download_file(url, filepath):
    if not os.path.exists(filepath):
        print(f"[Download] Fetching {url}...")
        r = requests.get(url)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(r.content)
        print(f"[Download] Saved to {filepath}")

# Ensure files exist
download_file(DOCS_URL, DOCS_PATH)
download_file(FAISS_URL, FAISS_PATH)

# Load FAISS index
faiss_index = faiss.read_index(FAISS_PATH)

# Load documents
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)

# Use Gemini for query embeddings
def embed_query_gemini(query: str):
    resp = genai.embed_content(
        model="models/embedding-001",
        content=query
    )
    return np.array([resp['embedding']], dtype="float32")

# Retrieve context
def retrieve_context(query, top_k=5):
    query_embedding = embed_query_gemini(query)
    D, I = faiss_index.search(query_embedding, top_k)
    results = [documents[i] for i in I[0]]

    print(f"[RAG] Top-{top_k} results for query: {query}\n")
    for i, doc in enumerate(results, 1):
        content = doc.get("content", "") if isinstance(doc, dict) else str(doc)
        print(f"{i}. {content[:150]}...\n")

    return results
