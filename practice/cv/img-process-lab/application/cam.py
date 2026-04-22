import argparse
import cv2


def preview(source):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open source: {source}")
        return
    print("Press q to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Preview", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


def record(source, output):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open source: {source}")
        return
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(output, fourcc, fps, (w, h))
    print(f"Recording to {output}. Press q to stop.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        writer.write(frame)
        cv2.imshow("Recording", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    writer.release()
    cap.release()
    cv2.destroyAllWindows()
    print(f"Saved: {output}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["preview", "record"], default="preview")
    ap.add_argument("--source", default="0", help="camera index or video file path")
    ap.add_argument("-o", "--output", default="output.mp4")
    args = ap.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source

    if args.mode == "preview":
        preview(source)
    else:
        record(source, args.output)


if __name__ == "__main__":
    main()
