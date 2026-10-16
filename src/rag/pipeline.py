from pathlib import Path
from src.rag.chunking import split_text
from src.rag.text_extractor import extract_text
from src.rag.vector_store import LocalVectorStore

def index_document(path, chunk_size=500, overlap=80, store=None):
    path = Path(path)
    text = extract_text(path)
    chunks = split_text(text, chunk_size=chunk_size, overlap=overlap)
    vector_store = store or LocalVectorStore()
    documents = [
        {"text": chunk, "metadata": {"source": str(path), "chunk": i}}
        for i, chunk in enumerate(chunks)
    ]
    vector_store.add_documents(documents)
    return {"source": str(path), "chunks_indexed": len(chunks)}

def search_documents(query, top_k=5, store=None):
    if not query or not query.strip():
        return []
    return (store or LocalVectorStore()).search(query, top_k=top_k)
