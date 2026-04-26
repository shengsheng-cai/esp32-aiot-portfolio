# MQTT 訂閱測試工具 - 訂閱 ESP32 發布的 DHT11 資料並印出
# 對應原始：test-mqtt-訂閱.py
# 用法：python mqtt_sub.py
# ESP32 端 main.py 每 20 秒發布一次 'H:<humi> T:<temp>' 到 TOPIC
#
# QoS 說明：
#   0 = At most once  (fire and forget，可能遺失，適合感測資料)
#   1 = At least once (確保送達，可能重複)
#   2 = Exactly once  (確保且只送一次，適合計費系統)
#
# 公開測試 Broker（無需自架，測試用）：
#   broker.emqx.io:1883
#   test.mosquitto.org:1883
#   broker.hivemq.com:1883
#   broker.mqtt-dashboard.com:1883

import paho.mqtt.client as mqtt

MQTT_BROKER = '192.168.1.100'  # 改為上方公開 broker 可直接測試，不需 ESP32
MQTT_PORT   = 1883
MQTT_TOPIC  = 'sensor/dht'


def on_connect(client, userdata, flags, rc):
    print('Connected, rc:', rc)
    client.subscribe(MQTT_TOPIC)
    print('Subscribed:', MQTT_TOPIC)


def on_message(client, userdata, msg):
    print('[{}]: {}'.format(msg.topic, msg.payload.decode()))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_forever()
