import argparse
import cv2


METHODS = {
    "NEAREST":  cv2.INTER_NEAREST,
    "LINEAR":   cv2.INTER_LINEAR,
    "AREA":     cv2.INTER_AREA,
    "CUBIC":    cv2.INTER_CUBIC,
    "LANCZOS4": cv2.INTER_LANCZOS4,
}


def show_enlarge(img):
    small = cv2.resize(img, (0, 0), fx=0.2, fy=0.2)
    for name, flag in METHODS.items():
        cv2.imshow(f"Enlarge {name}", cv2.resize(small, (0, 0), fx=7, fy=7, interpolation=flag))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_shrink(img):
    for name, flag in METHODS.items():
        cv2.imshow(f"Shrink {name}", cv2.resize(img, (0, 0), fx=0.18, fy=0.18, interpolation=flag))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="image path")
    ap.add_argument("--mode", choices=["enlarge", "shrink", "all"], default="all")
    args = ap.parse_args()

    img = cv2.imread(args.source)
    if img is None:
        print(f"[ERROR] Cannot read image: {args.source}")
        return

    if args.mode == "enlarge":
        show_enlarge(img)
    elif args.mode == "shrink":
        show_shrink(img)
    else:
        show_enlarge(img)
        show_shrink(img)


if __name__ == "__main__":
    main()
