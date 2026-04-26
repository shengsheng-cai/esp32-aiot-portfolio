"""
MQTT 發布感測器資料
networking - mqtt_publish

原始課程: linux-iot/iot-hardware/ai-rpi-i2c (dht_mqtt.py / main.py)
平台: ESP32 MicroPython

功能:
  WiFi 連線 → NTP 對時 → 定時讀取感測器 → MQTT publish
  與 mqtt_control.py 互補（一個 publish、一個 subscribe）

MQTT topic 設計:
  {topic_head}/temperature  → 溫度（°C）
  {topic_head}/humidity     → 濕度（%）
  或合併成單一 topic，payload 為 "humidity temperature"

設定方式:
  修改 /config.json，首次執行自動建立預設值
  參考 core-skills/flash_storage.py 的 load_config()

錯誤處理:
  WiFi 斷線 → 自動重連
  DHT 讀取失敗 → 跳過本次，繼續下一輪
  MQTT publish 失敗 → 印 log，不中斷主迴圈
  LED 閃爍指示運行狀態（GPIO 2，內建 LED）

硬體接線:
  DHT11 DATA → GPIO 15（可換 DHT22，改 dht.DHT22）
"""

import dht
import time
import network
import ntptime
from machine import Pin
from umqtt.robust import MQTTClient

# ── 設定（從 config.json 讀取）────────────────────────────
try:
    import json
    with open("/config.json") as f:
        _cfg = json.load(f)
except OSError:
    _cfg = {}

WIFI_SSID     = _cfg.get("wifi_ssid",     "your_ssid")
WIFI_PASSWORD = _cfg.get("wifi_password", "your_password")
MQTT_BROKER   = _cfg.get("mqtt_broker",   "192.168.1.100")
MQTT_PORT     = int(_cfg.get("mqtt_port", 1883))
CLIENT_ID     = _cfg.get("mqtt_client_id","esp32-pub-01")
TOPIC_HEAD    = _cfg.get("topic_head",    "home/esp32").encode()

PUBLISH_SEC   = 20    # 每幾秒發布一次

# ── 硬體 ──────────────────────────────────────────────────
DHT_PIN = 15
LED_PIN = 2

sensor = dht.DHT11(Pin(DHT_PIN))   # DHT22 請改 dht.DHT22
led    = Pin(LED_PIN, Pin.OUT)


# ── NTP 對時（UTC+8）────────────────────────────────────
def _sync_time():
    ntptime.host = "tw.pool.ntp.org"
    try:
        ntptime.settime()
        t = time.localtime(time.mktime(time.localtime()) + 28800)
        print("Time: {0}/{1:02d}/{2:02d} {3:02d}:{4:02d}:{5:02d}".format(*t))
    except Exception as e:
        print("NTP sync failed:", e)


def _now_str() -> str:
    t = time.localtime(time.mktime(time.localtime()) + 28800)
    return "{0}/{1:02d}/{2:02d} {3:02d}:{4:02d}:{5:02d}".format(*t)


# ── WiFi 連線 ─────────────────────────────────────────────
def _connect_wifi() -> bool:
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if wifi.isconnected():
        return True
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting WiFi...")
    for _ in range(20):
        if wifi.isconnected():
            print("WiFi OK:", wifi.ifconfig())
            return True
        led.value(not led.value())
        time.sleep(1)
    print("WiFi failed")
    return False


# ── 主程式 ────────────────────────────────────────────────
def main():
    if not _connect_wifi():
        return

    _sync_time()

    client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, keepalive=65535)
    client.connect(clean_session=False)
    print("MQTT connected →", MQTT_BROKER)
    led.value(1)

    topic = TOPIC_HEAD + b"/dht"

    while True:
        # ── WiFi 斷線重連 ──
        wifi = network.WLAN(network.STA_IF)
        if not wifi.isconnected():
            print("WiFi lost, reconnecting...")
            led.value(0)
            if not _connect_wifi():
                time.sleep(10)
                continue
            client.connect(clean_session=False)

        # ── 讀取感測器 ──
        try:
            sensor.measure()
            humidity    = sensor.humidity()
            temperature = sensor.temperature()
        except Exception as e:
            print("DHT error:", e)
            time.sleep(2)
            continue

        # ── 發布 ──
        payload = "{} {}".format(humidity, temperature)
        try:
            client.publish(topic, payload)
            print("{} publish: {}".format(_now_str(), payload))
        except Exception as e:
            print("MQTT publish error:", e)

        # ── 等待下次發布（LED 閃爍指示運行中）──
        for _ in range(PUBLISH_SEC):
            led.value(not led.value())
            time.sleep(1)


main()
