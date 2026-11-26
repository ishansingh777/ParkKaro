from pathlib import Path
import argparse
from PIL import Image
import torch
from torch import nn
from torchvision import models, transforms

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "traffic_sign_classifier.pth"

def load_classifier(model_path: Path, device: torch.device):
    checkpoint = torch.load(model_path, map_location=device, weights_only=True)
    classes = checkpoint["classes"]

    # weights=None avoids downloading ImageNet weights because trained weights are loaded next
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(classes))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model, classes

def predict_image(image_path: Path, model: nn.Module, classes: list[str], device: torch.device, top_k: int = 3):
    infer_tfms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    image = Image.open(image_path).convert("RGB")
    tensor = infer_tfms(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0]

    k = min(top_k, len(classes))
    top_probs, top_indices = torch.topk(probs, k=k)

    results = []
    for prob, idx in zip(top_probs.tolist(), top_indices.tolist()):
        results.append((classes[idx], prob * 100.0))
    return results

def main():
    parser = argparse.ArgumentParser(description="Classify a traffic sign image.")
    parser.add_argument("image_path", type=Path, help="Path to the input traffic sign image")
    parser.add_argument("--model", type=Path, default=MODEL_PATH, help="Path to traffic_sign_classifier.pth")
    parser.add_argument("--top-k", type=int, default=3, help="Number of top predictions to display")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, classes = load_classifier(args.model, device)
    predictions = predict_image(args.image_path, model, classes, device, top_k=args.top_k)

    print(f"Image: {args.image_path}")
    for rank, (label, confidence) in enumerate(predictions, start=1):
        print(f"  {rank}. {label} ({confidence:.2f}%)")

if __name__ == "__main__":
    main()
