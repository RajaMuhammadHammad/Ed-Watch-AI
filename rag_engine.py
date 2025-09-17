import os
import pickle
import faiss
import numpy as np
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Gemini 2.0 API Configuration
# -----------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# Paths
# -----------------------------
DOCS_PATH = "documents.pkl"
IDX_PATH = "faiss_index.idx"
FAISS_PATH = "faiss_index.faiss"

# -----------------------------
# Lazy-loaded variables
# -----------------------------
documents = None
index = None
tfidf_vectorizer = None
tfidf_matrix = None

# -----------------------------
# Load Documents lazily
# -----------------------------
def load_documents():
    global documents
    if documents is None:
        if not os.path.exists(DOCS_PATH):
            raise FileNotFoundError(f"{DOCS_PATH} not found.")
        with open(DOCS_PATH, "rb") as f:
            documents = pickle.load(f)
        print(f"📂 Loaded {len(documents)} documents")
    return documents

# -----------------------------
# Load or convert FAISS index lazily
# -----------------------------
def load_index():
    global index
    if index is None:
        if os.path.exists(FAISS_PATH):
            index = faiss.read_index(FAISS_PATH)
            print(f"📦 Loaded FAISS index from {FAISS_PATH}")
        else:
            if not os.path.exists(IDX_PATH):
                raise FileNotFoundError(f"Neither {FAISS_PATH} nor {IDX_PATH} found.")
            idx_data = np.load(IDX_PATH)
            index = faiss.IndexFlatL2(idx_data.shape[1])
            index.add(idx_data.astype(np.float32))
            faiss.write_index(index, FAISS_PATH)
            print("🔄 Converted .idx → .faiss and saved")
        print(f"📦 FAISS index dimension: {index.d}")
    return index

# -----------------------------
# Generate Embedding using Gemini
# -----------------------------
def get_embedding(text):
    """
    Generate embeddings using Gemini 2.0.
    """
    model_id = "embed_text_2.0"
    try:
        response = genai.get_embeddings(model=model_id, text=text)
        return np.array(response["embedding"], dtype=np.float32)
    except Exception as e:
        print("⚠️ Gemini embedding failed:", e)
        return None  # fallback handled in retrieve_context

# -----------------------------
# Fallback TF-IDF initialization
# -----------------------------
def init_tfidf():
    global tfidf_vectorizer, tfidf_matrix
    if tfidf_vectorizer is None or tfidf_matrix is None:
        docs = load_documents()
        tfidf_vectorizer = TfidfVectorizer(max_features=5000)
        tfidf_matrix = tfidf_vectorizer.fit_transform([d.get("content", "") for d in docs])
        print("📝 TF-IDF fallback initialized")

# -----------------------------
# Retrieve Relevant Context
# -----------------------------
def retrieve_context(query, top_k=5):
    """
    Retrieve top_k documents relevant to the query using FAISS or TF-IDF fallback.
    """
    docs = load_documents()
    idx = load_index()

    query_vec = get_embedding(query)

    # ✅ If Gemini embedding works, use FAISS
    if query_vec is not None:
        D, I = idx.search(np.array([query_vec]), top_k)
        results = [docs[i] for i in I[0] if i < len(docs)]
        return results

    # ⚠️ Fallback TF-IDF retrieval
    print("⚠️ Using TF-IDF fallback for retrieval")
    init_tfidf()
    query_vec_tfidf = tfidf_vectorizer.transform([query])
    similarities = cosine_similarity(query_vec_tfidf, tfidf_matrix)
    top_indices = similarities[0].argsort()[::-1][:top_k]
    results = [docs[i] for i in top_indices]
    return results
