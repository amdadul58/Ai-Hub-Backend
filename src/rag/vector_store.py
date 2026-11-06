import json
import os
import re
import tempfile
from pathlib import Path

from src.rag.embeddings import embed_text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STORE = PROJECT_ROOT / "data" / "rag_store.json"

_STOP_WORDS = {
    "কি", "কী", "কেন", "কবে", "কোথায়", "কোথায়", "কে", "কোন",
    "কত", "হয়", "হয়", "হলো", "এর", "ও", "এবং", "একটি",
}


def _tokens(text):
    return {
        token
        for token in re.findall(r"\w+", str(text or "").casefold())
        if token not in _STOP_WORDS and len(token) > 1
    }


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
        query_tokens = _tokens(query)
        results = []

        for record in self._read():
            embedding = record.get("embedding", [])
            if not isinstance(embedding, list):
                continue

            text = record.get("text", "")
            score = _cosine(query_vector, embedding)

            if score < 0.08:
                continue

            document_tokens = _tokens(text)
            overlap = len(query_tokens & document_tokens)
            coverage = overlap / len(query_tokens) if query_tokens else 0.0

            # Combine existing embedding similarity with exact word overlap.
            rank_score = score + (0.30 * coverage)

            results.append({
                "text": text,
                "metadata": record.get("metadata", {}),
                "score": round(score, 4),
                "_rank_score": rank_score,
            })

        results.sort(
            key=lambda item: (item["_rank_score"], item["score"]),
            reverse=True,
        )

        for item in results:
            item.pop("_rank_score", None)

        return results[:top_k]

    def clear(self):
        self._write([])
