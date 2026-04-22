import argparse
import cv2
import numpy as np


KERNELS = {
    "blur":      np.array([[0.0625, 0.125, 0.0625],
                            [0.125,  0.25,  0.125],
                            [0.0625, 0.125, 0.0625]], dtype="float32"),
    "edge":      np.array([[-1, -1, -1], [-1,  8, -1], [-1, -1, -1]], dtype="float32"),
    "emboss":    np.array([[-2, -1,  0], [-1,  1,  1], [ 0,  1,  2]], dtype="float32"),
    "sharpen":   np.array([[ 0, -1,  0], [-1,  5, -1], [ 0, -1,  0]], dtype="float32"),
    "laplacian": np.array([[ 0,  1,  0], [ 1, -4,  1], [ 0,  1,  0]], dtype="float32"),
}

SOBEL_DIR_KERNELS = {
    "top":    np.array([[ 1,  2,  1], [ 0,  0,  0], [-1, -2, -1]], dtype="float32"),
    "bottom": np.array([[-1, -2, -1], [ 0,  0,  0], [ 1,  2,  1]], dtype="float32"),
    "right":  np.array([[-1,  0,  1], [-2,  0,  2], [-1,  0,  1]], dtype="float32"),
    "left":   np.array([[ 1,  0, -1], [ 2,  0, -2], [ 1,  0,  1]], dtype="float32"),
}


def show_blur(img):
    cv2.imshow("Original",              img)
    cv2.imshow("Blur 7x7",              cv2.blur(img, (7, 7)))
    cv2.imshow("Blur 1x47 (H)",         cv2.blur(img, (1, 47)))
    cv2.imshow("Blur 47x1 (V)",         cv2.blur(img, (47, 1)))
    cv2.imshow("Gaussian 11x11",        cv2.GaussianBlur(img, (11, 11), 0))
    cv2.imshow("Gaussian 5x41 (H)",     cv2.GaussianBlur(img, (5, 41), 0))
    cv2.imshow("Gaussian 41x5 (V)",     cv2.GaussianBlur(img, (41, 5), 0))
    cv2.imshow("Median 5",              cv2.medianBlur(img, 5))
    cv2.imshow("Median 7",              cv2.medianBlur(img, 7))
    cv2.imshow("Median 9",              cv2.medianBlur(img, 9))
    cv2.imshow("Box 7x7 normalized",    cv2.boxFilter(img, -1, (7, 7), normalize=True))
    cv2.imshow("Box 7x7 unnormalized",  cv2.boxFilter(img, -1, (7, 7), normalize=False))
    cv2.imshow("Bilateral",             cv2.bilateralFilter(img, 16, 50, 16))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_filter2d(img, kernel_name):
    kernel = KERNELS[kernel_name]
    result = cv2.filter2D(img, -1, kernel)
    out = np.hstack((img, result))
    cv2.imshow(f"filter2D [{kernel_name}]  Original | Result", out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_sobel(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    depth = cv2.CV_16S
    grad_x = cv2.Sobel(gray, depth, 1, 0, ksize=7)
    grad_y = cv2.Sobel(gray, depth, 0, 1, ksize=7)
    abs_x  = cv2.convertScaleAbs(grad_x)
    abs_y  = cv2.convertScaleAbs(grad_y)
    sobel  = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)

    _, thresh = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    knl_v = np.ones((3, 1), np.uint8)
    morph = cv2.dilate(thresh, knl_v, iterations=2)
    morph = cv2.erode(morph,  knl_v, iterations=4)
    morph = cv2.dilate(morph, knl_v, iterations=2)
    morph = cv2.erode(morph,  knl_v, iterations=1)
    morph = cv2.dilate(morph, knl_v, iterations=2)

    cv2.imshow("Sobel",  sobel)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Morph",  morph)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    results = [cv2.filter2D(gray, -1, k) for k in SOBEL_DIR_KERNELS.values()]
    out = np.hstack([gray] + results)
    cv2.imshow("Sobel Dir  Gray | Top | Bottom | Right | Left", out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_canny(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    pairs = [(10, 30), (30, 70), (50, 120), (80, 170)]
    for lo, hi in pairs:
        cv2.imshow(f"Canny {lo}/{hi}", cv2.Canny(gray, lo, hi))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


MODES = {
    "blur":  show_blur,
    "sobel": show_sobel,
    "canny": show_canny,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="image path")
    ap.add_argument("--mode", choices=["blur", "filter2d", "sobel", "canny", "all"], default="all")
    ap.add_argument("--kernel", choices=list(KERNELS), default="edge",
                    help="kernel type for filter2d mode")
    args = ap.parse_args()

    img = cv2.imread(args.source)
    if img is None:
        print(f"[ERROR] Cannot read image: {args.source}")
        return

    if args.mode == "all":
        show_blur(img)
        for k in KERNELS:
            show_filter2d(img, k)
        show_sobel(img)
        show_canny(img)
    elif args.mode == "filter2d":
        show_filter2d(img, args.kernel)
    else:
        MODES[args.mode](img)


if __name__ == "__main__":
    main()
