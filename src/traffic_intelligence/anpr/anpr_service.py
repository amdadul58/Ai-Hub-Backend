
from pathlib import Path
import logging
import unicodedata

import cv2
import numpy as np
from ultralytics import YOLO

from src.traffic_intelligence.anpr.saudi_plate_mapping import latin_to_arabic


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "ai_models" / "anpr"


class ANPRService:
    """Unified Saudi and Bangladesh number-plate recognition service."""

    def __init__(self):
        self.saudi_detector = None
        self.saudi_ocr = None
        self.bangladesh_reader = None

    def _load_saudi_models(self):
        if self.saudi_detector is None:
            detector_path = MODEL_DIR / "saudi_plate_detector.pt"
            ocr_path = MODEL_DIR / "saudi_plate_ocr.pt"

            if not detector_path.is_file() or not ocr_path.is_file():
                raise FileNotFoundError(
                    "Saudi ANPR model files are missing."
                )

            self.saudi_detector = YOLO(str(detector_path))
            self.saudi_ocr = YOLO(str(ocr_path))

    def _load_bangladesh_reader(self):
        if self.bangladesh_reader is None:
            import easyocr

            self.bangladesh_reader = easyocr.Reader(
                ["bn", "en"],
                gpu=False,
            )

    @staticmethod
    def _validate_image(image):
        if image is None or not hasattr(image, "shape"):
            raise ValueError("A valid OpenCV image is required.")

        if len(image.shape) < 2 or image.size == 0:
            raise ValueError("The supplied image is empty or invalid.")

    @staticmethod
    def _crop_image(image, bbox):
        if len(bbox) != 4:
            raise ValueError("bbox must contain x1, y1, x2, y2.")

        x1, y1, x2, y2 = map(int, bbox)
        height, width = image.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width, x2)
        y2 = min(height, y2)

        if x2 <= x1 or y2 <= y1:
            raise ValueError("Invalid plate bounding box.")

        crop = image[y1:y2, x1:x2]

        if crop.size == 0:
            raise ValueError("Plate crop is empty.")

        return crop

    @staticmethod
    def _prepare_ocr_image(image):
        height, width = image.shape[:2]

        if width < 600:
            scale = 600 / width
            image = cv2.resize(
                image,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC,
            )

        return image

    def _recognize_saudi(self, image):
        self._load_saudi_models()

        detection = self.saudi_detector.predict(
            image,
            conf=0.25,
            imgsz=640,
            device="cpu",
            verbose=False,
        )[0]

        if detection.boxes is None or len(detection.boxes) == 0:
            return {
                "country": "saudi",
                "plate_detected": False,
                "plate_text": None,
                "arabic_text": None,
                "confidence": None,
                "message": "No Saudi-style plate detected.",
            }

        best_box = max(
            detection.boxes,
            key=lambda box: float(box.conf[0]),
        )

        bbox = [
            int(value)
            for value in best_box.xyxy[0].tolist()
        ]

        crop = self._crop_image(image, bbox)

        reading = self.saudi_ocr.predict(
            crop,
            conf=0.10,
            imgsz=640,
            device="cpu",
            verbose=False,
        )[0]

        characters = []

        if reading.boxes is not None:
            for box in reading.boxes:
                class_id = int(box.cls[0])
                char = reading.names[class_id]

                char_x = float(
                    box.xyxy[0][0] + box.xyxy[0][2]
                ) / 2

                characters.append({
                    "char": str(char),
                    "confidence": float(box.conf[0]),
                    "x": char_x,
                })

        characters.sort(key=lambda item: item["x"])

        plate_text = "".join(
            item["char"] for item in characters
        )

        arabic_text = None
        mapping_error = None

        if plate_text:
            try:
                arabic_text = latin_to_arabic(plate_text)
            except ValueError as exc:
                mapping_error = str(exc)

        return {
            "country": "saudi",
            "plate_detected": True,
            "plate_text": plate_text or None,
            "arabic_text": arabic_text,
            "confidence": round(float(best_box.conf[0]), 3),
            "character_count": len(characters),
            "characters": [
                {
                    "char": item["char"],
                    "confidence": round(item["confidence"], 3),
                }
                for item in characters
            ],
            "bbox": bbox,
            "mapping_error": mapping_error,
            "recognition_status": (
                "recognized" if plate_text else "plate_detected_ocr_empty"
            ),
            "message": (
                "Recognition result; verify against the original plate."
            ),
        }

    def _recognize_bangladesh(self, image, plate_bbox=None):
        self._load_bangladesh_reader()

        target = image
        detected_bbox = None

        # Use a manually supplied plate crop when available.
        if plate_bbox is not None:
            detected_bbox = list(map(int, plate_bbox))
            target = self._crop_image(image, detected_bbox)


        target = self._prepare_ocr_image(target)

        # Resize large images to reduce CPU processing time.
        original_height, original_width = target.shape[:2]
        max_dimension = 2000

        scale_x = 1.0
        scale_y = 1.0

        if max(original_width, original_height) > max_dimension:
            scale = max_dimension / max(original_width, original_height)

            new_width = max(1, int(original_width * scale))
            new_height = max(1, int(original_height * scale))

            ocr_target = cv2.resize(
                target,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA,
            )

            scale_x = original_width / new_width
            scale_y = original_height / new_height
        else:
            ocr_target = target

        # Bangladesh OCR: Bengali and English.
        results = self.bangladesh_reader.readtext(
            ocr_target,
            detail=1,
            paragraph=False,
        )

        candidates = []

        for result in results:
            bbox, text, confidence = result

            # Convert OCR coordinates back to original image size.
            original_bbox = np.asarray(
                bbox, dtype=np.float32
            ).copy()

            original_bbox[:, 0] *= scale_x
            original_bbox[:, 1] *= scale_y

            candidates.append({
                "text": str(text).strip(),
                "confidence": round(float(confidence), 3),
                "bbox": original_bbox.tolist(),
            })

        def is_bengali_char(ch):
            return unicodedata.name(ch, "").startswith("BENGALI")

        bengali_text = [
            item for item in candidates
            if any(
                is_bengali_char(ch) and ch.isalpha()
                for ch in item["text"]
            )
        ]

        number_candidates = []

        for item in candidates:
            digits = "".join(
                ch for ch in item["text"]
                if ch.isdecimal()
            )

            if 5 <= len(digits) <= 8:
                number_candidates.append({
                    "text": digits,
                    "confidence": item["confidence"],
                })

        number_candidates.sort(
            key=lambda item: item["confidence"],
            reverse=True,
        )

        area_text = [
            item["text"]
            for item in bengali_text
        ]

        best_number = (
            number_candidates[0]
            if number_candidates
            else None
        )

        plate_candidate = None

        if best_number:
            plate_candidate = " ".join(
                area_text[:2] + [best_number["text"]]
            )
        elif area_text:
            plate_candidate = " ".join(area_text[:2])

        return {
            "country": "bangladesh",
            "plate_detected": None,
            "plate_text": None,
            "plate_text_candidate": plate_candidate,
            "recognition_status": (
                "unverified" if plate_candidate else "no_candidate"
            ),
            "number_candidates": number_candidates,
            "recognized_text": candidates,
            "bengali_text": bengali_text,
            "plate_bbox": detected_bbox,
            "message": (
                "OCR-based candidate only. Verify against the original "
                "plate. A dedicated Bangladesh plate detector is not "
                "installed."
            ),
        }

    def analyze(self, image, country="auto", plate_bbox=None):
        self._validate_image(image)

        country = (country or "auto").strip().lower()

        if country not in {"auto", "saudi", "bangladesh"}:
            raise ValueError(
                "country must be auto, saudi, or bangladesh."
            )

        if country == "saudi":
            return self._recognize_saudi(image)

        if country == "bangladesh":
            return self._recognize_bangladesh(
                image,
                plate_bbox,
            )

        # Auto mode: try Saudi detector first.
        saudi_result = self._recognize_saudi(image)

        if saudi_result["plate_detected"]:
            saudi_result["country_detection"] = "provisional"
            return saudi_result

        # Fallback: Bangladesh OCR.
        bangladesh_result = self._recognize_bangladesh(
            image,
            plate_bbox,
        )

        if bangladesh_result["bengali_text"]:
            bangladesh_result["country_detection"] = "provisional"
            return bangladesh_result

        return {
            "country": "unknown",
            "plate_detected": False,
            "country_detection": "inconclusive",
            "bangladesh_ocr_candidates": (
                bangladesh_result["recognized_text"]
            ),
            "message": (
                "Could not reliably identify the plate country."
            ),
        }


anpr_service = ANPRService()
