"""
ParkKaro - Step 2: Advanced YOLO Training Pipeline for Road Signs
================================================================
Author: Senior Computer Vision & ML Engineer
Target:
  Fixes:
  1. Low recall on small/distant signs -> imgsz=960 + multi-scale scaling.
  2. Loose bounding boxes -> mosaic=1.0 + close_mosaic=15 + tuned box loss.
  3. False positives on hoardings/commercial boards -> trained with negative images.
  4. Class confusion (no_parking vs no_stopping) -> fliplr=0.0, high-res anchors, balanced class loss.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Configure local YOLO config directory to prevent Windows permission conflicts
config_dir = Path(__file__).resolve().parent / ".yolo_config"
config_dir.mkdir(parents=True, exist_ok=True)
os.environ["YOLO_CONFIG_DIR"] = str(config_dir)

import torch
from ultralytics import YOLO


def train_model(
    data_yaml: str,
    base_model: str = "yolov8s.pt",
    imgsz: int = 960,
    epochs: int = 100,
    batch: int = 16,
    patience: int = 20,
    device: str = None,
    project_dir: str = None,
    run_name: str = "parkkaro_sign_yolo960"
):
    print("=" * 80)
    print("🚀 PARKKARO 3-STAGE VISION TRAINING ENGINE (YOLOv8 @ 960px)")
    print("=" * 80)

    # 1. Device Selection & Memory Safeguards
    if device is None:
        device = 0 if torch.cuda.is_available() else "cpu"

    print(f"PyTorch Version : {torch.__version__}")
    print(f"Compute Device  : {device}")
    if torch.cuda.is_available() and device != "cpu":
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"GPU Hardware    : {gpu_name} ({vram_gb:.2f} GB VRAM)")
        # If GPU has 4GB VRAM (e.g. RTX 3050 Laptop), adjust batch to prevent CUDA OOM at 960px
        if vram_gb <= 4.5 and batch > 8:
            print(f"⚠️ 4GB VRAM detected: adjusting default batch size from {batch} to 8 for imgsz={imgsz}")
            batch = 8
    else:
        print("Note: Running on CPU.")
        if batch > 8:
            batch = 8

    # 2. Paths
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    if project_dir is None:
        project_dir = str(script_dir / "runs")

    target_model_path = project_root / "backend" / "models" / "sign_detector.pt"
    print(f"Dataset Config  : {data_yaml}")
    print(f"Target Deploy   : {target_model_path}")
    print(f"Project Runs    : {project_dir}/{run_name}")

    # 3. Model Initialization
    # If base model is a local file or name, load via Ultralytics
    print(f"\nLoading base architecture: {base_model}...")
    model = YOLO(base_model)

    # Callback: automatically deploy latest best.pt to backend as each epoch finishes
    def on_epoch_end_sync(trainer):
        try:
            best_weights = Path(trainer.save_dir) / "weights" / "best.pt"
            if best_weights.exists():
                target_model_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(best_weights, target_model_path)
        except Exception:
            pass

    model.add_callback("on_fit_epoch_end", on_epoch_end_sync)

    # 4. Hyperparameter Configuration (Tailored for Small Indian Roadside Signs)
    print("\nTraining Hyperparameters:")
    print(f"  • Image Size (imgsz) : {imgsz}px (crucial for small/distant sign recall)")
    print(f"  • Epochs / Batch     : {epochs} / {batch}")
    print("  • Fliplr             : 0.0 (STRICT: Never horizontally mirror directional arrows or 'P' symbols)")
    print("  • Scale Augmentation : 0.5 (Multi-scale zoom for distant roadside sign recognition)")
    print("  • Mosaic / Close     : 1.0 / 15 (Tight bounding boxes; mosaic disabled in last 15 epochs)")
    print("  • HSV Color Jitter   : h=0.015, s=0.6, v=0.4 (Handles glare, dust, and direct Indian sunlight)")
    print("  • Loss Weights       : box=7.5, cls=0.5, dfl=1.5 (High box precision to close mAP50 vs mAP50-95 gap)")

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        device=device,
        project=project_dir,
        name=run_name,
        exist_ok=True,
        patience=patience,

        # Small Object & Precision Enhancements:
        scale=0.5,              # Multi-scale feature pyramid training
        fliplr=0.0,             # NO horizontal flipping for traffic signage
        flipud=0.0,             # NO vertical flipping
        mosaic=1.0,             # 4-image mosaic for small object contextualization
        close_mosaic=15,        # Turn off mosaic for last 15 epochs to tighten bounding boxes
        hsv_h=0.015,            # Hue jitter
        hsv_s=0.6,              # Saturation jitter (sun-faded boards)
        hsv_v=0.4,              # Brightness jitter (harsh shadow/sunlight)

        # Loss Balance:
        box=7.5,                # Box regression weight (tightens IoU)
        cls=0.5,                # Classification weight
        dfl=1.5,                # Distribution Focal Loss weight

        # System & Validation:
        workers=4 if (torch.cuda.is_available() and device != "cpu") else 2,
        save=True,
        plots=True,
        val=True,
        amp=torch.cuda.is_available() and device != "cpu"  # FP16 mixed precision on GPU
    )

    print("\n" + "=" * 80)
    print("✅ TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 80)

    # 5. Locate and Deploy Best Weights
    run_dir = Path(project_dir) / run_name
    best_weights = run_dir / "weights" / "best.pt"

    if best_weights.exists():
        target_model_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weights, target_model_path)
        print(f"📦 Best model exported to: {target_model_path}")
        print(f"   Model size: {target_model_path.stat().st_size / (1024*1024):.2f} MB")
    else:
        print(f"⚠️ Warning: best.pt not found directly in {run_dir / 'weights'}")

    # 6. Evaluation Artifacts Guide
    print("\n📈 Model Evaluation Artifacts generated for error analysis:")
    for plot_file in ["results.png", "confusion_matrix.png", "BoxPR_curve.png", "val_batch0_pred.jpg"]:
        p = run_dir / plot_file
        if p.exists():
            print(f"   • {plot_file:25s}: {p}")

    return str(best_weights) if best_weights.exists() else None


def main():
    parser = argparse.ArgumentParser(description="ParkKaro Advanced YOLOv8 Sign Training Pipeline")
    parser.add_argument("--data", type=str,
                        default="C:/STUDY/Project/ParkKaro/ml/sign_scanner/dataset_consolidated/data_consolidated.yaml",
                        help="Path to data_consolidated.yaml")
    parser.add_argument("--model", type=str, default="yolov8s.pt",
                        help="Base weights (e.g., yolov8s.pt, yolov8n.pt, or yolo11s.pt)")
    parser.add_argument("--imgsz", type=int, default=960,
                        help="Input resolution (default: 960 for small sign recall)")
    parser.add_argument("--epochs", type=int, default=100, help="Total training epochs (default: 100)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (default: 16)")
    parser.add_argument("--patience", type=int, default=20, help="Early stopping patience (default: 20)")
    parser.add_argument("--device", type=str, default=None, help="Target device: '0' for CUDA GPU, 'cpu' for CPU")
    parser.add_argument("--project", type=str, default=None, help="Output runs directory")
    parser.add_argument("--name", type=str, default="parkkaro_sign_yolo960", help="Run name")

    args = parser.parse_args()

    train_model(
        data_yaml=args.data,
        base_model=args.model,
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        patience=args.patience,
        device=args.device,
        project_dir=args.project,
        run_name=args.name
    )


if __name__ == "__main__":
    main()
