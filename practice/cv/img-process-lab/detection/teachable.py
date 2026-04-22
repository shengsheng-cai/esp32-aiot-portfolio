import argparse
import cv2
import numpy as np


def load_model_and_labels(model_path, labels_path):
    from tensorflow import keras
    model = keras.models.load_model(model_path, compile=False)
    class_names = open(labels_path, "r", encoding="utf-8").readlines()
    return model, class_names


def preprocess(frame):
    h, w = frame.shape[:2]
    min_dim = min(h, w)
    sx = (w - min_dim) // 2
    sy = (h - min_dim) // 2
    cropped = frame[sy:sy + min_dim, sx:sx + min_dim]
    rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (224, 224), interpolation=cv2.INTER_AREA)
    inp = np.asarray(resized, dtype=np.float32).reshape(1, 224, 224, 3)
    return (inp / 127.5) - 1, (sx, sy, min_dim)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0", help="camera index or video path")
    ap.add_argument("--model",  default="keras_Model.h5", help="Keras model path (.h5)")
    ap.add_argument("--labels", default="labels.txt",     help="labels file path")
    ap.add_argument("--flip",   action="store_true",      help="flip frame horizontally")
    args = ap.parse_args()

    np.set_printoptions(suppress=True)
    print("[INFO] Loading model...")
    model, class_names = load_model_and_labels(args.model, args.labels)
    print("[INFO] Model loaded.")

    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("Press q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if args.flip:
            frame = cv2.flip(frame, 1)

        display = frame.copy()
        inp, (sx, sy, dim) = preprocess(frame)

        prediction = model.predict(inp, verbose=0)
        idx = np.argmax(prediction)
        label = class_names[idx].strip()[2:]
        confidence = prediction[0][idx]

        cv2.rectangle(display, (sx, sy), (sx + dim, sy + dim), (255, 0, 0), 2)
        cv2.putText(display, f"{label}: {int(confidence * 100)}%", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("Teachable Machine", display)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
