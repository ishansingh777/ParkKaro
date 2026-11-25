"""
ParkKaro - Step 3: 3-Stage Parking Inference Engine
===================================================
Author: Senior Computer Vision & ML Engineer
Architecture:
  Stage 1: High-Resolution YOLOv8 Object Detection (@960px)
  Stage 2: Dynamic Sub-Plate Bounding Box Expansion (+35% height, +15% width) + OCR
  Stage 3: Deterministic Rule Engine (evaluate_parking) combining sign class,
           OCR sub-plate text, query time (HH:MM), and vehicle type (car/bike/commercial).
"""

import os
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np

# Ensure Ultralytics config is local
config_dir = Path(__file__).resolve().parent / ".yolo_config"
config_dir.mkdir(parents=True, exist_ok=True)
os.environ["YOLO_CONFIG_DIR"] = str(config_dir)

from ultralytics import YOLO

# 6 Consolidated Classes
CLASS_NAMES = [
    "no_parking",          # 0
    "no_stopping",         # 1
    "parking_allowed",     # 2
    "auto_stand",          # 3
    "tow_away_zone",       # 4
    "other_traffic_sign"   # 5
]

# Color map for bounding boxes & banners
CLASS_COLORS = {
    0: (0, 0, 220),       # Red: no_parking
    1: (0, 0, 150),       # Dark Red: no_stopping
    2: (0, 200, 0),       # Green: parking_allowed
    3: (0, 165, 255),     # Orange: auto_stand
    4: (180, 0, 180),     # Purple: tow_away_zone
    5: (220, 180, 0)      # Cyan/Yellow: other_traffic_sign
}


# ==============================================================================
# STAGE 2: SUB-PLATE CROPPING & OCR ENGINE
# ==============================================================================

def get_subplate_crop(image: np.ndarray, bbox: tuple):
    """
    Crops the primary sign plus a downward margin to capture Indian sub-plates (पूरक तख्ती).
    Margin: +35% downward height, +15% horizontal width expansion.
    """
    img_h, img_w = image.shape[:2]
    x1, y1, x2, y2 = bbox

    bw = x2 - x1
    bh = y2 - y1

    # Downward expansion for sub-plate below the circular board
    y2_sub = min(img_h, int(y2 + bh * 0.35))
    x1_sub = max(0, int(x1 - bw * 0.15))
    x2_sub = min(img_w, int(x2 + bw * 0.15))

    crop = image[y1:y2_sub, x1_sub:x2_sub]
    return crop, (x1_sub, y1, x2_sub, y2_sub)


# Global cache for OCR reader to avoid re-initializing on each image
_OCR_READER = None
_OCR_TYPE = None


def init_ocr():
    global _OCR_READER, _OCR_TYPE
    if _OCR_READER is not None:
        return _OCR_READER, _OCR_TYPE

    # Try PaddleOCR first
    try:
        from paddleocr import PaddleOCR
        _OCR_READER = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        _OCR_TYPE = "paddle"
        return _OCR_READER, _OCR_TYPE
    except Exception:
        pass

    # Try EasyOCR second
    try:
        import easyocr
        _OCR_READER = easyocr.Reader(["en"], gpu=False)
        _OCR_TYPE = "easyocr"
        return _OCR_READER, _OCR_TYPE
    except Exception:
        pass

    _OCR_TYPE = "fallback"
    return None, _OCR_TYPE


def run_ocr_on_crop(crop_img: np.ndarray) -> str:
    """
    Runs text recognition on the sub-plate crop.
    Falls back gracefully if PaddleOCR/EasyOCR are not installed.
    """
    if crop_img is None or crop_img.size == 0:
        return ""

    reader, ocr_type = init_ocr()

    try:
        if ocr_type == "paddle":
            res = reader.ocr(crop_img, cls=True)
            text_lines = []
            if res and res[0]:
                for line in res[0]:
                    text_lines.append(line[1][0])
            return " ".join(text_lines).strip().upper()

        elif ocr_type == "easyocr":
            results = reader.readtext(crop_img)
            text_lines = [r[1] for r in results]
            return " ".join(text_lines).strip().upper()

    except Exception as e:
        pass

    # Fallback: image preprocessing & color check
    return ""


# ==============================================================================
# STAGE 3: DETERMINISTIC PARKING RULE ENGINE
# ==============================================================================

