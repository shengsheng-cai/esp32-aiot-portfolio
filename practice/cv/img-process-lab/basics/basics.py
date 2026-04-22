import argparse
import cv2
import numpy as np


def show_resize(img):
    h, w = img.shape[:2]
    fixed = cv2.resize(img, (200, 200))
    ratio = cv2.resize(img, (300, int(h * 300 / w)))
    cv2.imshow("Resize Fixed 200x200", fixed)
    cv2.imshow("Resize Keep Ratio", ratio)
    cv2.waitKey(0)


def show_rotate(img):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), -45, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h))
    cv2.imshow("Rotate -45deg", rotated)
    cv2.waitKey(0)


def show_edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 30, 150)
    cv2.imshow("Canny Edge", edges)
    cv2.waitKey(0)


def show_contour(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)[1]
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = img.copy()
    cv2.drawContours(out, cnts, -1, (240, 0, 159), 2)
    cv2.putText(out, f"{len(cnts)} objects", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 0, 159), 2)
    cv2.imshow("Contours", out)
    cv2.waitKey(0)


MODES = {
    "resize":  show_resize,
    "rotate":  show_rotate,
    "edge":    show_edge,
    "contour": show_contour,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="image path")
    ap.add_argument("--mode", choices=list(MODES) + ["all"], default="all")
    args = ap.parse_args()

    img = cv2.imread(args.source)
    if img is None:
        print(f"[ERROR] Cannot read image: {args.source}")
        return

    if args.mode == "all":
        for fn in MODES.values():
            fn(img)
    else:
        MODES[args.mode](img)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
