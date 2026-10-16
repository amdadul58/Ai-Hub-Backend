from src.rag.pipeline import index_document

def index_file(path, **kwargs):
    return index_document(path, **kwargs)
