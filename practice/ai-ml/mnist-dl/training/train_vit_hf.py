"""
Fine-tune google/vit-base-patch16-224 on MNIST。
輸出兩個版本：
  - myvit_mnist_hf_4060.pth  （快速版，3 epochs）
  - myvit_mnist_hf_best_tuned.pth（強化版，含 data augmentation + early stopping）
"""
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import datasets, transforms
from transformers import ViTForImageClassification, ViTImageProcessor, get_cosine_schedule_with_warmup

MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

MODEL_NAME = "google/vit-base-patch16-224"
BATCH_SIZE = 8


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def base_vit_transform(processor):
    """Resize + Grayscale→RGB + Normalize，train_quick 與 val 共用。"""
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.Grayscale(num_output_channels=3),
        transforms.ToTensor(),
        transforms.Normalize(mean=processor.image_mean, std=processor.image_std),
    ])


class MNISTforViT(Dataset):
    """把 MNIST 轉成 ViT 需要的 224×224 RGB 格式。"""
    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform

    def __getitem__(self, idx):
        x, y = self.subset[idx]
        return self.transform(x), y

    def __len__(self):
        return len(self.subset)


def train_quick(device, processor):
    """快速版：3 epochs，對應 ViT_HF_4060。"""
    print("\n=== 快速版 (myvit_mnist_hf_4060.pth) ===")
    transform = base_vit_transform(processor)
    train_ds = datasets.MNIST(root="./data", train=True, download=True, transform=transform)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)

    model = ViTForImageClassification.from_pretrained(
        MODEL_NAME, num_labels=10, ignore_mismatched_sizes=True
    ).to(device)

    optimizer = optim.AdamW(model.parameters(), lr=2e-5)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(3):
        model.train()
        total_loss = 0
        for i, (x, y) in enumerate(train_loader):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x).logits, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            if i % 200 == 0:
                print(f"  Epoch {epoch+1} batch {i}/{len(train_loader)}  Loss: {loss.item():.4f}")
        print(f"Epoch {epoch+1} avg loss: {total_loss/len(train_loader):.4f}")

    path = MODEL_DIR / "myvit_mnist_hf_4060.pth"
    torch.save(model.state_dict(), path)
    print(f"Saved → {path}")


def train_best(device, processor):
    """強化版：data augmentation + early stopping + checkpoint 續跑，對應 ViT_HF_BestTuned。"""
    print("\n=== 強化版 (myvit_mnist_hf_best_tuned.pth) ===")
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.Grayscale(num_output_channels=3),
        transforms.RandomRotation(20),
        transforms.RandomAffine(0, translate=(0.15, 0.15), scale=(0.85, 1.15)),
        transforms.ToTensor(),
        transforms.Normalize(mean=processor.image_mean, std=processor.image_std),
    ])
    val_transform = base_vit_transform(processor)

    raw_ds = datasets.MNIST(root="./data", train=True, download=True)
    raw_train, raw_val = random_split(raw_ds, [55000, 5000], generator=torch.Generator().manual_seed(42))
    train_loader = DataLoader(MNISTforViT(raw_train, train_transform), batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(MNISTforViT(raw_val, val_transform), batch_size=BATCH_SIZE)

    epochs = 3
    model = ViTForImageClassification.from_pretrained(
        MODEL_NAME, num_labels=10, ignore_mismatched_sizes=True
    ).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=5e-5, weight_decay=0.01)
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=len(train_loader),
        num_training_steps=len(train_loader) * epochs,
    )
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    save_path = MODEL_DIR / "myvit_mnist_hf_best_tuned.pth"
    ckpt_path = MODEL_DIR / "myvit_mnist_hf_best_tuned_ckpt.pth"

    start_epoch = 0
    best_acc = 0.0
    if ckpt_path.exists():
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=True)
        model.load_state_dict(ckpt["model"])
        optimizer.load_state_dict(ckpt["optimizer"])
        scheduler.load_state_dict(ckpt["scheduler"])
        start_epoch = ckpt["epoch"] + 1
        best_acc = ckpt["best_acc"]
        print(f"Checkpoint 載入：從 Epoch {start_epoch + 1} 繼續，目前最佳 {best_acc*100:.2f}%")

    for epoch in range(start_epoch, epochs):
        model.train()
        t0 = time.time()
        for i, (x, y) in enumerate(train_loader):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x).logits, y)
            loss.backward()
            optimizer.step()
            scheduler.step()
            if i % 50 == 0:
                dt = time.time() - t0
                print(f"  Epoch {epoch+1} batch {i}/{len(train_loader)}  Loss: {loss.item():.4f}  {dt:.1f}s", flush=True)
                t0 = time.time()

        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                correct += (model(x).logits.argmax(1) == y).sum().item()
                total += y.size(0)
        acc = correct / total
        print(f"Epoch {epoch+1:02d}  Val Acc: {acc*100:.2f}%")

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), save_path)
            print(f"  → Best! Saved to {save_path}")

        torch.save({
            "epoch": epoch,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "scheduler": scheduler.state_dict(),
            "best_acc": best_acc,
        }, ckpt_path)

    ckpt_path.unlink(missing_ok=True)
    print(f"Done. Best Val Acc: {best_acc*100:.2f}%")


if __name__ == "__main__":
    device = get_device()
    print(f"Device: {device}")
    processor = ViTImageProcessor.from_pretrained(MODEL_NAME)
    if not (MODEL_DIR / "myvit_mnist_hf_4060.pth").exists():
        train_quick(device, processor)
    else:
        print("快速版已存在，跳過。")
    train_best(device, processor)
