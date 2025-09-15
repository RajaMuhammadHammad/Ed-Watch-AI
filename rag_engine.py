import os
import pickle
import requests
import faiss
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_PATH = os.path.join(BASE_DIR, "documents.pkl")
FAISS_PATH = os.path.join(BASE_DIR, "faiss_index.faiss")

DOCS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/documents.pkl"
FAISS_URL = "https://github.com/RajaMuhammadHammad/Ed-Watch-AI/releases/download/v1.0.0/faiss_index.idx"

# 1. Auto-download files if missing
def download_if_missing(url, path):
    if not os.path.exists(path):
        print(f"Downloading {path} from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)

download_if_missing(DOCS_URL, DOCS_PATH)
download_if_missing(FAISS_URL, FAISS_PATH)

# 2. Load documents + FAISS index
with open(DOCS_PATH, "rb") as f:
    documents = pickle.load(f)

faiss_index = faiss.read_index(FAISS_PATH)

# 3. Retrieve function (only embed query!)
from google.generativeai import embedding

def embed_query(text):
    res = embedding.embed_content(model="models/embedding-001", content=text)
    return np.array(res["embedding"], dtype="float32")

def retrieve_context(query, k=5):
    query_vec = embed_query(query).reshape(1, -1)
    scores, indices = faiss_index.search(query_vec, k)
    return [documents[i] for i in indices[0] if i < len(documents)]
