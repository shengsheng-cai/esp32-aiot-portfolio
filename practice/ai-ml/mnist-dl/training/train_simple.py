"""訓練 SimpleNN 和 SimpleCNN，輸出到 ../models/"""
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from models import SimpleCNN, SimpleNN

MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

EPOCHS = 5
BATCH_SIZE = 64
LR = 1e-3


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def get_loaders():
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)),
    ])
    train_ds = datasets.MNIST(root="./data", train=True, download=True, transform=transform)
    test_ds = datasets.MNIST(root="./data", train=False, download=True, transform=transform)
    return (
        DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True),
        DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False),
    )


def train(model, train_loader, test_loader, device, save_name):
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f"[{save_name}] Epoch {epoch+1}/{EPOCHS}  Loss: {running_loss/len(train_loader):.4f}")

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(1)
            correct += (pred == y).sum().item()
            total += y.size(0)
    acc = correct / total
    print(f"[{save_name}] Test Accuracy: {acc*100:.2f}%")

    path = MODEL_DIR / save_name
    torch.save(model.state_dict(), path)
    print(f"Saved → {path}\n")


if __name__ == "__main__":
    device = get_device()
    print(f"Device: {device}")
    train_loader, test_loader = get_loaders()

    train(SimpleNN().to(device), train_loader, test_loader, device, "simple_nn_mnist.pth")
    train(SimpleCNN().to(device), train_loader, test_loader, device, "simple_cnn_mnist.pth")
