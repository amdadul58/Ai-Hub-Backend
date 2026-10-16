import json
from pathlib import Path
from src.rag.embeddings import embed_text

DEFAULT_STORE = Path("data/rag_store.json")

def _cosine(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))

class LocalVectorStore:
    def __init__(self, path=DEFAULT_STORE):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self):
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def add_documents(self, documents):
        records = self._read()
        for doc in documents:
            text = str(doc.get("text", "")).strip()
            if not text:
                continue
            records.append({
                "text": text,
                "metadata": doc.get("metadata", {}),
                "embedding": embed_text(text),
            })
        self.path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return len(records)

    def search(self, query, top_k=5):
        if top_k < 1:
            return []
        query_vector = embed_text(query)
        results = []
        for record in self._read():
            score = _cosine(query_vector, record.get("embedding", []))
            results.append({
                "text": record.get("text", ""),
                "metadata": record.get("metadata", {}),
                "score": round(score, 4),
            })
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

    def clear(self):
        self.path.write_text("[]", encoding="utf-8")
