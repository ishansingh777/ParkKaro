import os
from pathlib import Path

# Set config dir to avoid AppData permissions
config_dir = Path(__file__).resolve().parent / ".yolo_config"
config_dir.mkdir(parents=True, exist_ok=True)
os.environ["YOLO_CONFIG_DIR"] = str(config_dir)

from ultralytics import YOLO

# Load trained model
model_path = Path(__file__).resolve().parent.parent.parent / "backend" / "models" / "sign_detector.pt"
if not model_path.exists() or model_path.stat().st_size < 1000:
    # Fallback to runs best.pt if not yet copied
    runs_best = Path(__file__).resolve().parent / "runs" / "parkkaro_sign_detector" / "weights" / "best.pt"
    if runs_best.exists():
        model_path = runs_best

print(f"Testing model: {model_path}")
model = YOLO(str(model_path))

# Run prediction on test images
test_dir = Path(__file__).resolve().parent / "ParkKaro.v1i.yolov8" / "test" / "images"
test_images = list(test_dir.glob("*.jpg"))[:15]  # Test on sample of 15 images for quick verification

print(f"Running inference on {len(test_images)} test images (conf=0.25)...")
results = model.predict(
    source=[str(img) for img in test_images],
    conf=0.25,
    save=True,
    project=str(Path(__file__).resolve().parent / "runs"),
    name="verify_test",
    exist_ok=True
)

detections = 0
for r in results:
    for box in r.boxes:
        detections += 1
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = float(box.conf[0])
        xyxy = [round(x, 1) for x in box.xyxy[0].tolist()]
        print(f"Class: {label} | Confidence: {conf:.2f} | Box: {xyxy}")

print("\n" + "=" * 50)
print("Total detections across images:", detections)
print(f"Output images saved to: ml/sign_scanner/runs/verify_test/")
print("=" * 50)
