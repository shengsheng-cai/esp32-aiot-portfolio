import numpy as np
import cv2
from PIL import Image


def center_digit(gray: np.ndarray) -> np.ndarray:
    """找數字輪廓，裁切後置中到 28×28 畫布。"""
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return cv2.resize(thresh, (28, 28))

    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    digit = thresh[y : y + h, x : x + w]

    # 縮放到 20px 以內，保留長寬比
    scale = 20 / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    digit = cv2.resize(digit, (new_w, new_h))

    # 貼到 28×28 黑色畫布中央
    canvas = np.zeros((28, 28), dtype=np.uint8)
    top = (28 - new_h) // 2
    left = (28 - new_w) // 2
    canvas[top : top + new_h, left : left + new_w] = digit
    return canvas


def preprocess(pil_img: Image.Image) -> Image.Image:
    """PIL Image → MNIST 格式（28×28 灰階，黑底白字）。"""
    gray = np.array(pil_img.convert("L"))
    canvas = center_digit(gray)
    return Image.fromarray(canvas)
