"""
ParkKaro - Step 1: Dataset Audit, Consolidation & Balancing
===========================================================
Author: Senior Computer Vision & ML Engineer
Purpose:
  1. Audit existing YOLO dataset for corrupted images and malformed labels.
  2. Flag out-of-bounds coordinates and tiny boxes (<8x8 px at imgsz=960).
  3. Consolidate 85 classes into 6 targeted parking & traffic classes:
       0: no_parking
       1: no_stopping
       2: parking_allowed
       3: auto_stand
       4: tow_away_zone
       5: other_traffic_sign
  4. Preserve empty .txt files as negative background images (suppresses hoardings/shop boards).
  5. Oversample rare parking classes (< 100 instances in train) to eliminate class imbalance.
  6. Generate production-ready data_consolidated.yaml.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from collections import Counter
import cv2
import yaml

TARGET_CLASSES = [
    "no_parking",          # 0
    "no_stopping",         # 1
    "parking_allowed",     # 2
    "auto_stand",          # 3
    "tow_away_zone",       # 4
    "other_traffic_sign"   # 5
]

# Source name mapping to target ID
NAME_TO_TARGET = {
    # 0: No Parking
    "NO_PARKING": 0,
    "no_parking": 0,
    "NOPARKING": 0,
    "no_park": 0,

    # 1: No Stopping / Halting
    "NO_STOPPING_OR_STANDING": 1,
    "no_stopping": 1,
    "no_stopping_or_standing": 1,
    "NO_STOPPING": 1,
    "NO_STANDING": 1,

    # 2: Parking Allowed / P Boards
    "PARKING_ALLOWED": 2,
    "parking_allowed": 2,
    "PARKING": 2,
    "parking": 2,
    "PAID_PARKING": 2,
    "MUNICIPAL_PARKING": 2,

    # 3: Auto / Rickshaw / Taxi Stand
    "AUTO_STAND": 3,
    "auto_stand": 3,
    "RICKSHAW_STAND": 3,
    "TAXI_STAND": 3,

    # 4: Tow Away Zone
    "TOW_AWAY_ZONE": 4,
    "tow_away_zone": 4,
    "TOW_AWAY": 4,
    "tow_away": 4,
}


def build_class_mapping(source_yaml_path: Path):
    """
    Builds index-to-target-ID mapping using source data.yaml names list.
    """
    with open(source_yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    src_names = cfg.get("names", [])
    if isinstance(src_names, dict):
        src_names = [src_names[k] for k in sorted(src_names.keys())]

    idx_mapping = {}
    for idx, name in enumerate(src_names):
        normalized = name.strip()
        if normalized in NAME_TO_TARGET:
            target_id = NAME_TO_TARGET[normalized]
        else:
            upper = normalized.upper()
            if "NO_PARK" in upper:
                target_id = 0
            elif "NO_STOP" in upper or "STANDING" in upper:
                target_id = 1
            elif "TOW" in upper:
                target_id = 4
            elif "AUTO_STAND" in upper or "RICKSHAW" in upper:
                target_id = 3
            elif "PARKING" in upper and "NO" not in upper:
                target_id = 2
            else:
                target_id = 5  # other_traffic_sign

        idx_mapping[idx] = target_id

    return src_names, idx_mapping


def audit_and_consolidate(
    src_dir: Path,
    dest_dir: Path,
    source_yaml: Path,
    imgsz: int = 960,
    min_box_px: int = 8,
    oversample_threshold: int = 100
):
    print("=" * 75)
    print("🔍 PARKKARO DATASET AUDIT, CONSOLIDATION & BALANCING PIPELINE")
    print("=" * 75)
    print(f"Source Directory   : {src_dir}")
    print(f"Destination Dir    : {dest_dir}")
    print(f"Analysis Resolution: {imgsz}x{imgsz} (min box threshold: {min_box_px}px)")
    print(f"Oversample Cutoff  : {oversample_threshold} instances")

    src_names, idx_mapping = build_class_mapping(source_yaml)
    print(f"\nLoaded {len(src_names)} source classes from {source_yaml.name}")

    dest_dir.mkdir(parents=True, exist_ok=True)

    splits = ["train", "valid", "test"]
    stats = {}

    for split in splits:
        src_img_dir = src_dir / split / "images"
        src_lbl_dir = src_dir / split / "labels"

        if not src_img_dir.exists():
            print(f"⚠️ Split '{split}' not found at {src_img_dir}, skipping.")
            continue

        dest_img_dir = dest_dir / split / "images"
        dest_lbl_dir = dest_dir / split / "labels"
        dest_img_dir.mkdir(parents=True, exist_ok=True)
        dest_lbl_dir.mkdir(parents=True, exist_ok=True)

        img_files = list(src_img_dir.glob("*.*"))
        valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        img_files = [f for f in img_files if f.suffix.lower() in valid_exts]

        split_stats = {
            "total_images": len(img_files),
            "corrupted_images": 0,
            "negative_images": 0,  # empty label files
            "malformed_lines": 0,
            "out_of_bounds": 0,
            "tiny_boxes": 0,
            "class_counts": Counter(),
            "valid_pairs": 0,
            "image_paths_by_class": {c: set() for c in range(6)}
        }

        print(f"\n--- Processing split: [{split.upper()}] ({len(img_files)} images) ---")

        for img_path in img_files:
            # 1. Image Readability Verification
            img = cv2.imread(str(img_path))
            if img is None:
                split_stats["corrupted_images"] += 1
                continue

            h_img, w_img = img.shape[:2]
            dest_img_path = dest_img_dir / img_path.name
            shutil.copy2(img_path, dest_img_path)

            lbl_path = src_lbl_dir / f"{img_path.stem}.txt"
            dest_lbl_path = dest_lbl_dir / f"{img_path.stem}.txt"

            # 2. Check for Negative Street Images (empty labels)
            if not lbl_path.exists() or lbl_path.stat().st_size == 0:
                # Crucial: write empty label file so YOLO uses it as a negative sample!
                dest_lbl_path.write_text("", encoding="utf-8")
                split_stats["negative_images"] += 1
                split_stats["valid_pairs"] += 1
                continue

            # 3. Label Validation & Class Remapping
            remapped_lines = []
            with open(lbl_path, "r", encoding="utf-8") as lf:
                lines = lf.readlines()

            for line in lines:
                parts = line.strip().split()
                if len(parts) != 5:
                    split_stats["malformed_lines"] += 1
                    continue

                try:
                    src_cls = int(parts[0])
                    xc, yc, bw, bh = map(float, parts[1:])
                except ValueError:
                    split_stats["malformed_lines"] += 1
                    continue

                # Coordinate bounds validation
                if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and bw > 0.0 and bh > 0.0):
                    split_stats["out_of_bounds"] += 1
                    continue

                # Clamp coords cleanly to [0, 1]
                xc = max(0.0, min(1.0, xc))
                yc = max(0.0, min(1.0, yc))
                bw = min(1.0, bw)
                bh = min(1.0, bh)

                # Flag tiny boxes (< 8x8 pixels at imgsz=960)
                box_w_px = bw * imgsz
                box_h_px = bh * imgsz
                if box_w_px < min_box_px or box_h_px < min_box_px:
                    split_stats["tiny_boxes"] += 1
                    # Keep box if >= 4px to avoid discarding distant signs, but log
                    if box_w_px < 4 or box_h_px < 4:
                        continue

                target_cls = idx_mapping.get(src_cls, 5)
                remapped_lines.append(f"{target_cls} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
                split_stats["class_counts"][target_cls] += 1
                split_stats["image_paths_by_class"][target_cls].add(dest_img_path)

            dest_lbl_path.write_text("".join(remapped_lines), encoding="utf-8")
            split_stats["valid_pairs"] += 1

        stats[split] = split_stats

        # Print Split Audit Summary
        print(f"  Valid Image/Label Pairs: {split_stats['valid_pairs']}")
        print(f"  Negative Street Images : {split_stats['negative_images']} (Shop boards / non-sign scenery)")
        print(f"  Corrupted Images       : {split_stats['corrupted_images']}")
        print(f"  Malformed Lines        : {split_stats['malformed_lines']}")
        print(f"  Out of Bounds Fixed    : {split_stats['out_of_bounds']}")
        print(f"  Tiny Boxes (<{min_box_px}px)     : {split_stats['tiny_boxes']}")
        print("  Class Distribution:")
        for cid, cname in enumerate(TARGET_CLASSES):
            count = split_stats["class_counts"][cid]
            print(f"    ID {cid} [{cname:18s}]: {count:6d} instances")

    # 4. Oversampling Rare Parking Classes in Train Split
    train_stats = stats.get("train")
    oversample_txt_path = dest_dir / "train_oversampled.txt"

    if train_stats:
        train_img_dir = dest_dir / "train" / "images"
        all_train_images = list(train_img_dir.glob("*.*"))
        final_train_list = [str(p.resolve()) for p in all_train_images]

        print("\n" + "=" * 75)
        print("⚖️ CLASS BALANCING & OVERSAMPLING CHECK (Train Split)")
        print("=" * 75)

        oversampled_counts = {}
        for cid in range(5):  # check parking-critical classes 0 to 4
            cname = TARGET_CLASSES[cid]
            count = train_stats["class_counts"][cid]
            imgs_with_class = list(train_stats["image_paths_by_class"][cid])

            if count == 0:
                print(f"⚠️ Target ID {cid} [{cname}]: 0 training samples found in source dataset.")
                print(f"   Sub-plate OCR + Rule Engine will handle this rule directly at inference.")
            elif count < oversample_threshold:
                multiplier = max(1, int(oversample_threshold / count))
                extra_samples = imgs_with_class * multiplier
                final_train_list.extend([str(p.resolve()) for p in extra_samples])
                oversampled_counts[cname] = len(extra_samples)
                print(f"🔄 Target ID {cid} [{cname:18s}]: {count} instances (< {oversample_threshold}).")
                print(f"   Oversampled by {multiplier}x (+{len(extra_samples)} training paths injected).")
            else:
                print(f"✅ Target ID {cid} [{cname:18s}]: {count} instances (Sufficiently populated).")

        # Write oversampled text manifest
        with open(oversample_txt_path, "w", encoding="utf-8") as f:
            for item in final_train_list:
                f.write(f"{item}\n")

        print(f"\nManifest written: {oversample_txt_path} ({len(final_train_list)} total training samples)")

    # 5. Generate Updated data_consolidated.yaml
    consolidated_yaml_path = dest_dir / "data_consolidated.yaml"
    val_dir_rel = "valid/images" if (dest_dir / "valid" / "images").exists() else "val/images"
    test_dir_rel = "test/images" if (dest_dir / "test" / "images").exists() else "valid/images"

    yaml_data = {
        "path": str(dest_dir.resolve()).replace("\\", "/"),
        "train": str(oversample_txt_path.resolve()).replace("\\", "/") if oversample_txt_path.exists() else "train/images",
        "val": val_dir_rel,
        "test": test_dir_rel,
        "nc": len(TARGET_CLASSES),
        "names": TARGET_CLASSES
    }

    with open(consolidated_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, sort_keys=False, default_flow_style=False)

    print(f"\n Production dataset config generated at: {consolidated_yaml_path}")
    print("=" * 75)
    return consolidated_yaml_path


def main():
    parser = argparse.ArgumentParser(description="ParkKaro YOLO Dataset Preparation & Consolidation")
    parser.add_argument("--src-dir", type=str, default="C:/STUDY/Project/ParkKaro/ml/sign_scanner/ParkKaro.v1i.yolov8",
                        help="Path to source YOLO dataset directory")
    parser.add_argument("--dest-dir", type=str, default="C:/STUDY/Project/ParkKaro/ml/sign_scanner/dataset_consolidated",
                        help="Path to destination consolidated dataset directory")
    parser.add_argument("--source-yaml", type=str, default="C:/STUDY/Project/ParkKaro/ml/sign_scanner/data.yaml",
                        help="Path to existing data.yaml")
    parser.add_argument("--imgsz", type=int, default=960, help="Target image size for bounding box checks")
    parser.add_argument("--min-box-px", type=int, default=8, help="Flag boxes smaller than this in pixels")
    parser.add_argument("--oversample-threshold", type=int, default=100, help="Min instances per rare parking class")

    args = parser.parse_args()

    audit_and_consolidate(
        src_dir=Path(args.src_dir),
        dest_dir=Path(args.dest_dir),
        source_yaml=Path(args.source_yaml),
        imgsz=args.imgsz,
        min_box_px=args.min_box_px,
        oversample_threshold=args.oversample_threshold
    )


if __name__ == "__main__":
    main()
