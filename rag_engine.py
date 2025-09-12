
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer


faiss_index = faiss.read_index("data/faiss_index.idx")  


# Load documents (list of dicts)
with open("data/documents.pkl", "rb") as f:
    documents = pickle.load(f)

# Load same embedding model used during index creation
model = SentenceTransformer("all-MiniLM-L6-v2")  # or whatever model was used

def retrieve_context(query, top_k=5):
    query_embedding = model.encode([query])

    # Search the FAISS index
    D, I = faiss_index.search(np.array(query_embedding), top_k)

    # Retrieve documents based on index positions
    results = [documents[i] for i in I[0]]

    print(f"[RAG] Top-{top_k} results for query: {query}\n")
    for i, doc in enumerate(results, 1):
        # Safely handle both dict and string types
        if isinstance(doc, dict):
            content = doc.get("content", "")
        elif isinstance(doc, str):
            content = doc
            # Optionally wrap in a dict if needed
            doc = {"content": content}
            results[i - 1] = doc
        else:
            content = str(doc)

        print(f"{i}. {content[:150]}...\n")

    return results
