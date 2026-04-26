# esp32-sensor-lab

ESP32 MicroPython 基礎硬體控制學習實驗室。

課程來源（泰山職訓局 2025~2026）將 Raspberry Pi 範例移植至 ESP32，全程 MicroPython，不使用 Arduino/C++。

---

## 模組

| 模組 | 檔案 | 硬體 | 功能 |
|------|------|------|------|
| I2C LCD | `i2c_lcd.py` | LCD 1602 + PCF8574（addr 0x27） | 字元顯示，不依賴外部 library |
| PWM 舵機 | `servo.py` | SG90（GPIO 13） | 0~180° 角度控制、掃描 |
| LED 呼吸燈 | `led_breath.py` | LED（GPIO 2） | PWM 漸亮漸暗 |
| 蜂鳴器 | `buzzer.py` | 被動蜂鳴器（GPIO 12） | Do Re Mi 音階，可擴充音符 |
| NTP 時鐘 | `ntp_clock.py` | — | WiFi 對時，UTC+8，取代外接 RTC 晶片 |
| 主程式 | `main.py` | DHT11（GPIO 15） | DHT 讀取 → LCD 顯示 → MQTT pub |

---

## 接線

```
ESP32 GPIO 21 → I2C SDA (LCD PCF8574)
ESP32 GPIO 22 → I2C SCL (LCD PCF8574)
ESP32 GPIO 13 → SG90 Signal
ESP32 GPIO 15 → DHT11 Data
ESP32 GPIO 12 → 被動蜂鳴器正極
ESP32 GPIO 2  → LED（板載 LED）
3.3V / GND   → 各模組供電
```

> SG90 建議外接 5V 供電，訊號線接 3.3V 可驅動。

---

## 快速開始

**1. 燒錄 MicroPython firmware**

至 [micropython.org/download/ESP32_GENERIC](https://micropython.org/download/ESP32_GENERIC/) 下載最新版，燒錄至 ESP32。

**2. 修改 WiFi 與 MQTT 設定**

編輯 `esp32/main.py`：
```python
WIFI_SSID     = 'your_ssid'
WIFI_PASSWORD = 'your_password'
MQTT_BROKER   = '192.168.1.100'
```

**3. 啟動 MQTT Broker（選用）**

```bash
docker run -d -p 1883:1883 eclipse-mosquitto
```

**4. 上傳程式至 ESP32**

使用 [Thonny](https://thonny.org/) 或 `mpremote`：
```bash
pip install mpremote
mpremote connect /dev/ttyUSB0 cp esp32/ :
```

**5. 執行**

`main.py` 放到 ESP32 根目錄後重開機自動執行，或在 Thonny 手動 Run。

---

## 各模組單獨測試

```python
# I2C LCD
from i2c_lcd import LCD
lcd = LCD()
lcd.show('Hello', 'ESP32!')

# SG90 舵機
from servo import Servo
s = Servo(pin=13)
s.sweep()

# LED 呼吸燈
from led_breath import LedBreath
led = LedBreath(pin=2)
led.breath()

# 蜂鳴器
from buzzer import Buzzer
bz = Buzzer(pin=12)
bz.do_re_mi()

# NTP 時鐘
from ntp_clock import connect_wifi, sync_ntp, time_str
connect_wifi('ssid', 'password')
sync_ntp()
print(time_str())
```

---

## 技術棧

- **硬體**：ESP32（38-pin 或相容板）
- **語言**：MicroPython
- **通訊**：WiFi + MQTT（umqtt.simple，MicroPython 內建）
- **時間**：NTP 同步（ntptime，取代 DS1302 外接 RTC）
