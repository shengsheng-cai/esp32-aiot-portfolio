import argparse
import cv2


THRESHOLDS = [30, 50, 80, 110]


def show_threshold(img, flag, label):
    cv2.imshow("Original", img)
    for t in THRESHOLDS:
        cv2.imshow(f"{label} thresh={t}", cv2.threshold(img, t, 255, flag)[1])
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="image path")
    ap.add_argument("--mode", choices=["binary", "binary_inv", "all"], default="all")
    ap.add_argument("--gray", action="store_true", help="convert to grayscale before thresholding")
    args = ap.parse_args()

    img = cv2.imread(args.source)
    if img is None:
        print(f"[ERROR] Cannot read image: {args.source}")
        return

    if args.gray:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (5, 5), 0)

    if args.mode in ("binary", "all"):
        show_threshold(img, cv2.THRESH_BINARY, "BINARY")
    if args.mode in ("binary_inv", "all"):
        show_threshold(img, cv2.THRESH_BINARY_INV, "BINARY_INV")


if __name__ == "__main__":
    main()
