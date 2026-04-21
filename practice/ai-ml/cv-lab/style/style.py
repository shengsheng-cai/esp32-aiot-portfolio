import argparse
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from torchvision.models import VGG19_Weights, Inception_V3_Weights
from PIL import Image
import numpy as np

DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

CONTENT_LAYERS = {"features.30"}
STYLE_LAYERS = {"features.0", "features.5", "features.10", "features.19", "features.28"}


# ─── Image helpers ───────────────────────────────────────────────────────────

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

_MEAN_T = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
_STD_T  = torch.tensor(IMAGENET_STD).view(3, 1, 1)

_to_tensor = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])

def load_image(path: str, size: int | None = None) -> torch.Tensor:
    img = Image.open(path).convert("RGB")
    if size:
        w, h = img.size
        img = img.resize((size, int(h * size / w)), Image.LANCZOS)
    return _to_tensor(img).unsqueeze(0).to(DEVICE)


def save_image(tensor: torch.Tensor, path: str):
    img = tensor.squeeze(0).cpu().detach()
    img = (img * _STD_T + _MEAN_T).clamp(0, 1)
    transforms.ToPILImage()(img).save(path)
    print(f"Saved: {path}")


# ─── Style Transfer ──────────────────────────────────────────────────────────

def gram_matrix(x: torch.Tensor) -> torch.Tensor:
    b, c, h, w = x.size()
    f = x.view(b, c, h * w)
    return torch.bmm(f, f.transpose(1, 2)) / (c * h * w)


class StyleTransfer:
    def __init__(self):
        vgg = models.vgg19(weights=VGG19_Weights.IMAGENET1K_V1).features.eval().to(DEVICE)
        for p in vgg.parameters():
            p.requires_grad_(False)
        self.vgg = vgg

    def _get_features(self, x: torch.Tensor,
                      target_layers: set[str]) -> dict[str, torch.Tensor]:
        features = {}
        for name, layer in self.vgg.named_children():
            key = f"features.{name}"
            x = layer(x)
            if key in target_layers:
                features[key] = x
            if len(features) == len(target_layers):
                break
        return features

    def run(self, content_path: str, style_path: str, size: int,
            steps: int, content_w: float, style_w: float, tv_w: float,
            out_path: str):
        content = load_image(content_path, size)
        style   = load_image(style_path, size)

        content_feats = self._get_features(content, CONTENT_LAYERS)
        style_grams   = {
            k: gram_matrix(v)
            for k, v in self._get_features(style, STYLE_LAYERS).items()
        }

        canvas = content.clone().requires_grad_(True)
        optimizer = torch.optim.LBFGS([canvas], max_iter=20)

        step = 0
        while step < steps:
            def closure():
                nonlocal step
                canvas.data.clamp_(0, 1)
                optimizer.zero_grad()
                feats = self._get_features(canvas, CONTENT_LAYERS | STYLE_LAYERS)

                c_loss = sum(
                    F.mse_loss(feats[k], content_feats[k])
                    for k in CONTENT_LAYERS
                )
                s_loss = sum(
                    F.mse_loss(gram_matrix(feats[k]), style_grams[k])
                    for k in STYLE_LAYERS
                )
                tv_loss = (
                    torch.sum(torch.abs(canvas[:, :, :, :-1] - canvas[:, :, :, 1:])) +
                    torch.sum(torch.abs(canvas[:, :, :-1, :] - canvas[:, :, 1:, :]))
                )
                loss = content_w * c_loss + style_w * s_loss + tv_w * tv_loss
                loss.backward()

                if step % 50 == 0:
                    print(f"  step {step:04d} | loss {loss.item():.2f} "
                          f"(content {c_loss.item():.2f} style {s_loss.item():.4f})")
                step += 1
                return loss

            optimizer.step(closure)

        save_image(canvas, out_path)


# ─── Deep Dream ──────────────────────────────────────────────────────────────

DREAM_LAYERS = {
    "Mixed_5d": 0.2,
    "Mixed_6a": 0.5,
    "Mixed_6b": 2.0,
    "Mixed_6c": 1.5,
}