def parse_time_window(text: str):
    """
    Extracts time windows from Indian sub-plates (e.g. '8:00 AM TO 8:00 PM', '10AM-6PM', '08:00 - 20:00').
    Returns (start_minutes, end_minutes) or None.
    """
    text_clean = text.upper().replace(".", ":").replace("  ", " ")

    # Regex for "8 AM TO 8 PM" or "8:00 AM - 8:00 PM"
    pattern = r"(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?\s*(?:TO|-)\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?"
    match = re.search(pattern, text_clean)

    if match:
        h1, m1, p1, h2, m2, p2 = match.groups()
        h1 = int(h1)
        m1 = int(m1) if m1 else 0
        h2 = int(h2)
        m2 = int(m2) if m2 else 0

        # Handle 12-hour AM/PM normalization
        if p1 == "PM" and h1 < 12:
            h1 += 12
        elif p1 == "AM" and h1 == 12:
            h1 = 0

        if p2 == "PM" and h2 < 12:
            h2 += 12
        elif p2 == "AM" and h2 == 12:
            h2 = 0

        # Default assumption: If no AM/PM provided and h1 < 12, h2 < 12, assume typical daytime window (e.g. 8 to 8 = 8 AM to 8 PM)
        if not p1 and not p2:
            if h1 <= 12 and h2 <= 12 and h2 <= h1:
                h2 += 12

        start_min = h1 * 60 + m1
        end_min = h2 * 60 + m2
        return (start_min, end_min)

    # Check for 24 Hours
    if "24" in text and ("HR" in text or "HOUR" in text):
        return (0, 1440)

    return None


