import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt


def show_gray(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    equ = cv2.equalizeHist(gray)
    cv2.imshow("Gray", gray)
    cv2.imshow("EqualizeHist", equ)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_normalize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Gray", gray)
    cv2.imshow("Normalize MINMAX 50-255", cv2.normalize(gray, None, 50, 255, cv2.NORM_MINMAX))
    cv2.imshow("Normalize INF alpha=50",  cv2.normalize(gray, None, 50,  255, cv2.NORM_INF))
    cv2.imshow("Normalize INF alpha=150", cv2.normalize(gray, None, 150, 255, cv2.NORM_INF))
    cv2.imshow("Normalize INF alpha=200", cv2.normalize(gray, None, 200, 255, cv2.NORM_INF))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_color(img):
    def equalize_yuv(src, channels):
        yuv = cv2.cvtColor(src, cv2.COLOR_BGR2YUV)
        for c in channels:
            yuv[:, :, c] = cv2.equalizeHist(yuv[:, :, c])
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    def equalize_ycrcb(src):
        ycrcb = cv2.cvtColor(src, cv2.COLOR_BGR2YCrCb)
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    cv2.imshow("Original",          img)
    cv2.imshow("YUV Y channel",     equalize_yuv(img, [0]))
    cv2.imshow("YUV Y+U channels",  equalize_yuv(img, [0, 1]))
    cv2.imshow("YCrCb Y channel",   equalize_ycrcb(img))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_plot(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)
    equ = cv2.equalizeHist(gray)

    for title, src in [("Grayscale Histogram", gray), ("EqualizeHist Histogram", equ)]:
        hist = cv2.calcHist([src], [0], None, [256], [0, 256])
        plt.figure()
        plt.title(title)
        plt.xlabel("Bins")
        plt.ylabel("# of Pixels")
        plt.plot(hist)
        plt.xlim([0, 256])

    plt.show()


MODES = {
    "gray":      show_gray,
    "normalize": show_normalize,
    "color":     show_color,
    "plot":      show_plot,
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


if __name__ == "__main__":
    main()
