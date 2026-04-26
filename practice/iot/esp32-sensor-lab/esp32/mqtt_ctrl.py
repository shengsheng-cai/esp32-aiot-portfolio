# MQTT 訂閱 + 繼電器控制
# 對應原始：mqtt/ctl-r104（bash mosquitto_sub + GPIO → Python MicroPython）
# 訂閱 topic_relay，收到 'H' → 繼電器開，'L' → 繼電器關
# 同時持續發布 DHT11 溫濕度到 topic_dht

import dht
import time
from machine import Pin
from umqtt.simple import MQTTClient

import relay
from ntp_clock import connect_wifi

WIFI_SSID     = 'your_ssid'
WIFI_PASSWORD = 'your_password'

MQTT_BROKER   = '192.168.1.100'
MQTT_PORT     = 1883
MQTT_CLIENT   = 'esp32-ctrl'
TOPIC_DHT     = b'sensor/dht'
TOPIC_RELAY   = b'sensor/relay'

DHT_PIN = 15
dht11 = dht.DHT11(Pin(DHT_PIN))
led = Pin(2, Pin.OUT)
led.value(1)


def on_message(topic, msg):
    cmd = msg.decode().strip()
    if cmd == 'H':
        relay.on()
        print('relay ON')
    elif cmd == 'L':
        relay.off()
        print('relay OFF')


def main():
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)

    client = MQTTClient(MQTT_CLIENT, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(TOPIC_RELAY)
    print('subscribed:', TOPIC_RELAY)

    last_pub = 0
    while True:
        client.check_msg()
        now = time.time()
        if now - last_pub >= 20:
            try:
                dht11.measure()
                msg = '{} {}'.format(dht11.humidity(), dht11.temperature())
                client.publish(TOPIC_DHT, msg)
                print('pub:', msg)
                led.value(0)
                time.sleep_ms(200)
                led.value(1)
            except OSError as e:
                print('DHT error:', e)
            last_pub = now
        time.sleep_ms(100)


if __name__ == '__main__':
    main()
