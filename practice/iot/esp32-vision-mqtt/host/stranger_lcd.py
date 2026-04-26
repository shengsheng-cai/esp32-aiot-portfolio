# MobileNetSSD 人物偵測 + face_recognition + 追蹤 + 錄影 + LCD/Relay
# 對應原始：i2c-fr/stranger_lcd.py（myI2C → mySerial）
# http://localhost:9090/a.mjpg

import cv2
import numpy as np
import time
import face_recognition

from myCam1 import myCam
from mySerial import mm_close, r_h, lcd_show, dev_On, dev_Off
from mjpg_server import start_mjpg_server

ADJ_DIFF = 80
ADJ_STEP = 1
SKIPFLAME = 1
SEARCH_STEP = 2
MOVESKIPFLAME = 1
CONFIDENCE = 0.6
PERSON_CLASS = 15

net = cv2.dnn.readNetFromCaffe('models/MobileNetSSD_deploy.prototxt', 'MobileNetSSD_deploy.caffemodel')

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

    Co_P_encoding = face_recognition.face_encodings(face_recognition.load_image_file('img/Co-p.jpg'))[0]
    chinese_encoding = face_recognition.face_encodings(face_recognition.load_image_file('img/chinese.jpg'))[0]
    english_encoding = face_recognition.face_encodings(face_recognition.load_image_file('img/english.jpg'))[0]
    known_face_encodings = [Co_P_encoding, chinese_encoding, english_encoding]
    known_face_names = ['Co-P', 'chinese', 'english']

    try:
        nowAngle = r_h()
        server = start_mjpg_server(9090, lambda: frm_HTTP, lambda: serving)

        vwriter = cv2.VideoWriter()
        fps = 30
        vwriter.open('output.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, my_cam.getProp_W_H(), True)

        count = 0
        mvCnt = 0
        while True:
            frame = my_cam.read()
            if count > 0:
                count -= 1
            else:
                (h, w) = frame.shape[:2]
                frame_x_center = w // 2

                blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843,
                                             (300, 300), (127.5, 127.5, 127.5))
                net.setInput(blob)
                detections = net.forward()

                diff = 0
                new_angle = nowAngle
                noface = 1

                if len(detections) > 0:
                    ixay = np.argwhere(detections[0, 0, :, 1] == PERSON_CLASS).flatten()
                    if len(ixay) > 0:
                        iix = np.argmax(np.take(detections[0, 0, :, 2], ixay))
                        i = ixay[iix]
                        confidence = detections[0, 0, i, 2]
                        if confidence > CONFIDENCE:
                            noface = 0
                            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                            (startX, startY, endX, endY) = box.astype('int')
                            face_x_center = (startX + endX) // 2

                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            face_locations = face_recognition.face_locations(rgb_frame)
                            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                            face_names = []
                            hasUnknown = len(face_locations)

                            for face_encoding in face_encodings:
                                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                                name = 'Unknown'
                                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                                best_match_index = np.argmin(face_distances)
                                if face_distances[best_match_index] < 0.6 and matches[best_match_index]:
                                    name = known_face_names[best_match_index]
                                    lcd_show(name)
                                    hasUnknown -= 1
                                face_names.append(name)

                            if len(face_locations):
                                for (top, right, bottom, left), name in zip(face_locations, face_names):
                                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                                    cv2.putText(frame, name, (left + 6, bottom - 6),
                                                cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)
                            else:
                                hasUnknown = 1
                                text = '{:.2f}%'.format(confidence * 100)
                                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                                y = startY - 10 if startY - 10 > 10 else startY + 10
                                cv2.putText(frame, text, (startX, y),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

                            dev_On()
                            if hasUnknown:
                                vwriter.write(frame)

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
                    dev_Off()
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
        vwriter.release()
        my_cam.release()
        server.socket.close()
        mm_close()
        print('程式結束')


if __name__ == '__main__':
    main()
