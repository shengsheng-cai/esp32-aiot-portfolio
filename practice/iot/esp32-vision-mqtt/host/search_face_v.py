# SSD 人臉偵測 + threading + 追蹤 + 沒臉掃描
# 對應原始：search_face_v.py（myI2C → mySerial）
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
SEARCH_STEP = 2
MOVESKIPFLAME = 10
CONFIDENCE = 0.6

net = cv2.dnn.readNetFromCaffe('models/deploy.prototxt.txt', 'res10_300x300_ssd_iter_140000.caffemodel')

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
                blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                             (300, 300), (104.0, 177.0, 123.0))
                net.setInput(blob)
                detections = net.forward()
                diff = 0
                new_angle = nowAngle
                noface = 1
                if len(detections) > 0:
                    i = np.argmax(detections[0, 0, :, 2])
                    confidence = detections[0, 0, i, 2]
                    if confidence > CONFIDENCE:
                        noface = 0
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype('int')
                        face_x_center = (startX + endX) // 2
                        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                        text = '{:.2f}%'.format(confidence * 100)
                        y = startY - 10 if startY - 10 > 10 else startY + 10
                        cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
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
