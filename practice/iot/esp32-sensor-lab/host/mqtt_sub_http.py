# MQTT 訂閱 + HTTP 轉發 bridge
# 對應原始：mqtt_sub_http.py（移除 Docker 硬編碼 172.17.0.1 → 改讀設定）
# 用法：python mqtt_sub_http.py
# 收到 'humidity temperature' 格式訊息後，將溫度 *100 轉成整數發 HTTP GET

import paho.mqtt.client as mqtt
import requests

MQTT_BROKER  = '192.168.1.100'
MQTT_PORT    = 1883
MQTT_TOPIC   = 'sensor/dht'

HTTP_ENDPOINT = 'http://localhost:12321/'


def on_connect(client, userdata, flags, rc):
    print('Connected, rc:', rc)
    client.subscribe(MQTT_TOPIC)
    print('Subscribed:', MQTT_TOPIC)


def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip()
    print('[{}]: {}'.format(msg.topic, payload))
    parts = payload.split()
    if len(parts) >= 2:
        try:
            tmp_int = int(float(parts[1]) * 100)
            requests.get(HTTP_ENDPOINT + '?tmp=' + str(tmp_int), timeout=2)
        except Exception as e:
            print('HTTP forward error:', e)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_forever()
