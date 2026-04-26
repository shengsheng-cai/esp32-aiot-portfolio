# HC 人臉偵測 + threading + resize 加速 + 追蹤 + 沒臉掃描
# 對應原始：search_face_hc_v4.py（myI2C → mySerial，haarcascades 路徑修正）
# http://localhost:9090/a.mjpg

import cv2
import numpy as np
import time

from myCam1 import myCam
from mySerial import mm_close, r_h
from mjpg_server import start_mjpg_server

ADJ_DIFF = 80
ADJ_STEP = 1
SKIPFLAME = 1
SEARCH_STEP = 1
MOVESKIPFLAME = 10

HC_FACE = 'haarcascades/haarcascade_frontalface_default.xml'
HC_EYE  = 'haarcascades/haarcascade_eye.xml'
face_cascade = cv2.CascadeClassifier(HC_FACE)
eyes_cascade = cv2.CascadeClassifier(HC_EYE)

nowAngle = -1
frame_x_center = 0
face_x_center = 0
my_cam = None
frm_HTTP = None
search_direction = 1
serving = True


def main():
    global frame_x_center, face_x_center, search_direction
    global my_cam, frm_HTTP, nowAngle, serving

    my_cam = myCam()
    try:
        nowAngle = r_h()
        server = start_mjpg_server(9090, lambda: frm_HTTP, lambda: serving)

        count = 0
        mvCnt = 0
        while True:
            frame = my_cam.read()
            if count > 0:
                count -= 1
            else:
                (h, w) = frame.shape[:2]
                frame_x_center = w // 2
                frame_gray = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                # resize 1/2 加速偵測，結果座標還原 ×2
                faces = face_cascade.detectMultiScale(cv2.resize(frame_gray, (w // 2, h // 2)))
                diff = 0
                new_angle = nowAngle
                noface = 1
                if len(faces) > 0:
                    (x, y, fw, fh) = faces[0]
                    x *= 2; y *= 2; fw *= 2; fh *= 2
                    center = (x + fw // 2, y + fh // 2)
                    face_x_center = center[0]
                    faceROI = frame_gray[y:y + fh, x:x + fw]
                    eyes = eyes_cascade.detectMultiScale(faceROI)
                    if len(eyes) >= 2:
                        noface = 0
                        frame = cv2.ellipse(frame, center, (fw // 2, fh // 2), 0, 0, 360, (255, 0, 255), 4)
                        for (x2, y2, w2, h2) in eyes:
                            eye_center = (x + x2 + w2 // 2, y + y2 + h2 // 2)
                            radius = int(round((w2 + h2) * 0.25))
                            frame = cv2.circle(frame, eye_center, radius, (255, 0, 0), 4)
                        if face_x_center > frame_x_center + ADJ_DIFF:
                            diff = face_x_center - frame_x_center
                            turnR = -1
                        elif frame_x_center > face_x_center + ADJ_DIFF:
                            diff = frame_x_center - face_x_center
                            turnR = 1
                        if diff > 0:
                            new_angle = max(0, min(180, nowAngle + turnR * ADJ_STEP))
                        if new_angle != nowAngle:
                            nowAngle = r_h(new_angle, 0.16, nowAngle, frame_x_center, face_x_center)
                            count = SKIPFLAME
                            mvCnt = MOVESKIPFLAME
                if noface:
                    if mvCnt > 0:
                        mvCnt -= 1
                    else:
                        new_angle = nowAngle + SEARCH_STEP * search_direction
                        if new_angle > 180:
                            new_angle = 180 - SEARCH_STEP
                            search_direction = -1
                        elif new_angle < 0:
                            new_angle = SEARCH_STEP
                            search_direction = 1
                        nowAngle = r_h(new_angle, 0.1, nowAngle)
            frm_HTTP = frame.copy()

    except KeyboardInterrupt:
        print('Ctrl-C 中斷')
    except Exception as e:
        print(f'Exception: {e}')
    finally:
        serving = False
        my_cam.release()
        server.socket.close()
        mm_close()
        print('程式結束')


if __name__ == '__main__':
    main()
