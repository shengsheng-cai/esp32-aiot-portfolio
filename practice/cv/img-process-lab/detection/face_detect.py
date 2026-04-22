import argparse
import os
import urllib.request
import numpy as np
import cv2


MODEL_URL = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
DEFAULT_PROTOTXT = "models/deploy.prototxt"
DEFAULT_MODEL = "models/res10_300x300_ssd_iter_140000.caffemodel"


def download_if_missing(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(f"[INFO] Downloading {os.path.basename(path)}...")
        urllib.request.urlretrieve(url, path)


def detect(frame, net, confidence_thresh):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                  (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence < confidence_thresh:
            continue
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (x1, y1, x2, y2) = box.astype("int")
        label = f"{confidence * 100:.1f}%"
        y = y1 - 10 if y1 - 10 > 10 else y1 + 10
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, label, (x1, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    return frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0", help="image/video path or camera index (default: 0)")
    ap.add_argument("--prototxt", default=DEFAULT_PROTOTXT)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--confidence", type=float, default=0.5)
    ap.add_argument("-o", "--output", default=None, help="output image path (image mode only)")
    args = ap.parse_args()

    download_if_missing(MODEL_URL, args.model)

    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(args.prototxt, args.model)

    source = int(args.source) if args.source.isdigit() else args.source
    is_image = isinstance(source, str) and source.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))

    if is_image:
        frame = cv2.imread(source)
        if frame is None:
            print(f"[ERROR] Cannot read image: {source}")
            return
        result = detect(frame, net, args.confidence)
        cv2.imshow("Face Detection", result)
        if args.output:
            cv2.imwrite(args.output, result)
            print(f"[INFO] Saved: {args.output}")
        cv2.waitKey(0)
    else:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"[ERROR] Cannot open source: {source}")
            return
        print("Press q to quit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            result = detect(frame, net, args.confidence)
            cv2.imshow("Face Detection", result)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
