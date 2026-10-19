from pathlib import Path

from src.rag.chunking import split_text
from src.rag.text_extractor import extract_text
from src.rag.vector_store import LocalVectorStore


def index_document(path, chunk_size=500, overlap=80, store=None):
    path = Path(path).resolve()

    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")

    text = extract_text(path)
    if not text or not text.strip():
        raise ValueError("The document contains no extractable text.")

    chunks = split_text(text, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        raise ValueError("No text chunks were generated.")

    vector_store = store if store is not None else LocalVectorStore()

    documents = [
        {
            "text": chunk,
            "metadata": {
                "source": str(path),
                "chunk": index,
            },
        }
        for index, chunk in enumerate(chunks)
    ]

    count = vector_store.add_documents(documents)

    return {
        "source": str(path),
        "chunks_indexed": len(chunks),
        "total_chunks_in_store": count,
    }


def search_documents(query, top_k=5, store=None):
    if not query or not query.strip():
        return []

    vector_store = store if store is not None else LocalVectorStore()
    return vector_store.search(query, top_k=top_k)
