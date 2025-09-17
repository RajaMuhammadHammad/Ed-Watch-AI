import os
import pickle
import requests
import faiss
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
DOCS_PATH = os.path.join(BASE_DIR, "documents.pkl")
FAISS_IDX_PATH = os.path.join(BASE_DIR, "faiss_index.idx")
FAISS_FAISS_PATH = os.path.join(BASE_DIR, "faiss_index.faiss")

# GitHub Releases URLs
DOCS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/documents.pkl"
IDX_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/faiss_index.idx"

def download_file(url, local_path):
    if not os.path.exists(local_path):
        print(f"⬇️ Downloading {os.path.basename(local_path)} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
        print(f"✅ Downloaded {os.path.basename(local_path)}")

# Download files if missing
download_file(DOCS_URL, DOCS_PATH)
download_file(IDX_URL, FAISS_IDX_PATH)

# Convert .idx → .faiss if missing
if not os.path.exists(FAISS_FAISS_PATH):
    print(f"🔄 Converting {os.path.basename(FAISS_IDX_PATH)} → {os.path.basename(FAISS_FAISS_PATH)} ...")
    index = faiss.read_index(FAISS_IDX_PATH)
    faiss.write_index(index, FAISS_FAISS_PATH)
    print(f"✅ Converted and saved as {os.path.basename(FAISS_FAISS_PATH)}")

# Load documents
def load_documents():
    with open(DOCS_PATH, "rb") as f:
        docs = pickle.load(f)
    print(f"📂 Loaded {len(docs)} documents")
    return docs

# Load FAISS index
def load_faiss_index():
    index = faiss.read_index(FAISS_FAISS_PATH)
    print(f"📦 FAISS index dimension: {index.d}")
    return index

# Simple random projection for query embedding (matches FAISS dimension 384)
def embed_query(query, dim=384):
    # Use deterministic hashing for lightweight embedding
    vec = np.zeros(dim, dtype='float32')
    for i, c in enumerate(query):
        vec[i % dim] += ord(c) % 256
    vec /= np.linalg.norm(vec) + 1e-10
    return vec.reshape(1, -1).astype('float32')

# Retrieve top-k documents
def retrieve_context(query, top_k=5):
    docs = load_documents()
    index = load_faiss_index()
    query_vec = embed_query(query, dim=index.d)
    distances, indices = index.search(query_vec, top_k)
    retrieved = [docs[i] for i in indices[0]]
    return retrieved
