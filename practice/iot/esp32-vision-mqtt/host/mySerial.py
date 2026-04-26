import serial
import threading
import time

# 對應 myI2C.py：原本透過 smbus2 I2C → Arduino slave 控制舵機
# 改為 UART Serial → ESP32 MicroPython (servo_uart.py)
# 使用前請確認 PORT（Mac: /dev/cu.usbserial-xxxx，Linux: /dev/ttyUSB0）

PORT = '/dev/cu.usbserial-0001'
BAUD = 9600

_ser = None
_lock = threading.Lock()


def _get_ser():
    global _ser
    if _ser is None or not _ser.is_open:
        _ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(1.5)
    return _ser


def _write_line(line):
    ser = _get_ser()
    ser.write((line + '\n').encode())


def r_h(angle=90, sleepSec=0.16, oldAngle=-1, frame_x_center=-1, face_x_center=-1):
    angle = max(0, min(180, int(angle)))
    with _lock:
        _write_line(str(angle))
    time.sleep(sleepSec if 0 < sleepSec < 0.5 else 0.32)
    print('原角度={: >3}, 新角度={: >3}, sleep={:.2f}, frame_x_center={: >3}, faceX_center={: >3}'.format(
        oldAngle, angle, sleepSec, frame_x_center, face_x_center))
    return angle


def lcd_show(name):
    text = str(name).strip()
    if not text:
        return
    with _lock:
        _write_line(f'LCD:{text}')


def dev_On():
    with _lock:
        _write_line('RELAY:H')


def dev_Off():
    with _lock:
        _write_line('RELAY:L')


def mm_close():
    global _ser
    if _ser and _ser.is_open:
        _ser.close()
    print(f'mySerial.py : mm_close() 結束')