class DeepDream:
    def __init__(self):
        inception = models.inception_v3(weights=Inception_V3_Weights.IMAGENET1K_V1).eval().to(DEVICE)
        for p in inception.parameters():
            p.requires_grad_(False)
        self.model = inception

    def _get_activations(self, x: torch.Tensor) -> list[torch.Tensor]:
        acts = []
        for name, layer in self.model.named_children():
            if name in ("AuxLogits", "fc"):
                continue
            x = layer(x)
            if name in DREAM_LAYERS:
                acts.append(DREAM_LAYERS[name] * x)
                if len(acts) == len(DREAM_LAYERS):
                    break
        return acts

    def _gradient_ascent(self, img: np.ndarray, steps: int, step_size: float,
                         max_loss: float) -> np.ndarray:
        t = torch.tensor(img, dtype=torch.float32, device=DEVICE).unsqueeze(0)
        t.requires_grad_(True)
        for i in range(steps):
            acts = self._get_activations(t)
            if not acts:
                break
            loss = sum(a.norm() for a in acts)
            if loss.item() > max_loss:
                break
            loss.backward()
            with torch.no_grad():
                grad = t.grad / (t.grad.abs().mean() + 1e-8)
                t += step_size * grad
                t.grad.zero_()
            if i % 5 == 0:
                print(f"    ascent step {i:02d} | loss {loss.item():.4f}")
        return t.detach().squeeze(0).cpu().numpy()

    def run(self, img_path: str, out_path: str, num_octave: int,
            octave_scale: float, steps: int, step_size: float, max_loss: float):
        img = np.array(Image.open(img_path).convert("RGB")).astype("float32") / 255.0
        img = np.transpose(img, (2, 0, 1))  # HWC → CHW

        original_shape = img.shape[1:]
        octave_shapes = [original_shape]
        for i in range(1, num_octave):
            h = int(original_shape[0] / (octave_scale ** i))
            w = int(original_shape[1] / (octave_scale ** i))
            octave_shapes.append((h, w))
        octave_shapes = octave_shapes[::-1]

        shrunk = self._resize(img, octave_shapes[0])
        current = shrunk.copy()

        for shape in octave_shapes:
            print(f"Octave shape: {shape}")
            current = self._resize(current, shape)
            current = self._gradient_ascent(current, steps, step_size, max_loss)
            upscaled_shrunk = self._resize(shrunk, shape)
            same_size_orig  = self._resize(img, shape)
            current += same_size_orig - upscaled_shrunk
            shrunk = self._resize(img, shape)

        result = np.transpose(np.clip(current, 0, 1), (1, 2, 0))
        Image.fromarray((result * 255).astype(np.uint8)).save(out_path)
        print(f"Saved: {out_path}")

    @staticmethod
    def _resize(img: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
        h, w = shape
        pil = Image.fromarray(
            (np.transpose(np.clip(img, 0, 1), (1, 2, 0)) * 255).astype(np.uint8)
        )
        return np.transpose(
            np.array(pil.resize((w, h), Image.LANCZOS)).astype("float32") / 255.0,
            (2, 0, 1),
        )


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    global DEVICE
    device_parser = argparse.ArgumentParser(add_help=False)
    device_parser.add_argument("--device", default=DEVICE, choices=["cpu", "cuda", "mps"])

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)

    sp = sub.add_parser("style", parents=[device_parser], help="Neural Style Transfer")
    sp.add_argument("--content", required=True)
    sp.add_argument("--style",   required=True)
    sp.add_argument("--out",     default="result_style.png")
    sp.add_argument("--size",    type=int, default=400)
    sp.add_argument("--steps",   type=int, default=300)
    sp.add_argument("--content-weight", type=float, default=1.0)
    sp.add_argument("--style-weight",   type=float, default=1e6)
    sp.add_argument("--tv-weight",      type=float, default=1e-4)

    dp = sub.add_parser("dream", parents=[device_parser], help="Deep Dream")
    dp.add_argument("--img",         required=True)
    dp.add_argument("--out",         default="result_dream.png")
    dp.add_argument("--num-octave",  type=int,   default=3)
    dp.add_argument("--octave-scale",type=float, default=1.4)
    dp.add_argument("--steps",       type=int,   default=20)
    dp.add_argument("--step-size",   type=float, default=0.01)
    dp.add_argument("--max-loss",    type=float, default=10.0)

    args = parser.parse_args()
    DEVICE = args.device
    print(f"Device: {DEVICE} | Mode: {args.mode}")

    if args.mode == "style":
        StyleTransfer().run(
            args.content, args.style, args.size, args.steps,
            args.content_weight, args.style_weight, args.tv_weight, args.out,
        )
    else:
        DeepDream().run(
            args.img, args.out, args.num_octave, args.octave_scale,
            args.steps, args.step_size, args.max_loss,
        )


if __name__ == "__main__":
    main()
