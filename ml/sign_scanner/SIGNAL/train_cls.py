from pathlib import Path
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

BASE_DIR = Path(__file__).resolve().parent
DATA_ROOT = BASE_DIR / "dataset" / "traffic_sign_classification_dataset"
TRAIN_DIR = DATA_ROOT / "train"
VAL_DIR = DATA_ROOT / "test"

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    train_tfms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    val_tfms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    train_ds = datasets.ImageFolder(TRAIN_DIR, transform=train_tfms)
    val_ds = datasets.ImageFolder(VAL_DIR, transform=val_tfms)

    num_classes = len(train_ds.classes)
    print(f"Found {num_classes} classes")

    # On Windows, num_workers=0 avoids DataLoader worker spawn issues
    num_workers = 0
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_ds, batch_size=32, shuffle=False, num_workers=num_workers)

    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    epochs = 10
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(inputs), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                preds = model(inputs).argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        train_loss = running_loss / len(train_ds)
        val_acc = (correct / total) * 100 if total else 0.0
        print(f"Epoch {epoch}/{epochs} - Loss: {train_loss:.4f} - Val Acc: {val_acc:.2f}%")

    save_path = BASE_DIR / "traffic_sign_classifier.pth"
    torch.save({"model_state_dict": model.state_dict(), "classes": train_ds.classes}, save_path)
    print("Saved model to:", save_path)

if __name__ == "__main__":
    main()
