# paho-mqtt 版伺服控制模組，對應 mySerial.py 的 UART 版本
# API 完全相同（r_h / mm_close），只需改 import 即可切換傳輸方式
# 對應原始：myMQTT.py（路徑修正，移除硬編碼 IP → 改讀 config.json）
# 依賴：pip install paho-mqtt
# ESP32 端需訂閱 config.json 中的 topic_servo 主題

import json
import random
import time
from paho.mqtt import client as mqtt_client

_conf_file = 'config.json'
with open(_conf_file) as f:
    _conf = json.load(f)

_servo_topic = _conf['topic_head'] + _conf['topic_servo']
_lcd_topic   = _conf['topic_head'] + _conf['topic_lcd']
_relay_topic = _conf['topic_head'] + _conf['topic_relay']

myMQTT = mqtt_client.Client(f'host-{random.randint(0, 9999)}')
myMQTT.connect(_conf['mqtt_broker'], _conf['mqtt_port'])
myMQTT.loop_start()


def r_h(angle=90, sleepSec=0.16, oldAngle=-1, frame_x_center=-1, face_x_center=-1):
    angle = max(0, min(180, int(angle)))
    myMQTT.publish(_servo_topic, str(angle), qos=2)
    time.sleep(sleepSec if 0 < sleepSec < 0.5 else 0.32)
    print('原角度={: >3}, 新角度={: >3}, sleep={:.2f}, frame_x_center={: >3}, faceX_center={: >3}'.format(
        oldAngle, angle, sleepSec, frame_x_center, face_x_center))
    return angle


def mm_close():
    myMQTT.loop_stop()
    myMQTT.disconnect()
    print('myMQTT.py : mm_close() 結束')


def lcd_show(name):
    myMQTT.publish(_lcd_topic, name)


def dev_On():
    myMQTT.publish(_relay_topic, 'H')


def dev_Off():
    myMQTT.publish(_relay_topic, 'L')
