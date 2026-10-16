from src.rag.vector_store import LocalVectorStore

def retrieve(query, top_k=5, store=None):
    if not query or not query.strip():
        return []
    return (store or LocalVectorStore()).search(query, top_k=top_k)
