import os
from pathlib import Path
import numpy as np
import cv2

# Ensure Ultralytics config is stored within the workspace directory
config_dir = Path(__file__).resolve().parent / ".yolo_config"
config_dir.mkdir(parents=True, exist_ok=True)
os.environ["YOLO_CONFIG_DIR"] = str(config_dir)

from ultralytics import YOLO

# 1. Load the model from backend/models/sign_detector.pt
model_path = Path("backend/models/sign_detector.pt")
print(f"Loading model: {model_path} ({model_path.stat().st_size / (1024*1024):.2f} MB)")
model = YOLO(str(model_path))

# 2. Select test images from test/images (including NO_PARKING and other signs)
test_dir = Path("ml/sign_scanner/ParkKaro.v1i.yolov8/test/images")
test_samples = [
    test_dir / "43000_jpg.rf.30f8d3e95c3ba4fc620e750b32a23306.jpg", # NO_PARKING
    test_dir / "43003_2_jpg.rf.6091723f7725bccecc7262962eb1f46d.jpg", # NO_PARKING
    test_dir / "43004_jpg.rf.0131ec9a7d6fb373a2277a6419ca4d74.jpg", # NO_PARKING
    test_dir / "00001_jpg.rf.e408c4b98ceb672584c2df9fa4738057.jpg", # ALL_MOTOR_VEHICLES_PROHIBITED
    test_dir / "00009_jpg.rf.6e7b0f774ad6ebc8f394067fe128b01b.jpg", # PROHIBITED
]

# Ensure images exist
valid_samples = [str(p) for p in test_samples if p.exists()]
if not valid_samples:
    valid_samples = [str(p) for p in list(test_dir.glob("*.jpg"))[:5]]

print(f"\n--- 1. Quick Inference & Box Check (conf=0.25) on {len(valid_samples)} Test Images ---")
results = model.predict(
    source=valid_samples,
    conf=0.25,
    save=True,
    project="ml/sign_scanner/runs",
    name="verify_test",
    exist_ok=True
)

detections = 0
for r in results:
    img_name = Path(r.path).name
    print(f"\nImage: {img_name}")
    if len(r.boxes) == 0:
        print("  (No detections at conf=0.25)")
    for box in r.boxes:
        detections += 1
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = float(box.conf[0])
        xyxy = [round(x, 1) for x in box.xyxy[0].tolist()]
        print(f"  Class: {label} | Confidence: {conf:.2f} | Box: {xyxy}")

print(f"\nTotal detections across images: {detections}")

# 3. Test Lower Confidence (conf=0.15) if needed
print(f"\n--- 2. Sensitivity Check with conf=0.15 ---")
results_low = model.predict(
    source=valid_samples,
    conf=0.15,
    save=False,
    verbose=False
)
low_detections = sum(len(r.boxes) for r in results_low)
print(f"Total detections at conf=0.15: {low_detections}")

# 4. Test Edge Case: Blank / Non-Sign Image
print(f"\n--- 3. Edge Case: Blank Image (No Signs) Test ---")
blank_img_path = Path("ml/sign_scanner/runs/blank_test.jpg")
blank_canvas = np.zeros((416, 416, 3), dtype=np.uint8) + 128 # neutral grey wall
cv2.imwrite(str(blank_img_path), blank_canvas)

blank_results = model.predict(
    source=str(blank_img_path),
    conf=0.25,
    save=False,
    verbose=False
)
blank_boxes = len(blank_results[0].boxes)
print(f"Blank image false positives: {blank_boxes} boxes (Expected: 0)")
if blank_boxes == 0:
    print("✅ Passed: No false positives on non-sign background!")

print("\n" + "=" * 60)
print("Verification complete! Check images at: ml/sign_scanner/runs/verify_test/")
print("=" * 60)
