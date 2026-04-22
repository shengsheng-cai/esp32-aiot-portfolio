import argparse
import cv2
import numpy as np


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA  = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB  = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (maxWidth, maxHeight))


def resize_h(img, height):
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w * height / h), height))


def find_doc_contour(edged):
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            return approx
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="image path")
    ap.add_argument("--mode", choices=["scan", "warp"], default="scan",
                    help="scan: perspective + binarize | warp: perspective only")
    ap.add_argument("-o", "--output", default=None, help="output image path")
    args = ap.parse_args()

    image = cv2.imread(args.source)
    if image is None:
        print(f"[ERROR] Cannot read image: {args.source}")
        return

    ratio = image.shape[0] / 500.0
    orig = image.copy()
    small = resize_h(image, 500)

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    print("STEP 1: Edge Detection")
    cv2.imshow("Image", small)
    cv2.imshow("Edged", edged)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    doc_cnt = find_doc_contour(edged)
    if doc_cnt is None:
        print("[ERROR] Could not find document contour.")
        return

    print("STEP 2: Find contours of paper")
    outline = small.copy()
    cv2.drawContours(outline, [doc_cnt], -1, (0, 255, 0), 2)
    cv2.imshow("Outline", outline)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    warped = four_point_transform(orig, doc_cnt.reshape(4, 2) * ratio)

    if args.mode == "scan":
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        warped = cv2.adaptiveThreshold(warped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 10)

    print("STEP 3: Apply perspective transform")
    cv2.imshow("Original", resize_h(orig, 650))
    cv2.imshow("Scanned", resize_h(warped, 650))
    cv2.waitKey(0)

    if args.output:
        cv2.imwrite(args.output, warped)
        print(f"[INFO] Saved: {args.output}")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
