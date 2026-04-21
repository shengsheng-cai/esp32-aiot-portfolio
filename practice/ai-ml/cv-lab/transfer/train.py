import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms
from torchvision.models import ResNet50_Weights, EfficientNet_B0_Weights
from tqdm import tqdm

DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
CLASSES = 10
CIFAR10_LABELS = ["airplane","automobile","bird","cat","deer","dog","frog","horse","ship","truck"]


def get_model(name: str) -> nn.Module:
    if name == "resnet50":
        model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        model.fc = nn.Linear(model.fc.in_features, CLASSES)
    elif name == "efficientnet":
        model = models.efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, CLASSES)
    else:
        raise ValueError(f"Unknown model: {name}")
    return model


def freeze_backbone(model: nn.Module, name: str):
    for p in model.parameters():
        p.requires_grad = False
    head = model.fc if name == "resnet50" else model.classifier
    for p in head.parameters():
        p.requires_grad = True


def get_loaders(img_size: int, batch_size: int, subset: int | None = None):
    mean, std = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
    train_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    test_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    train_ds = datasets.CIFAR10("data", train=True, download=True, transform=train_tf)
    test_ds = datasets.CIFAR10("data", train=False, download=True, transform=test_tf)
    if subset:
        train_ds = Subset(train_ds, range(min(subset, len(train_ds))))
        test_ds = Subset(test_ds, range(min(subset // 5, len(test_ds))))
    return (
        DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0),
        DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0),
    )


def train_epoch(model, loader, optimizer, criterion, desc="train"):
    model.train()
    loss_sum, correct = 0.0, 0
    pbar = tqdm(loader, desc=desc, leave=False)
    for x, y in pbar:
        x, y = x.to(DEVICE), y.to(DEVICE)
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        loss_sum += loss.item() * x.size(0)
        correct += (out.argmax(1) == y).sum().item()
        pbar.set_postfix(loss=f"{loss.item():.3f}")
    n = len(loader.dataset)
    return loss_sum / n, correct / n


@torch.no_grad()
def evaluate(model, loader, criterion, desc="eval"):
    model.eval()
    loss_sum, correct = 0.0, 0
    for x, y in tqdm(loader, desc=desc, leave=False):
        x, y = x.to(DEVICE), y.to(DEVICE)
        out = model(x)
        loss_sum += criterion(out, y).item() * x.size(0)
        correct += (out.argmax(1) == y).sum().item()
    n = len(loader.dataset)
    return loss_sum / n, correct / n


def run_phase(label, epochs, model, train_loader, test_loader, optimizer, criterion):
    print(f"\n=== {label} ===")
    for epoch in range(1, epochs + 1):
        tr_loss, tr_acc = train_epoch(model, train_loader, optimizer, criterion)
        val_loss, val_acc = evaluate(model, test_loader, criterion)
        print(f"  Epoch {epoch:02d}/{epochs} | loss {tr_loss:.4f} acc {tr_acc:.4f} | val_loss {val_loss:.4f} val_acc {val_acc:.4f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="resnet50", choices=["resnet50", "efficientnet"])
    parser.add_argument("--epochs-extract", type=int, default=5)
    parser.add_argument("--epochs-finetune", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--img-size", type=int, default=64)
    parser.add_argument("--subset", type=int, default=None,
                        help="Use only N training samples (for quick testing)")
    args = parser.parse_args()

    print(f"Device: {DEVICE} | Model: {args.model}")
    if args.subset:
        print(f"Subset mode: {args.subset} training samples")
    train_loader, test_loader = get_loaders(args.img_size, args.batch_size, args.subset)

    model = get_model(args.model).to(DEVICE)
    criterion = nn.CrossEntropyLoss()

    freeze_backbone(model, args.model)
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3)
    run_phase("Phase 1: Feature Extraction", args.epochs_extract, model, train_loader, test_loader, optimizer, criterion)

    for p in model.parameters():
        p.requires_grad = True
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    run_phase("Phase 2: Fine-tuning", args.epochs_finetune, model, train_loader, test_loader, optimizer, criterion)

    _, acc = evaluate(model, test_loader, criterion)
    print(f"\nFinal test accuracy: {acc:.4f}")

    out_path = f"{args.model}_cifar10.pth"
    torch.save(model.state_dict(), out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
