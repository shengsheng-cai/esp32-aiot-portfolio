import cv2
import threading
import time


class myCam:
    def __init__(self, cam_index=0):
        self.errCntMax = 5
        self.frame = None
        self.retval = False
        self.reading = False
        self.errCnt = 0
        self.fmID = 0
        self.O_ID = 0

        print(f'Try: cv2.VideoCapture({cam_index})')
        self.capture = cv2.VideoCapture(cam_index)
        if not self.capture.isOpened():
            raise RuntimeError(f'無法開啟攝影機 index={cam_index}')

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        print('鏡頭開了！')

        self.reading = True
        t = threading.Thread(target=self.readloop, daemon=True)
        t.start()

    def readloop(self):
        try:
            while self.reading:
                self.retval, self.frame = self.capture.read()
                if self.retval:
                    self.errCnt = 0
                    self.fmID += 1
                else:
                    self.errCnt += 1
                    if self.errCnt >= self.errCntMax:
                        raise RuntimeError('capture.read() 連續失敗')
        except RuntimeError as e:
            print(f'myCam1.py : {e}')
            raise SystemExit
        finally:
            self.capture.release()
            print('鏡頭關閉')

    def read(self):
        while self.O_ID == self.fmID:
            if self.errCnt >= self.errCntMax:
                raise SystemExit('鏡頭沒讀到畫面')
            time.sleep(0.05)
        self.O_ID = self.fmID
        return self.frame.copy()

    def getProp_W_H(self):
        return (int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def release(self):
        self.reading = False
