from src.rag.vector_store import LocalVectorStore

def get_vector_store(path="data/rag_store.json"):
    return LocalVectorStore(path)
