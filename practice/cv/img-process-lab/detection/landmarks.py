import argparse
import os
import time
import urllib.request
import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance as dist

MODEL_PATH = "models/face_landmarker.task"
MODEL_URL  = ("https://storage.googleapis.com/mediapipe-models/"
              "face_landmarker/face_landmarker/float16/1/face_landmarker.task")

LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]
EYE_AR_THRESH        = 0.25
EYE_AR_CONSEC_FRAMES = 3


def download_model():
    if not os.path.exists(MODEL_PATH):
        print("[INFO] Downloading face_landmarker.task ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print(f"[INFO] Saved to {MODEL_PATH}")


def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)


def get_eye_pts(landmarks, idxs, w, h):
    return np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in idxs])


def run_detector(frame, landmarker, timestamp_ms, video_mode):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    if video_mode:
        return landmarker.detect_for_video(mp_img, timestamp_ms)
    return landmarker.detect(mp_img)


def draw_landmarks(frame, result, h, w):
    for face in result.face_landmarks:
        for lm in face:
            cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 1, (0, 255, 0), -1)
    return frame


def calc_blinks(frame, result, h, w, counter, total):
    if result.face_landmarks:
        lms = result.face_landmarks[0]
        left  = get_eye_pts(lms, LEFT_EYE,  w, h)
        right = get_eye_pts(lms, RIGHT_EYE, w, h)
        ear = (eye_aspect_ratio(left) + eye_aspect_ratio(right)) / 2.0
        if ear < EYE_AR_THRESH:
            counter += 1
        elif counter >= EYE_AR_CONSEC_FRAMES:
            total += 1
            counter = 0
        else:
            counter = 0
        cv2.putText(frame, f"Blinks: {total}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    return frame, counter, total


def main():
    download_model()

    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0", help="image/video path or camera index")
    ap.add_argument("--mode", choices=["landmarks", "blinks"], default="landmarks")
    args = ap.parse_args()

    source    = int(args.source) if args.source.isdigit() else args.source
    is_image  = isinstance(source, str) and source.lower().endswith(
                    (".jpg", ".jpeg", ".png", ".bmp"))
    video_mode = not is_image

    FaceLandmarker        = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    RunningMode           = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
        num_faces=5,
        min_face_detection_confidence=0.5,
        running_mode=RunningMode.VIDEO if video_mode else RunningMode.IMAGE,
    )

    with FaceLandmarker.create_from_options(options) as landmarker:
        if is_image:
            frame = cv2.imread(source)
            if frame is None:
                print(f"[ERROR] Cannot read: {source}")
                return
            h, w = frame.shape[:2]
            result = run_detector(frame, landmarker, 0, False)
            if args.mode == "landmarks":
                frame = draw_landmarks(frame, result, h, w)
            else:
                frame, _, _ = calc_blinks(frame, result, h, w, 0, 0)
            cv2.namedWindow(args.mode.capitalize(), cv2.WINDOW_NORMAL)
            cv2.imshow(args.mode.capitalize(), frame)
            cv2.waitKey(0)
        else:
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                print(f"[ERROR] Cannot open: {source}")
                return
            print("Press q to quit.")
            counter, total = 0, 0
            t0 = time.time()
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                h, w = frame.shape[:2]
                ts = int((time.time() - t0) * 1000)
                result = run_detector(frame, landmarker, ts, True)
                if args.mode == "landmarks":
                    frame = draw_landmarks(frame, result, h, w)
                else:
                    frame, counter, total = calc_blinks(frame, result, h, w, counter, total)
                cv2.imshow(args.mode.capitalize(), frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
