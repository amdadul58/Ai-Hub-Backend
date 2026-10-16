import pytest

from src.translation.text_chunking import chunk_text
from src.translation.language_detection import detect_language_script


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello world", "en"),
        ("আমি বাংলা লিখি", "bn"),
        ("مرحبا بالعالم", "ar"),
        ("Привет мир", "ru"),
    ],
)
def test_script_language_detection(text, expected):
    result = detect_language_script(text)

    assert result["language"] == expected
    assert result["confidence"] > 0
    assert result["method"] == "script_heuristic"


@pytest.mark.parametrize("text", ["", "   ", "12345", None])
def test_script_detection_unknown_input(text):
    result = detect_language_script(text)

    assert result["language"] == "unknown"
    assert result["confidence"] == 0.0


def test_translation_chunking_respects_limit():
    text = "This is a sentence that needs to be split into smaller chunks."
    chunks = chunk_text(text, max_chars=15)

    assert chunks
    assert all(len(chunk) <= 15 for chunk in chunks)
    assert " ".join(chunks) == text


def test_translation_chunking_handles_long_word():
    chunks = chunk_text("abcdefghijklmnop", max_chars=5)

    assert chunks == ["abcde", "fghij", "klmno", "p"]


@pytest.mark.parametrize("limit", [0, -1])
def test_translation_chunking_rejects_invalid_limit(limit):
    with pytest.raises(ValueError):
        chunk_text("hello", max_chars=limit)