import pytest

from src.traffic_intelligence.traffic_pipeline import analyze_frame
from src.traffic_intelligence.vehicle_counting import count_detections
from src.traffic_intelligence.video_validation import (
    validate_video_path,
)


def test_count_detections_counts_all_records():
    detections = [
        {"class_name": "car"},
        {"class_name": "bus"},
        {"class_name": "car"},
    ]

    assert count_detections(detections) == {
        "count": 3,
        "class_name": None,
    }


def test_count_detections_filters_by_class():
    detections = [
        {"class_name": "car"},
        {"class_name": "bus"},
        {"class_name": "car"},
    ]

    assert count_detections(detections, "car") == {
        "count": 2,
        "class_name": "car",
    }


def test_count_detections_accepts_empty_input():
    assert count_detections([])["count"] == 0


def test_analyze_frame_returns_detector_results():
    frame = object()
    detections = [{"type": "car"}, {"type": "bus"}]

    result = analyze_frame(
        frame,
        detector=lambda received_frame: (
            detections if received_frame is frame else []
        ),
    )

    assert result["detections"] == detections
    assert result["vehicle_count"] == 2
    assert "density" not in result


def test_analyze_frame_includes_density_when_configured():
    detections = [{"type": "car"}]

    result = analyze_frame(
        "frame",
        detector=lambda frame: detections,
        density_estimator=lambda found, frame: "medium",
    )

    assert result["vehicle_count"] == 1
    assert result["density"] == "medium"


def test_analyze_frame_rejects_non_callable_detector():
    with pytest.raises(TypeError, match="detector must be callable"):
        analyze_frame("frame", detector=None)


def test_validate_video_path_returns_file_metadata(tmp_path):
    video = tmp_path / "sample.MP4"
    video.write_bytes(b"test-video")

    result = validate_video_path(video)

    assert result["path"] == str(video.resolve())
    assert result["size_bytes"] == len(b"test-video")
    assert result["extension"] == ".mp4"


def test_validate_video_path_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_video_path(tmp_path / "missing.mp4")


def test_validate_video_path_rejects_unsupported_extension(tmp_path):
    video = tmp_path / "notes.txt"
    video.write_text("not a video", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported video extension"):
        validate_video_path(video)


def test_validate_video_path_accepts_custom_extensions(tmp_path):
    video = tmp_path / "sample.custom"
    video.write_bytes(b"video")

    result = validate_video_path(
        video,
        allowed_extensions={".custom"},
    )

    assert result["extension"] == ".custom"