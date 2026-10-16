from src.rag.pipeline import index_document

class IndexManager:
    def __init__(self, store=None):
        self.store = store

    def index(self, path, **kwargs):
        return index_document(path, store=self.store, **kwargs)
