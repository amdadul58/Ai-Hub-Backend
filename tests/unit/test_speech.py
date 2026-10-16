import pytest

from src.speech.audio_chunking import chunk_sequence, chunk_text


def test_chunk_text_obeys_maximum_length():
    chunks = chunk_text("one two three four five six", max_chars=9)

    assert chunks
    assert all(len(chunk) <= 9 for chunk in chunks)
    assert " ".join(chunks) == "one two three four five six"


def test_chunk_text_splits_oversized_word():
    chunks = chunk_text("abcdefghij", max_chars=4)

    assert chunks == ["abcd", "efgh", "ij"]


@pytest.mark.parametrize("limit", [0, -1])
def test_chunk_text_rejects_invalid_limit(limit):
    with pytest.raises(ValueError):
        chunk_text("hello", max_chars=limit)


def test_chunk_sequence_preserves_items_and_order():
    items = list(range(7))
    chunks = chunk_sequence(items, 3)

    assert chunks == [[0, 1, 2], [3, 4, 5], [6]]
    assert [item for chunk in chunks for item in chunk] == items


def test_chunk_sequence_rejects_invalid_size():
    with pytest.raises(ValueError):
        chunk_sequence([1, 2], 0)