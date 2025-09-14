import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
import requests

# GitHub release file URLs
DOCS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/documents.pkl"
FAISS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/faiss_index.idx"

# Local cache paths
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

# Ensure files exist locally
download_file(DOCS_URL, DOCS_PATH)
download_file(FAISS_URL, FAISS_PATH)

# Load FAISS index
faiss_index = faiss.read_index(FAISS_PATH)

# Load documents
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)

# Load local embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight, free

def embed_query_local(query: str):
    """Compute embeddings locally using SentenceTransformer"""
    return model.encode([query], convert_to_numpy=True).astype("float32")

def retrieve_context(query, top_k=5):
    """Retrieve top-k relevant documents from FAISS using local embeddings"""
    query_embedding = embed_query_local(query)
    D, I = faiss_index.search(query_embedding, top_k)
    results = [documents[i] for i in I[0]]

    print(f"[RAG] Top-{top_k} results for query: {query}\n")
    for i, doc in enumerate(results, 1):
        content = doc.get("content", "") if isinstance(doc, dict) else str(doc)
        print(f"{i}. {content[:150]}...\n")
    return results
