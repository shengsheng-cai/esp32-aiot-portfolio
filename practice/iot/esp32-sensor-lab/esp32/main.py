import dht
import time
from machine import Pin
from umqtt.simple import MQTTClient

from i2c_lcd import LCD
from ntp_clock import connect_wifi, sync_ntp, time_str

WIFI_SSID     = 'your_ssid'
WIFI_PASSWORD = 'your_password'

MQTT_BROKER   = '192.168.1.100'
MQTT_PORT     = 1883
MQTT_CLIENT   = 'esp32-sensor-lab'
MQTT_TOPIC    = b'sensor/dht'

DHT_PIN  = 15
LED_PIN  = 2

dht11  = dht.DHT11(Pin(DHT_PIN))
led    = Pin(LED_PIN, Pin.OUT)
lcd    = LCD(sda=21, scl=22)


def read_dht():
    dht11.measure()
    return dht11.humidity(), dht11.temperature()


def main():
    wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    sync_ntp()

    client = MQTTClient(MQTT_CLIENT, MQTT_BROKER, port=MQTT_PORT)
    client.connect()

    lcd.show('ESP32 Sensor Lab', 'Starting...')
    time.sleep(1)

    i = 0
    while True:
        try:
            humi, temp = read_dht()
            now = time_str()
            msg = '{} H:{} T:{}'.format(now, humi, temp)

            client.publish(MQTT_TOPIC, msg)
            print(msg)

            lcd.show('H:{}%  T:{}C'.format(humi, temp), now[11:])

            led.value(0)
            time.sleep_ms(200)
            led.value(1)

            i += 1
            time.sleep(20)

        except OSError as e:
            print('DHT error:', e)
            lcd.show('DHT Error', str(e))
            time.sleep(5)


if __name__ == '__main__':
    main()
