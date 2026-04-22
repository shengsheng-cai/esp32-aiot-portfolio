import argparse
import time
import cv2
import numpy as np


def draw_bbox(img, bbox):
    points = bbox[0]
    for i in range(len(points)):
        pt1 = [int(v) for v in points[i]]
        pt2 = [int(v) for v in points[(i + 1) % 4]]
        cv2.line(img, pt1, pt2, (255, 0, 0), 3)


def decode_image(img, output):
    detector = cv2.QRCodeDetector()
    t = time.time()
    data, bbox, rectified = detector.detectAndDecode(img)
    print(f"[INFO] Time: {time.time() - t:.3f}s")
    if data:
        print(f"[INFO] Decoded: {data}")
        draw_bbox(img, bbox)
        cv2.imshow("QR Result", img)
        cv2.imshow("Rectified", np.uint8(rectified))
    else:
        print("[INFO] QR Code not detected")
        cv2.imshow("QR Result", img)
    if output:
        cv2.imwrite(output, img)
        print(f"[INFO] Saved: {output}")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def decode_camera(source, output):
    detector = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open source: {source}")
        return
    print("Press q to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        data, bbox, rectified = detector.detectAndDecode(frame)
        if data:
            draw_bbox(frame, bbox)
            cv2.putText(frame, data, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("QR", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    if output:
        cv2.imwrite(output, frame)
        print(f"[INFO] Saved: {output}")
    cap.release()
    cv2.destroyAllWindows()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0", help="image path or camera index")
    ap.add_argument("-o", "--output", default=None, help="output image path")
    args = ap.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source
    is_image = isinstance(source, str) and source.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))

    if is_image:
        img = cv2.imread(source)
        if img is None:
            print(f"[ERROR] Cannot read image: {source}")
            return
        decode_image(img, args.output)
    else:
        decode_camera(source, args.output)


if __name__ == "__main__":
    main()
