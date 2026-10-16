import json

import pytest

from src.rag.chunking import split_text
from src.rag.vector_store import LocalVectorStore


def test_split_text_normalizes_whitespace():
    assert split_text("  hello   world \n again ", chunk_size=30, overlap=2) == [
        "hello world again"
    ]


def test_split_text_respects_chunk_size_and_overlap():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = split_text(text, chunk_size=10, overlap=2)

    assert "".join([chunks[0], chunks[1][2:], chunks[2][2:]]) == text
    assert all(len(chunk) <= 10 for chunk in chunks)


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [(0, 0), (5, -1), (5, 5), (5, 6)],
)
def test_split_text_rejects_invalid_parameters(chunk_size, overlap):
    with pytest.raises(ValueError):
        split_text("some text", chunk_size=chunk_size, overlap=overlap)


def test_vector_store_add_search_and_clear(tmp_path):
    store = LocalVectorStore(tmp_path / "vectors.json")

    count = store.add_documents([
        {"text": "Bengali language document", "metadata": {"source": "test"}},
        {"text": "   "},
        {"text": "English language document", "metadata": {"source": "demo"}},
    ])

    assert count == 2
    results = store.search("Bengali language", top_k=2)

    assert len(results) == 2
    assert all("text" in item and "score" in item for item in results)
    assert results[0]["metadata"]["source"] == "test"

    store.clear()
    assert store.search("Bengali language") == []
    assert json.loads((tmp_path / "vectors.json").read_text(encoding="utf-8")) == []


def test_vector_store_handles_invalid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{invalid json", encoding="utf-8")

    store = LocalVectorStore(path)

    assert store.search("query") == []