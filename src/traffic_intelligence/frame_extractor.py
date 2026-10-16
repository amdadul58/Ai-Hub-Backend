def extract_frames(video_path, every_n_frames=30, max_frames=100):
    if every_n_frames < 1 or max_frames < 1:
        raise ValueError("Frame interval and maximum must be positive.")
    from src.traffic_intelligence.video_input import open_video
    capture = open_video(video_path)
    frames = []
    frame_index = 0
    try:
        while len(frames) < max_frames:
            ok, frame = capture.read()
            if not ok:
                break
            if frame_index % every_n_frames == 0:
                frames.append({"frame_index": frame_index, "frame": frame})
            frame_index += 1
    finally:
        capture.release()
    return frames