def evaluate_parking(
    sign_class: int,
    sign_name: str,
    ocr_text: str = "",
    query_time: str = None,           # "HH:MM", defaults to current local time
    vehicle_type: str = "car",        # "car", "two_wheeler", "commercial"
    query_day: str = None             # "Monday", "Sunday", etc.
) -> dict:
    """
    Deterministic rule engine that combines YOLO sign class, OCR sub-plate text,
    query time (HH:MM), and vehicle type to compute exact parking legality.
    """
    now = datetime.now()
    if query_time is None:
        query_time = now.strftime("%H:%M")
    if query_day is None:
        query_day = now.strftime("%A")

    try:
        qh, qm = map(int, query_time.split(":"))
        query_min = qh * 60 + qm
    except ValueError:
        query_min = now.hour * 60 + now.minute
        query_time = f"{now.hour:02d}:{now.minute:02d}"

    vtype = vehicle_type.lower().strip()
    ocr_upper = ocr_text.upper()
    restrictions = []

    # 1. Parse Sub-Plate Restrictions
    time_window = parse_time_window(ocr_upper)
    is_inside_time_window = None

    if time_window:
        start_m, end_m = time_window
        sh, sm = divmod(start_m, 60)
        eh, em = divmod(end_m, 60)
        time_str = f"{sh:02d}:{sm:02d} to {eh:02d}:{em:02d}"
        restrictions.append(f"TIME_WINDOW({time_str})")

        if start_m <= end_m:
            is_inside_time_window = (start_m <= query_min <= end_m)
        else:
            # Crosses midnight
            is_inside_time_window = (query_min >= start_m or query_min <= end_m)

    # Vehicle-specific sub-plate restrictions
    has_two_wheeler_only = any(k in ocr_upper for k in ["TWO WHEELER", "2 WHEELER", "SCOOTER", "BIKE"])
    has_car_only = any(k in ocr_upper for k in ["CAR ONLY", "FOUR WHEELER", "4 WHEELER"])
    has_commercial_ban = any(k in ocr_upper for k in ["NO TRUCK", "NO COMMERCIAL", "BUS ONLY"])
    has_tow_away = any(k in ocr_upper for k in ["TOW AWAY", "TOWING", "CRANE"])

    if has_tow_away:
        restrictions.append("TOW_AWAY_ZONE")
    if "SUNDAY" in ocr_upper and ("EXCEPT" in ocr_upper or "FREE" in ocr_upper):
        restrictions.append("EXCEPT_SUNDAY")

    # 2. Decision Logic by Sign Class

    # CLASS 0: NO_PARKING
    if sign_class == 0:
        # If time window is specified and current time is OUTSIDE window
        if time_window is not None and not is_inside_time_window:
            return {
                "can_park": True,
                "status_label": "ALLOWED",
                "reason": f"No-Parking restriction applies only between {time_str}. Free to park right now at {query_time}.",
                "detected_restrictions": restrictions
            }

        # If vehicle is exempted
        if has_two_wheeler_only and vtype == "two_wheeler":
            return {
                "can_park": True,
                "status_label": "ALLOWED",
                "reason": "Sub-plate exempts two-wheelers (scooters/bikes permitted).",
                "detected_restrictions": restrictions
            }

        # If Sunday is exempted
        if "EXCEPT_SUNDAY" in restrictions and query_day.lower() == "sunday":
            return {
                "can_park": True,
                "status_label": "ALLOWED",
                "reason": f"No-Parking restriction is not enforced on Sundays ({query_day}).",
                "detected_restrictions": restrictions
            }

        # Standard No Parking rule applies
        reason = f"No Parking zone active at {query_time}."
        if time_window:
            reason += f" Restricted hours are {time_str}."
        if has_tow_away or sign_class == 4:
            reason += " Active crane/tow-away enforcement!"

        return {
            "can_park": False,
            "status_label": "PROHIBITED",
            "reason": reason,
            "detected_restrictions": restrictions
        }

    # CLASS 1: NO_STOPPING (Strict Halt Ban)
    elif sign_class == 1:
        if time_window is not None and not is_inside_time_window:
            return {
                "can_park": True,
                "status_label": "CONDITIONAL",
                "reason": f"No-Stopping restriction relaxed outside {time_str}. Proceed with caution.",
                "detected_restrictions": restrictions
            }
        return {
            "can_park": False,
            "status_label": "PROHIBITED",
            "reason": f"Strict No-Stopping & No-Standing zone active at {query_time}! Halting even for drop-off will get your vehicle towed.",
            "detected_restrictions": restrictions + ["ZERO_HALTING"]
        }

    # CLASS 2: PARKING_ALLOWED
    elif sign_class == 2:
        if has_two_wheeler_only and vtype != "two_wheeler":
            return {
                "can_park": False,
                "status_label": "PROHIBITED",
                "reason": f"Designated Two-Wheeler parking only. Parking for {vtype} is prohibited.",
                "detected_restrictions": restrictions + ["TWO_WHEELER_ONLY"]
            }
        if has_car_only and vtype == "two_wheeler":
            return {
                "can_park": False,
                "status_label": "PROHIBITED",
                "reason": "Designated Car-only parking lot. Two-wheelers prohibited in this bay.",
                "detected_restrictions": restrictions + ["CAR_ONLY"]
            }
        if has_commercial_ban and vtype == "commercial":
            return {
                "can_park": False,
                "status_label": "PROHIBITED",
                "reason": "Commercial vehicles and trucks prohibited in this public parking space.",
                "detected_restrictions": restrictions + ["NO_COMMERCIAL"]
            }

        return {
            "can_park": True,
            "status_label": "ALLOWED",
            "reason": f"Authorized parking zone. Legal to park your {vtype} at {query_time}.",
            "detected_restrictions": restrictions
        }

    # CLASS 3: AUTO_STAND
    elif sign_class == 3:
        if vtype == "commercial":
            return {
                "can_park": True,
                "status_label": "ALLOWED",
                "reason": "Designated public auto-rickshaw/taxi stand. Commercial auto permitted.",
                "detected_restrictions": restrictions + ["AUTO_RICKSHAW_STAND"]
            }
        return {
            "can_park": False,
            "status_label": "PROHIBITED",
            "reason": f"Designated Auto/Taxi stand. Private {vtype} parking is illegal and will be challenged.",
            "detected_restrictions": restrictions + ["AUTO_RICKSHAW_STAND"]
        }

    # CLASS 4: TOW_AWAY_ZONE
    elif sign_class == 4:
        return {
            "can_park": False,
            "status_label": "TOW_AWAY",
            "reason": f"Designated Tow-Away Zone. Traffic police crane actively towing unattended vehicles.",
            "detected_restrictions": restrictions + ["TOW_AWAY_ACTIVE"]
        }

    # CLASS 5: OTHER_TRAFFIC_SIGN
    else:
        return {
            "can_park": True,
            "status_label": "ALLOWED",
            "reason": f"Regulatory/warning road sign ({sign_name}). Not an active parking prohibition.",
            "detected_restrictions": restrictions
        }


# ==============================================================================
# INFERENCE PIPELINE
# ==============================================================================

