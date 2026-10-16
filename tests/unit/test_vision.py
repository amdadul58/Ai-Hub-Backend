import pytest

from src.vision.image_loader import image_metadata, load_image


def test_load_image_and_metadata(tmp_path):
    Image = pytest.importorskip("PIL.Image")

    path = tmp_path / "sample.png"
    Image.new("RGB", (16, 12), color=(20, 40, 60)).save(path)

    loaded = load_image(path)

    assert loaded.size == (16, 12)
    assert loaded.mode == "RGB"

    metadata = image_metadata(path)
    assert metadata["format"] == "PNG"
    assert metadata["width"] == 16
    assert metadata["height"] == 12


def test_load_image_converts_mode(tmp_path):
    Image = pytest.importorskip("PIL.Image")

    path = tmp_path / "grayscale.png"
    Image.new("L", (8, 8), color=128).save(path)

    assert load_image(path, mode="RGB").mode == "RGB"


def test_load_image_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_image(tmp_path / "missing.png")