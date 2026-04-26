"""
MQTT 訂閱控制 Servo / Relay / LCD
networking - mqtt_control

原始課程: linux-iot/iot-hardware/ai-rpi-i2c
平台: ESP32 MicroPython

功能:
  訂閱 MQTT topic，依訊息控制：
    servo  → SG90 舵機角度（0〜180）
    relay  → 繼電器開/關（H/L）
    LCD    → I2C LCD 顯示文字（需外接模組）

場景:
  RPi / 後端發布 MQTT 指令 → ESP32 接收執行
  是 FastAPI 後端 + MQTT broker 架構的末端執行節點

MQTT topic 結構:
  {topic_head}/servo  → 角度整數字串，如 "90"
  {topic_head}/relay  → "H"（開）或 "L"（關）
  {topic_head}/LCD    → 任意字串（顯示於 LCD）

設定方式:
  修改 CONFIG_FILE（/config.json）或在首次執行時自動建立預設值
  參考 core-skills/flash_storage.py 的 load_config()

Servo PWM 計算:
  SG90: 50Hz，脈寬 0.5ms〜2.4ms → 0°〜180°
  duty_u16 範圍: 1638（0°）〜 7864（180°）

硬體接線:
  Servo 訊號線  → GPIO 4
  繼電器 IN     → GPIO 12
  I2C LCD SDA   → GPIO 21（選配）
  I2C LCD SCL   → GPIO 22（選配）
"""

import time
import network
import ntptime
from machine import Pin, PWM
from umqtt.robust import MQTTClient

# ── 設定（優先從 config.json 讀取）────────────────────────
try:
    import json
    with open("/config.json") as f:
        _cfg = json.load(f)
except OSError:
    _cfg = {}

WIFI_SSID     = _cfg.get("wifi_ssid",     "your_ssid")
WIFI_PASSWORD = _cfg.get("wifi_password", "your_password")
MQTT_BROKER   = _cfg.get("mqtt_broker",   "192.168.1.100")
MQTT_PORT     = _cfg.get("mqtt_port",     1883)
CLIENT_ID     = _cfg.get("mqtt_client_id","esp32-ctrl-01")
TOPIC_HEAD    = _cfg.get("topic_head",    "home/esp32").encode()

# ── 腳位 ──────────────────────────────────────────────────
SERVO_PIN = 4
RELAY_PIN = 12
LED_PIN   = 2     # 內建 LED，用於狀態指示

# ── Servo（SG90 50Hz PWM）────────────────────────────────
_D_MIN  = 1638    # 0°  對應 duty_u16
_D_SPAN = 7864 - _D_MIN   # 180° 對應的 span

servo_pwm = PWM(Pin(SERVO_PIN), freq=50)

def servo_write(angle: int):
    """設定 Servo 角度（0〜180）"""
    angle = max(0, min(180, angle))
    servo_pwm.duty_u16(_D_MIN + _D_SPAN * angle // 180)


# ── 繼電器 ────────────────────────────────────────────────
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0)   # 預設關閉


# ── I2C LCD（選配，未連接時不報錯）──────────────────────
_lcd = None

def _init_lcd():
    global _lcd
    try:
        from machine import I2C
        from machine_i2c_lcd import I2cLcd
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400_000)
        _lcd = I2cLcd(i2c, 0x27, 2, 16)
        _lcd.backlight_on()
        print("LCD init OK")
    except Exception as e:
        print("LCD not available:", e)


def lcd_show(text: str):
    if _lcd:
        _lcd.clear()
        _lcd.move_to(0, 0)
        _lcd.putstr(text[:32])   # 2行 16字元


# ── MQTT callback ────────────────────────────────────────
topic_servo = TOPIC_HEAD + b"/servo"
topic_relay = TOPIC_HEAD + b"/relay"
topic_lcd   = TOPIC_HEAD + b"/LCD"


def on_message(topic, msg):
    print("MQTT:", topic, msg)
    if topic == topic_servo:
        try:
            angle = int(msg)
            servo_write(angle)
            print("Servo →", angle, "°")
        except ValueError:
            print("Invalid angle:", msg)
    elif topic == topic_relay:
        if msg == b"H":
            relay.value(1)
            print("Relay ON")
        elif msg == b"L":
            relay.value(0)
            print("Relay OFF")
    elif topic == topic_lcd:
        lcd_show(msg.decode())


# ── NTP 對時（UTC+8）────────────────────────────────────
def _sync_time():
    ntptime.host = "tw.pool.ntp.org"
    try:
        ntptime.settime()
        cst = time.localtime(time.mktime(time.localtime()) + 28800)
        print("Time: {0}/{1:02d}/{2:02d} {3:02d}:{4:02d}:{5:02d}".format(*cst))
    except Exception as e:
        print("NTP sync failed:", e)


# ── WiFi 連線 ─────────────────────────────────────────────
def _connect_wifi():
    led = Pin(LED_PIN, Pin.OUT)
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)
        print("Connecting to WiFi...")
        for i in range(20):
            if wifi.isconnected():
                break
            led.value(i % 2)
            time.sleep(1)
    if wifi.isconnected():
        led.value(1)
        print("WiFi OK:", wifi.ifconfig())
        return True
    print("WiFi failed")
    return False


# ── 主程式 ────────────────────────────────────────────────
def main():
    _init_lcd()
    if not _connect_wifi():
        return

    _sync_time()

    client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, keepalive=65535)
    client.set_callback(on_message)
    client.connect(clean_session=False)
    client.subscribe(TOPIC_HEAD + b"/#")
    print("MQTT connected, subscribed:", TOPIC_HEAD)

    while True:
        client.check_msg()
        time.sleep_ms(50)


main()
