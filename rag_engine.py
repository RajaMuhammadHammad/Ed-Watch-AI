import faiss
import pickle
import numpy as np
import requests
import os
from sentence_transformers import SentenceTransformer


# GitHub release file URLs
DOCS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/documents.pkl"
FAISS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/faiss_index.idx"

# Local cache paths (Render ephemeral filesystem, re-downloaded each time container restarts)
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

# Load documents (list of dicts)
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)

# Load same embedding model used during index creation
model = SentenceTransformer("all-MiniLM-L6-v2")  # or your actual model


def retrieve_context(query, top_k=5):
    query_embedding = model.encode([query])

    # Search the FAISS index
    D, I = faiss_index.search(np.array(query_embedding), top_k)

    # Retrieve documents based on index positions
    results = [documents[i] for i in I[0]]

    print(f"[RAG] Top-{top_k} results for query: {query}\n")
    for i, doc in enumerate(results, 1):
        if isinstance(doc, dict):
            content = doc.get("content", "")
        elif isinstance(doc, str):
            content = doc
            doc = {"content": content}
            results[i - 1] = doc
        else:
            content = str(doc)

        print(f"{i}. {content[:150]}...\n")

    return results
