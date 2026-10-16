class CentroidTracker:
    """Basic frame-to-frame centroid matcher; not a production multi-object tracker."""
    def __init__(self, max_distance=50.0):
        if max_distance <= 0:
            raise ValueError("max_distance must be positive.")
        self.max_distance = float(max_distance)
        self._next_id = 1
        self._tracks = {}

    def update(self, detections):
        current = {}
        unmatched = set(self._tracks)
        output = []
        for detection in detections:
            x1, y1, x2, y2 = detection["bbox"]
            center = ((x1 + x2) / 2, (y1 + y2) / 2)
            best_id, best_distance = None, self.max_distance
            for track_id in unmatched:
                old_x, old_y = self._tracks[track_id]
                distance = ((center[0] - old_x) ** 2 + (center[1] - old_y) ** 2) ** 0.5
                if distance < best_distance:
                    best_id, best_distance = track_id, distance
            if best_id is None:
                best_id = self._next_id
                self._next_id += 1
            else:
                unmatched.remove(best_id)
            current[best_id] = center
            output.append({**detection, "track_id": best_id})
        self._tracks = current
        return output