def run_pipeline(
    image_path: str,
    weights_path: str,
    conf_thresh: float = 0.25,
    iou_thresh: float = 0.45,
    imgsz: int = 960,
    query_time: str = None,
    vehicle_type: str = "car",
    output_path: str = None
):
    print("=" * 75)
    print("🚗 PARKKARO 3-STAGE INFERENCE PIPELINE")
    print("=" * 75)
    print(f"Target Image   : {image_path}")
    print(f"YOLO Weights   : {weights_path}")
    print(f"Resolution     : {imgsz}px (conf={conf_thresh}, iou={iou_thresh})")
    print(f"Vehicle Type   : {vehicle_type}")
    print(f"Query Time     : {query_time or datetime.now().strftime('%H:%M')}")

    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {image_path}")

    # Stage 1: YOLO Detection
    model = YOLO(weights_path)
    results = model.predict(
        source=img,
        conf=conf_thresh,
        iou=iou_thresh,
        imgsz=imgsz,
        verbose=False
    )[0]

    detections = []
    annotated = img.copy()

    overall_can_park = True
    primary_verdict = "ALLOWED"
    primary_reason = "No parking restriction detected in this frame."

    boxes = results.boxes
    print(f"\nStage 1: Detected {len(boxes)} road signs in image.")

    for idx, box in enumerate(boxes):
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        xyxy = box.xyxy[0].cpu().numpy().astype(int)
        x1, y1, x2, y2 = xyxy

        cls_name = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else f"class_{cls_id}"

        # Stage 2: Sub-Plate Crop & OCR
        crop, sub_coords = get_subplate_crop(img, (x1, y1, x2, y2))
        ocr_text = run_ocr_on_crop(crop)

        # Stage 3: Deterministic Rule Engine
        verdict = evaluate_parking(
            sign_class=cls_id,
            sign_name=cls_name,
            ocr_text=ocr_text,
            query_time=query_time,
            vehicle_type=vehicle_type
        )

        detections.append({
            "detection_id": idx + 1,
            "class_id": cls_id,
            "class_name": cls_name,
            "confidence": round(conf, 4),
            "bbox": [int(x1), int(y1), int(x2), int(y2)],
            "subplate_ocr": ocr_text if ocr_text else "(No sub-plate text detected)",
            "parking_verdict": verdict
        })

        print(f"\n  Sign #{idx + 1}: [{cls_name.upper()}] (Conf: {conf:.2f})")
        print(f"    • Sub-plate text : {ocr_text if ocr_text else '<none>'}")
        print(f"    • Can Park?      : {'YES' if verdict['can_park'] else 'NO'} [{verdict['status_label']}]")
        print(f"    • Reason         : {verdict['reason']}")

        # Overall logic: Any prohibitive sign forces overall false
        if not verdict["can_park"]:
            overall_can_park = False
            primary_verdict = verdict["status_label"]
            primary_reason = verdict["reason"]

        # Draw on annotated image
        color = CLASS_COLORS.get(cls_id, (255, 255, 255))
        # Primary sign box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)

        # Sub-plate expanded box in dashed/thinner outline
        sx1, sy1, sx2, sy2 = sub_coords
        cv2.rectangle(annotated, (sx1, sy1), (sx2, sy2), (255, 255, 0), 1)

        # Label pill
        label_text = f"{cls_name} {conf:.2f}"
        if ocr_text:
            label_text += f" | {ocr_text[:15]}"
        cv2.putText(annotated, label_text, (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

    # Top Status Banner on Image
    banner_color = (0, 160, 0) if overall_can_park else (0, 0, 200)
    if primary_verdict == "TOW_AWAY":
        banner_color = (180, 0, 180)
    elif primary_verdict == "CONDITIONAL":
        banner_color = (0, 165, 255)

    cv2.rectangle(annotated, (0, 0), (annotated.shape[1], 50), banner_color, -1)
    banner_txt = f"VERDICT: {primary_verdict} ({'PARKING ALLOWED' if overall_can_park else 'PARKING PROHIBITED'})"
    cv2.putText(annotated, banner_txt, (15, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

    # Save output if path given
    if output_path is None:
        p = Path(image_path)
        output_path = str(p.parent / f"{p.stem}_parking_verdict.jpg")

    cv2.imwrite(output_path, annotated)
    print(f"\n🖼️ Annotated prediction image saved: {output_path}")

    return {
        "overall_can_park": overall_can_park,
        "primary_verdict": primary_verdict,
        "primary_reason": primary_reason,
        "detections": detections,
        "output_image": output_path
    }


def main():
    parser = argparse.ArgumentParser(description="ParkKaro 3-Stage Parking Inference Engine")
    parser.add_argument("--image", type=str, required=True, help="Path to input street/parking photo")
    parser.add_argument("--weights", type=str,
                        default="C:/STUDY/Project/ParkKaro/backend/models/sign_detector.pt",
                        help="Path to trained sign detector weights")
    parser.add_argument("--conf", type=float, default=0.25, help="Detection confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
    parser.add_argument("--imgsz", type=int, default=960, help="Inference resolution")
    parser.add_argument("--time", type=str, default=None, help="Query time in HH:MM format (default: current time)")
    parser.add_argument("--vehicle", type=str, default="car", choices=["car", "two_wheeler", "commercial"],
                        help="Vehicle type: car, two_wheeler, commercial")
    parser.add_argument("--output", type=str, default=None, help="Path to save annotated output image")

    args = parser.parse_args()

    run_pipeline(
        image_path=args.image,
        weights_path=args.weights,
        conf_thresh=args.conf,
        iou_thresh=args.iou,
        imgsz=args.imgsz,
        query_time=args.time,
        vehicle_type=args.vehicle,
        output_path=args.output
    )


if __name__ == "__main__":
    main()
