import os
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
import torch
from supabase import create_client

from predict import MODEL_PATH, load_classifier, predict_image

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")
    return create_client(url, key)

def sync_classes_to_db(supabase, classes: list[str]):
    rows = [{"class_name": name} for name in classes]
    supabase.table("sign_classes").upsert(rows, on_conflict="class_name").execute()


def ensure_model_from_supabase(model_path: Path = MODEL_PATH) -> Path:
    """Download trained weights from Supabase Storage if not cached locally."""
    if model_path.exists():
        return model_path
    supabase = get_supabase_client()
    bucket = os.environ.get("SUPABASE_BUCKET", "traffic-signs")
    data = supabase.storage.from_(bucket).download("models/traffic_sign_classifier.pth")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_bytes(data)
    return model_path


def classify_and_log(image_path: Path, model_path: Path = MODEL_PATH):
    ensure_model_from_supabase(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, classes = load_classifier(model_path, device)
    predictions = predict_image(image_path, model, classes, device, top_k=1)
    top_label, top_conf = predictions[0]

    supabase = get_supabase_client()
    bucket = os.environ.get("SUPABASE_BUCKET", "traffic-signs")
    storage_path = f"predictions/{uuid4().hex}_{image_path.name}"

    with open(image_path, "rb") as f:
        supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=f,
            file_options={"content-type": "image/jpeg"},
        )

    supabase.table("prediction_logs").insert({
        "image_path": storage_path,
        "predicted_class": top_label,
        "confidence": round(top_conf, 2),
    }).execute()

    print(f"Predicted: {top_label} ({top_conf:.2f}%)")
    print(f"Uploaded to: {bucket}/{storage_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        classify_and_log(Path(sys.argv[1]))
    else:
        supabase = get_supabase_client()
        bucket = os.environ.get("SUPABASE_BUCKET", "traffic-signs")
        sample_bytes = supabase.storage.from_(bucket).download("dataset/test/COMPULSARY_AHEAD/06046.jpg")
        tmp_sample = BASE_DIR / "_tmp_sample.jpg"
        tmp_sample.write_bytes(sample_bytes)
        try:
            classify_and_log(tmp_sample)
        finally:
            tmp_sample.unlink(missing_ok=True)
