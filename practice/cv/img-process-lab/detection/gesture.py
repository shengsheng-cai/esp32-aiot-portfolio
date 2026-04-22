import argparse
import os
import time
import urllib.request
import cv2
import mediapipe as mp

MODEL_PATH = "models/hand_landmarker.task"
MODEL_URL  = ("https://storage.googleapis.com/mediapipe-models/"
              "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")

GESTURE_CODES = {"Paper": 1, "Rock": 2, "Scissors": 3, "Unknown": 4}

CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),            # thumb
    (0,5),(5,6),(6,7),(7,8),            # index
    (5,9),(9,10),(10,11),(11,12),       # middle
    (9,13),(13,14),(14,15),(15,16),     # ring
    (13,17),(17,18),(18,19),(19,20),    # pinky
    (0,17),                              # palm
]


def download_model():
    if not os.path.exists(MODEL_PATH):
        print("[INFO] Downloading hand_landmarker.task ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print(f"[INFO] Saved to {MODEL_PATH}")


def get_gesture(landmarks):
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]

    fingers_open = []
    # thumb: tip-to-midpalm distance > knuckle-to-midpalm distance → extended
    if abs(landmarks[4].x - landmarks[9].x) > abs(landmarks[3].x - landmarks[9].x):
        fingers_open.append(1)
    else:
        fingers_open.append(0)

    for tip, pip in zip(finger_tips, finger_pips):
        fingers_open.append(1 if landmarks[tip].y < landmarks[pip].y else 0)

    total = sum(fingers_open)
    if total >= 4:
        return "Paper"
    if fingers_open[1] == 1 and fingers_open[2] == 1 and fingers_open[3] == 0 and fingers_open[4] == 0:
        return "Scissors"
    if total <= 1:
        return "Rock"
    return "Unknown"


def draw_hand(frame, landmarks):
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
    for pt in pts:
        cv2.circle(frame, pt, 4, (255, 0, 0), -1)


def main():
    download_model()

    ap = argparse.ArgumentParser()
    ap.add_argument("--source",   default="0", help="camera index or video path")
    ap.add_argument("--serial",   default=None, help="serial port (e.g. /dev/ttyUSB0)")
    ap.add_argument("--baud",     type=int,   default=9600)
    ap.add_argument("--interval", type=float, default=0.1, help="serial send interval (s)")
    args = ap.parse_args()

    ser = None
    if args.serial:
        import serial
        try:
            ser = serial.Serial(args.serial, args.baud, timeout=1)
            print(f"[INFO] Serial opened: {args.serial}")
        except Exception as e:
            print(f"[WARN] Serial open failed: {e}")

    HandLandmarker        = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    RunningMode           = mp.tasks.vision.RunningMode

    options = HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        running_mode=RunningMode.VIDEO,
    )

    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("Press q to quit.")

    last_send = 0
    t0 = time.time()

    with HandLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ts    = int((time.time() - t0) * 1000)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = landmarker.detect_for_video(mp_img, ts)

            h, w = frame.shape[:2]
            gesture, code = "No Hand", GESTURE_CODES["Unknown"]

            if result.hand_landmarks:
                lms = result.hand_landmarks[0]
                draw_hand(frame, lms)
                gesture = get_gesture(lms)
                code = GESTURE_CODES[gesture]
                wx = int(lms[0].x * w)
                wy = int(lms[0].y * h)
                cv2.putText(frame, f"{gesture} ({code})", (wx, wy - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            now = time.time()
            if ser and ser.is_open and now - last_send > args.interval:
                ser.write((str(code) + "\n").encode("utf-8"))
                last_send = now

            cv2.imshow("Hand Gesture", frame)
            if cv2.waitKey(5) & 0xFF == ord("q"):
                break

    if ser:
        ser.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
