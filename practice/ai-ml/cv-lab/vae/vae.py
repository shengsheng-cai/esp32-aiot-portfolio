import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np

DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
LATENT_DIM = 2


# ─── VAE ────────────────────────────────────────────────────────────────────

class Encoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, 3, stride=2, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1), nn.ReLU(),
        )
        self.fc = nn.Linear(64 * 7 * 7, 16)
        self.fc_mean = nn.Linear(16, LATENT_DIM)
        self.fc_logvar = nn.Linear(16, LATENT_DIM)

    def forward(self, x):
        x = self.conv(x).flatten(1)
        x = F.relu(self.fc(x))
        return self.fc_mean(x), self.fc_logvar(x)


class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(LATENT_DIM, 64 * 7 * 7)
        self.deconv = nn.Sequential(
            nn.ConvTranspose2d(64, 64, 3, stride=2, padding=1, output_padding=1), nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1), nn.ReLU(),
            nn.ConvTranspose2d(32, 1, 3, padding=1), nn.Sigmoid(),
        )

    def forward(self, z):
        x = F.relu(self.fc(z)).view(-1, 64, 7, 7)
        return self.deconv(x)


class VAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = Encoder()
        self.decoder = Decoder()

    def reparameterize(self, mean, logvar):
        std = torch.exp(0.5 * logvar)
        return mean + std * torch.randn_like(std)

    def forward(self, x):
        mean, logvar = self.encoder(x)
        z = self.reparameterize(mean, logvar)
        return self.decoder(z), mean, logvar


def vae_loss(recon, x, mean, logvar):
    recon_loss = F.binary_cross_entropy(recon, x, reduction="sum")
    kl = -0.5 * torch.sum(1 + logvar - mean.pow(2) - logvar.exp())
    return recon_loss + kl


# ─── Denoising AE ───────────────────────────────────────────────────────────

class DenoisingAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.decoder = nn.Sequential(
            nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(32, 1, 3, padding=1), nn.Sigmoid(),
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))


# ─── Data ────────────────────────────────────────────────────────────────────

def get_loaders(batch_size: int):
    tf = transforms.ToTensor()
    train = datasets.MNIST("data", train=True, download=True, transform=tf)
    test = datasets.MNIST("data", train=False, download=True, transform=tf)
    return (
        DataLoader(train, batch_size=batch_size, shuffle=True),
        DataLoader(test, batch_size=batch_size, shuffle=False),
    )


def add_noise(x: torch.Tensor, factor: float = 0.5) -> torch.Tensor:
    return (x + factor * torch.randn_like(x)).clamp(0, 1)


# ─── Train ───────────────────────────────────────────────────────────────────

def _train_loop(model, train_loader, optimizer, compute_loss, epochs, save_path):
    for epoch in range(1, epochs + 1):
        model.train()
        total = 0.0
        for x, _ in train_loader:
            x = x.to(DEVICE)
            optimizer.zero_grad()
            loss = compute_loss(model, x)
            loss.backward()
            optimizer.step()
            total += loss.item()
        print(f"Epoch {epoch:02d}/{epochs} | loss {total / len(train_loader.dataset):.4f}")
    torch.save(model.state_dict(), save_path)
    print(f"Saved: {save_path}")
    return model


def train_vae(train_loader, epochs: int):
    model = VAE().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    def compute_loss(m, x):
        recon, mean, logvar = m(x)
        return vae_loss(recon, x, mean, logvar)
    return _train_loop(model, train_loader, optimizer, compute_loss, epochs, "vae.pth")


def train_denoise(train_loader, epochs: int):
    model = DenoisingAE().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    def compute_loss(m, x):
        return F.binary_cross_entropy(m(add_noise(x)), x, reduction="sum")
    return _train_loop(model, train_loader, optimizer, compute_loss, epochs, "denoise_ae.pth")


# ─── Visualize ───────────────────────────────────────────────────────────────

@torch.no_grad()
def plot_latent_space(model: VAE, n: int = 20):
    grid_x = np.linspace(-1.5, 1.5, n)
    grid_y = np.linspace(-1.5, 1.5, n)[::-1]
    canvas = np.zeros((28 * n, 28 * n))

    for i, yi in enumerate(grid_y):
        for j, xi in enumerate(grid_x):
            z = torch.tensor([[xi, yi]], dtype=torch.float32).to(DEVICE)
            img = model.decoder(z).cpu().squeeze().numpy()
            canvas[i * 28:(i + 1) * 28, j * 28:(j + 1) * 28] = img

    plt.figure(figsize=(10, 10))
    plt.imshow(canvas, cmap="Greys_r")
    plt.xticks(np.arange(14, 28 * n, 28), np.round(grid_x, 1), fontsize=7)
    plt.yticks(np.arange(14, 28 * n, 28), np.round(grid_y, 1), fontsize=7)
    plt.xlabel("z[0]")
    plt.ylabel("z[1]")
    plt.title("VAE Latent Space — 2D Manifold")
    plt.tight_layout()
    plt.savefig("latent_space.png", dpi=100)
    plt.show()
    print("Saved: latent_space.png")


@torch.no_grad()
def plot_label_clusters(model: VAE, loader: DataLoader):
    model.eval()
    zs, labels = [], []
    for x, y in loader:
        mean, _ = model.encoder(x.to(DEVICE))
        zs.append(mean.cpu().numpy())
        labels.append(y.numpy())
    zs = np.concatenate(zs)
    labels = np.concatenate(labels)

    plt.figure(figsize=(8, 6))
    sc = plt.scatter(zs[:, 0], zs[:, 1], c=labels, cmap="tab10", alpha=0.5, s=5)
    plt.colorbar(sc, label="digit")
    plt.title("VAE Latent Space — Label Clusters")
    plt.xlabel("z[0]")
    plt.ylabel("z[1]")
    plt.tight_layout()
    plt.savefig("label_clusters.png", dpi=100)
    plt.show()
    print("Saved: label_clusters.png")


@torch.no_grad()
def plot_denoise(model: DenoisingAE, loader: DataLoader, n: int = 10):
    model.eval()
    x, _ = next(iter(loader))
    x = x[:n].to(DEVICE)
    noisy = add_noise(x)
    recon = model(noisy)

    fig, axes = plt.subplots(3, n, figsize=(20, 6))
    for i in range(n):
        for row, img in enumerate([x, noisy, recon]):
            axes[row, i].imshow(img[i].cpu().squeeze(), cmap="gray")
            axes[row, i].axis("off")
    axes[0, 0].set_ylabel("Original", fontsize=10)
    axes[1, 0].set_ylabel("Noisy", fontsize=10)
    axes[2, 0].set_ylabel("Denoised", fontsize=10)
    plt.suptitle("Denoising AutoEncoder")
    plt.tight_layout()
    plt.savefig("denoise_result.png", dpi=100)
    plt.show()
    print("Saved: denoise_result.png")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="vae", choices=["vae", "denoise"])
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()

    print(f"Device: {DEVICE} | Mode: {args.mode}")
    train_loader, test_loader = get_loaders(args.batch_size)

    if args.mode == "vae":
        model = train_vae(train_loader, args.epochs)
        plot_latent_space(model)
        plot_label_clusters(model, test_loader)
    else:
        model = train_denoise(train_loader, args.epochs)
        plot_denoise(model, test_loader)


if __name__ == "__main__":
    main()
