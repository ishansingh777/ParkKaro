"""
ParkKaro - Full YOLOv8n Parking & Traffic Sign Detector Training
Target: Train YOLOv8n on ALL 17,515 Indian traffic & parking sign images across all 85 classes
and automatically deploy best.pt weights to backend/models/sign_detector.pt
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
    print("=" * 65)
    print("🚗 ParkKaro - Full YOLOv8 Traffic & Parking Sign Training")
    print("=" * 65)

    # 1. Environment & Device Check
    cuda_available = torch.cuda.is_available()
    device = 0 if cuda_available else "cpu"
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {cuda_available}")
    if cuda_available:
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"Total VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    else:
        print("Note: Running on CPU. Training will utilize multi-core CPU threads.")

    # 2. Paths
    script_dir = Path(__file__).resolve().parent
    data_yaml = script_dir / "data.yaml"
    runs_dir = script_dir / "runs"
    project_root = script_dir.parent.parent
    target_model_path = project_root / "backend" / "models" / "sign_detector.pt"

    print(f"\nDataset Config: {data_yaml}")
    print(f"Runs Directory: {runs_dir}")
    print(f"Destination Model: {target_model_path}")

    # 3. Load Base Model (YOLOv8 Nano)
    base_model_path = script_dir / "yolov8n.pt"
    print(f"\nLoading base YOLOv8n weights from {base_model_path}...")
    model = YOLO(str(base_model_path))

    # Real-time sync callback: copies best.pt to backend/models as soon as each epoch finishes!
    def sync_weights(trainer):
        try:
            best_path = Path(trainer.save_dir) / "weights" / "best.pt"
            if best_path.exists():
                target_model_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(best_path, target_model_path)
                print(f"\n🔄 [Auto-Sync] Updated {target_model_path} with latest best.pt from Epoch {trainer.epoch + 1}")
        except Exception as e:
            pass

    model.add_callback("on_fit_epoch_end", sync_weights)

    # 4. Train Model across ALL images (100% of the dataset, NO fraction filter!)
    batch_size = 16 if cuda_available else 8
    epochs = 15
    imgsz = 416
    workers = 4 if cuda_available else 2

    print(f"\nStarting full training: epochs={epochs}, batch={batch_size}, imgsz={imgsz}, device={device}...")
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        device=device,
        project=str(runs_dir),
        name="parkkaro_sign_detector_full",
        exist_ok=True,
        workers=workers,
        save=True,
        plots=True,
        amp=cuda_available,
        patience=10
    )

    print("\n" + "=" * 65)
    print(" Full Training Complete!")
    print("=" * 65)

    # 5. Final Copy Verification
    best_weights = runs_dir / "parkkaro_sign_detector_full" / "weights" / "best.pt"
    if not best_weights.exists():
        candidate = list(runs_dir.glob("**/best.pt"))
        if candidate:
            best_weights = candidate[0]

    if best_weights.exists():
        print(f"Found best weights at: {best_weights}")
        target_model_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weights, target_model_path)
        print(f" Successfully deployed best weights to: {target_model_path}")
        print(f"File size: {target_model_path.stat().st_size / (1024*1024):.2f} MB")
    else:
        print(f"⚠️ Could not find best.pt in {runs_dir}")

if __name__ == "__main__":
    main()
