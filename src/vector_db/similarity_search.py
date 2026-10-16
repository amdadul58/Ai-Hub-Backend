from src.rag.retrieval import retrieve
from src.vector_db.metadata_filters import filter_metadata

def similarity_search(query, top_k=5, filters=None, store=None):
    results = retrieve(query, top_k=top_k, store=store)
    return filter_metadata(results, filters)
