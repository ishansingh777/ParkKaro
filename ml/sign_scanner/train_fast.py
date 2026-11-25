"""
ParkKaro - Fast YOLOv8n Fine-Tuning for Sign Scanner
Produces verified best.pt weights and copies to backend/models/sign_detector.pt
"""

import os
from pathlib import Path

# Ensure Ultralytics config is stored within the workspace directory
config_dir = Path(__file__).resolve().parent / ".yolo_config"
config_dir.mkdir(parents=True, exist_ok=True)
os.environ["YOLO_CONFIG_DIR"] = str(config_dir)

import shutil
import torch
from ultralytics import YOLO

def main():
    print("=" * 60)
    print("🚗 ParkKaro - Fine-tuning YOLOv8n Sign Detector")
    print("=" * 60)

    script_dir = Path(__file__).resolve().parent
    data_yaml = script_dir / "data.yaml"
    runs_dir = script_dir / "runs"
    project_root = script_dir.parent.parent
    target_model_path = project_root / "backend" / "models" / "sign_detector.pt"

    base_model_path = script_dir / "yolov8n.pt"
    print(f"Base model: {base_model_path}")
    model = YOLO(str(base_model_path))

    # Fast fine-tuning on diverse subset of 1,200 images to prevent CPU RAM overflow
    print("\nStarting fast training (3 epochs, imgsz=416, fraction=0.08)...")
    results = model.train(
        data=str(data_yaml),
        epochs=3,
        imgsz=416,
        batch=8,
        fraction=0.08,
        device="cpu",
        workers=0,
        project=str(runs_dir),
        name="parkkaro_sign_detector",
        exist_ok=True,
        save=True,
        plots=True
    )

    print("\n" + "=" * 60)
    print(" Training Finished! Exporting best.pt...")
    print("=" * 60)

    best_weights = runs_dir / "parkkaro_sign_detector" / "weights" / "best.pt"
    if not best_weights.exists():
        candidate = list(runs_dir.glob("**/best.pt"))
        if candidate:
            best_weights = candidate[0]

    if best_weights.exists():
        target_model_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weights, target_model_path)
        print(f" Successfully exported to: {target_model_path}")
        print(f"File size: {target_model_path.stat().st_size / (1024*1024):.2f} MB")
    else:
        print(f"⚠️ Could not find best.pt in {runs_dir}")

if __name__ == "__main__":
    main()
