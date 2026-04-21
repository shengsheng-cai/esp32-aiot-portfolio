import argparse
from pathlib import Path

import numpy as np
import torch
import torchvision.transforms.functional as TF
from PIL import Image

STYLES = ["paprika", "face_paint_v2", "celeba_distill"]
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}
HUB_REPO = "bryandlee/animegan2-pytorch:main"

PRETRAINED_MAP = {
    "paprika":        "paprika",
    "face_paint_v2":  "face_paint_512_v2",
    "celeba_distill": "celeba_distill",
}


def load_generator(style: str, device: torch.device):
    key = PRETRAINED_MAP[style]
    model = torch.hub.load(HUB_REPO, "generator", pretrained=key, progress=True, trust_repo=True)
    model.eval().to(device)
    return model


def preprocess(img: Image.Image, max_height: int) -> torch.Tensor:
    w, h = img.size
    if h > max_height:
        img = img.resize((int(w * max_height / h), max_height), Image.LANCZOS)
    # AnimeGAN requires dimensions divisible by 32
    w, h = img.size
    img = img.resize(((w // 32) * 32, (h // 32) * 32), Image.LANCZOS)
    return TF.to_tensor(img).unsqueeze(0) * 2 - 1


def postprocess(tensor: torch.Tensor) -> np.ndarray:
    arr = tensor.squeeze().permute(1, 2, 0).cpu().numpy()
    return ((arr + 1) / 2 * 255).clip(0, 255).astype(np.uint8)


def build_comparison(original: np.ndarray, results: dict, view: str) -> np.ndarray:
    h, w = original.shape[:2]
    panels = [original] + list(results.values())

    for i, p in enumerate(panels):
        if p.shape[:2] != (h, w):
            panels[i] = np.array(Image.fromarray(p).resize((w, h), Image.LANCZOS))

    if view == "smart":
        aspect = w / h
        use_grid = (len(results) + 1) % 2 == 0 and aspect > 0.75
        view = "grid" if use_grid else ("horizontal" if aspect <= 0.75 else "vertical")

    if view == "horizontal":
        return np.hstack(panels)
    elif view == "vertical":
        return np.vstack(panels)
    else:
        mid = len(panels) // 2
        return np.vstack([np.hstack(panels[:mid]), np.hstack(panels[mid:])])


def process_image(img_path: Path, models: dict, out_dir: Path,
                  max_height: int, view: str, skip_comparison: bool,
                  overwrite: bool, device: torch.device):
    original = Image.open(img_path).convert("RGB")
    results = {}

    for style, model in models.items():
        style_dir = out_dir / style
        style_dir.mkdir(parents=True, exist_ok=True)
        out_path = style_dir / img_path.name

        if out_path.exists() and not overwrite:
            print(f"  [skip] {out_path} already exists")
            results[style] = np.array(Image.open(out_path).convert("RGB"))
            continue

        print(f"  [{style}] cartoonizing {img_path.name}...")
        inp = preprocess(original, max_height).to(device)
        with torch.no_grad():
            out = model(inp)
        result = postprocess(out)
        Image.fromarray(result).save(out_path)
        results[style] = result

    if not skip_comparison and results:
        w, h = original.size
        if h > max_height:
            original = original.resize((int(w * max_height / h), max_height), Image.LANCZOS)
        comparison = build_comparison(np.array(original), results, view)
        cmp_dir = out_dir / "comparison"
        cmp_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(comparison).save(cmp_dir / img_path.name)
        print(f"  [comparison] {cmp_dir / img_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Cartoonize images using AnimeGANv2 (PyTorch)")
    parser.add_argument("--input-dir",  default="input_images")
    parser.add_argument("--output-dir", default="output_images")
    parser.add_argument("--styles", nargs="+", default=["paprika"], choices=STYLES)
    parser.add_argument("--all-styles", action="store_true")
    parser.add_argument("--max-height", type=int, default=300)
    parser.add_argument("--comparison-view", default="smart",
                        choices=["smart", "horizontal", "vertical", "grid"])
    parser.add_argument("--skip-comparison", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    styles  = STYLES if args.all_styles else args.styles
    in_dir  = Path(args.input_dir)
    out_dir = Path(args.output_dir)

    if not in_dir.exists():
        raise SystemExit(f"Input directory not found: {in_dir}")

    image_paths = [p for p in sorted(in_dir.iterdir())
                   if p.suffix.lower() in VALID_EXTENSIONS]
    if not image_paths:
        raise SystemExit(f"No images found in {in_dir}")

    print(f"Device: {device}")
    print(f"Loading models: {', '.join(styles)}")
    models = {s: load_generator(s, device) for s in styles}

    print(f"Processing {len(image_paths)} image(s) with {len(styles)} style(s)...\n")
    for img_path in image_paths:
        print(f"[{img_path.name}]")
        process_image(img_path, models, out_dir, args.max_height,
                      args.comparison_view, args.skip_comparison, args.overwrite, device)

    print(f"\nDone. Results saved to {out_dir}/")


if __name__ == "__main__":
    main()
