import argparse
from pathlib import Path

import numpy as np
from PIL import Image

STYLES = ["Hayao", "Paprika", "Shinkai", "PortraitSketch"]
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def load_model(style: str):
    try:
        from animeganv2 import AnimeGANv2
    except ImportError:
        raise SystemExit("Install animeganv2 first:  pip install animeganv2")
    return AnimeGANv2(style)


def resize_image(img: Image.Image, max_height: int) -> Image.Image:
    w, h = img.size
    if h > max_height:
        img = img.resize((int(w * max_height / h), max_height), Image.LANCZOS)
    return img


def cartoonize(model, img: Image.Image) -> np.ndarray:
    return model(img)


def build_comparison(original: np.ndarray, results: dict[str, np.ndarray],
                     view: str) -> np.ndarray:
    h, w = original.shape[:2]
    panels = [original] + list(results.values())

    for i, p in enumerate(panels):
        if p.shape[:2] != (h, w):
            panels[i] = np.array(Image.fromarray(p.astype("uint8")).resize((w, h), Image.LANCZOS))

    if view == "smart":
        aspect = w / h
        n_styles = len(results)
        use_grid = (n_styles + 1) % 2 == 0 and aspect > 0.75
        view = "grid" if use_grid else ("horizontal" if aspect <= 0.75 else "vertical")

    if view == "horizontal":
        return np.hstack(panels)
    elif view == "vertical":
        return np.vstack(panels)
    elif view == "grid":
        mid = len(panels) // 2
        return np.vstack([np.hstack(panels[:mid]), np.hstack(panels[mid:])])
    else:
        raise ValueError(f"Unknown view: {view}")


def process_image(img_path: Path, models: dict[str, object], out_dir: Path,
                  max_height: int, view: str, skip_comparison: bool, overwrite: bool):
    original_img = resize_image(Image.open(img_path).convert("RGB"), max_height)
    results = {}
    for style, model in models.items():
        style_dir = out_dir / style
        style_dir.mkdir(parents=True, exist_ok=True)
        out_path = style_dir / img_path.name

        if out_path.exists() and not overwrite:
            print(f"  [skip] {out_path} exists")
            results[style] = np.array(Image.open(out_path).convert("RGB"))
            continue

        print(f"  [{style}] cartoonizing {img_path.name}...")
        result = cartoonize(model, original_img)
        Image.fromarray(result.astype("uint8")).save(out_path)
        results[style] = result

    if not skip_comparison and results:
        original = np.array(original_img)
        comparison = build_comparison(original, results, view)
        cmp_dir = out_dir / "comparison"
        cmp_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(comparison.astype("uint8")).save(cmp_dir / img_path.name)
        print(f"  [comparison] saved to {cmp_dir / img_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Cartoonize images using AnimeGAN v2 pretrained models")
    parser.add_argument("--input-dir",  default="input_images",
                        help="Directory containing input images")
    parser.add_argument("--output-dir", default="output_images",
                        help="Directory to save results")
    parser.add_argument("--styles", nargs="+", default=["Hayao"], choices=STYLES)
    parser.add_argument("--all-styles", action="store_true",
                        help="Run all available styles")
    parser.add_argument("--max-height", type=int, default=512,
                        help="Resize images taller than this before processing")
    parser.add_argument("--comparison-view", default="smart",
                        choices=["smart", "horizontal", "vertical", "grid"])
    parser.add_argument("--skip-comparison", action="store_true",
                        help="Save only per-style results, skip side-by-side comparison")
    parser.add_argument("--overwrite", action="store_true",
                        help="Re-generate even if output already exists")
    args = parser.parse_args()

    styles = STYLES if args.all_styles else args.styles
    in_dir  = Path(args.input_dir)
    out_dir = Path(args.output_dir)

    if not in_dir.exists():
        raise SystemExit(f"Input directory not found: {in_dir}")

    image_paths = [p for p in in_dir.iterdir() if p.suffix.lower() in VALID_EXTENSIONS]
    if not image_paths:
        raise SystemExit(f"No images found in {in_dir}")

    print(f"Loading models: {', '.join(styles)}")
    models = {style: load_model(style) for style in styles}

    print(f"Processing {len(image_paths)} image(s) with {len(styles)} style(s)...\n")
    for img_path in sorted(image_paths):
        print(f"[{img_path.name}]")
        process_image(img_path, models, out_dir, args.max_height,
                      args.comparison_view, args.skip_comparison, args.overwrite)

    print(f"\nDone. Results saved to {out_dir}/")


if __name__ == "__main__":
    main()
