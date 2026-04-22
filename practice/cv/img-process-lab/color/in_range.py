import argparse
import time
import cv2
import numpy as np


COLORS = {
    "black":  ((0,   0,   0),   (180, 255,  45)),
    "gray":   ((0,   0,  46),   (180,  43, 220)),
    "white":  ((0,   0, 221),   (180,  30, 255)),
    "red":    ((0,  43,  46),   ( 10, 255, 255)),
    "orange": ((11, 43,  46),   ( 25, 255, 255)),
    "yellow": ((26, 43,  46),   ( 34, 255, 255)),
    "green":  ((35, 43,  46),   ( 77, 255, 255)),
    "cyan":   ((78, 43,  46),   ( 99, 255, 255)),
    "blue":   ((100, 43, 46),   (124, 255, 255)),
    "purple": ((125, 43, 46),   (155, 255, 255)),
}


def show_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    for name in ("red", "green", "blue"):
        lower, upper = (np.array(v) for v in COLORS[name])
        mask   = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(img, img, mask=mask)
        cv2.imshow(f"{name} mask",   mask)
        cv2.imshow(f"{name} result", result)
    cv2.imshow("Original", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_replace(img, bg):
    hsv  = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower, upper = np.array(COLORS["blue"][0]), np.array(COLORS["blue"][1])
    mask     = cv2.inRange(hsv, lower, upper)
    mask_inv = cv2.bitwise_not(mask)

    bg = cv2.resize(bg, (img.shape[1], img.shape[0]))
    fg      = cv2.bitwise_and(img, img, mask=mask_inv)
    bg_part = cv2.bitwise_and(bg,  bg,  mask=mask)
    out     = cv2.bitwise_or(fg, bg_part)

    cv2.imshow("Original", img)
    cv2.imshow("Mask",     mask)
    cv2.imshow("Result",   out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_cloak(source, min_area):
    cap = cv2.VideoCapture(source)
    time.sleep(2.0)
    for _ in range(30):
        _, background = cap.read()
    print("Press q to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        hsv     = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower, upper = np.array(COLORS["green"][0]), np.array(COLORS["green"][1])
        w_cloak = cv2.inRange(hsv, lower, upper)
        w_cloak = cv2.morphologyEx(w_cloak, cv2.MORPH_OPEN,  np.ones((3, 3), "uint8"))
        w_cloak = cv2.morphologyEx(w_cloak, cv2.MORPH_CLOSE, np.ones((3, 3), "uint8"))
        cnts, _ = cv2.findContours(w_cloak, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            mx = max(cnts, key=cv2.contourArea)
            w_cloak = np.zeros_like(w_cloak)
            if cv2.contourArea(mx) > min_area:
                cv2.drawContours(w_cloak, [mx], -1, 255, -1)
        b_cloak    = cv2.bitwise_not(w_cloak)
        nocloak    = cv2.bitwise_and(frame,      frame,      mask=b_cloak)
        cloak_bg   = cv2.bitwise_and(background, background, mask=w_cloak)
        cv2.imshow("Cloak", nocloak + cloak_bg)
        if cv2.waitKey(10) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0", help="image path or camera index")
    ap.add_argument("--mode", choices=["mask", "replace", "cloak"], default="mask")
    ap.add_argument("--bg", default=None, help="background image for replace mode")
    ap.add_argument("--min-area", type=int, default=2000,
                    help="min contour area for cloak mode (0 = no filter)")
    args = ap.parse_args()

    if args.mode == "cloak":
        source = int(args.source) if args.source.isdigit() else args.source
        show_cloak(source, args.min_area)
        return

    img = cv2.imread(args.source)
    if img is None:
        print(f"[ERROR] Cannot read image: {args.source}")
        return

    if args.mode == "mask":
        show_mask(img)
    elif args.mode == "replace":
        if not args.bg:
            print("[ERROR] --bg required for replace mode")
            return
        bg = cv2.imread(args.bg)
        if bg is None:
            print(f"[ERROR] Cannot read bg image: {args.bg}")
            return
        show_replace(img, bg)


if __name__ == "__main__":
    main()
