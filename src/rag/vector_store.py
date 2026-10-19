import json
import os
import tempfile
from pathlib import Path

from src.rag.embeddings import embed_text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STORE = PROJECT_ROOT / "data" / "rag_store.json"


def _cosine(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


class LocalVectorStore:
    def __init__(self, path=DEFAULT_STORE):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self):
        if not self.path.exists():
            return []

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

        if not isinstance(data, list):
            return []

        return [
            record for record in data
            if isinstance(record, dict)
            and isinstance(record.get("text"), str)
        ]

    def _write(self, records):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=self.path.parent,
                suffix=".tmp",
                delete=False,
            ) as temp_file:
                json.dump(records, temp_file, ensure_ascii=False, indent=2)
                temp_file.write("\n")
                temp_path = Path(temp_file.name)

            os.replace(temp_path, self.path)
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()

    def add_documents(self, documents):
        records = self._read()
        added = 0

        for doc in documents:
            if not isinstance(doc, dict):
                continue

            text = str(doc.get("text", "")).strip()
            if not text:
                continue

            metadata = doc.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}

            source = str(metadata.get("source", ""))
            chunk = metadata.get("chunk")

            # Replace the same source/chunk instead of accumulating duplicates.
            if source and chunk is not None:
                records = [
                    record for record in records
                    if not (
                        isinstance(record.get("metadata"), dict)
                        and str(record["metadata"].get("source", "")) == source
                        and record["metadata"].get("chunk") == chunk
                    )
                ]

            records.append({
                "text": text,
                "metadata": metadata,
                "embedding": embed_text(text),
            })
            added += 1

        self._write(records)
        return len(records)

    def search(self, query, top_k=5):
        query = str(query or "").strip()

        if not query or top_k < 1:
            return []

        query_vector = embed_text(query)
        results = []

        for record in self._read():
            embedding = record.get("embedding", [])
            if not isinstance(embedding, list):
                continue

            score = _cosine(query_vector, embedding)
            results.append({
                "text": record.get("text", ""),
                "metadata": record.get("metadata", {}),
                "score": round(score, 4),
            })

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]

    def clear(self):
        self._write([])
