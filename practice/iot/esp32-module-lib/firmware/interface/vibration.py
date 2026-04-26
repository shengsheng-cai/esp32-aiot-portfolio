"""
震動開關 (SW-18010P)
Interface - vibration

原始課程: 39.震動開闢
平台: ESP32 MicroPython

功能:
  讀取震動開關（常閉型），震動時觸發 LED 閃爍

SW-18010P 工作原理:
  - 常閉開關（無震動時內部彈簧接通，輸出 LOW）
  - 震動時彈簧與金屬腳脫離 → 輸出 HIGH
  - 類似按鈕，需串接限流電阻（100Ω~1kΩ）

注意：市售震動開關型號不同，常開/常閉特性也不同，
接線後先用 print(sensor.value()) 確認靜止狀態輸出。

硬體接線:
  震動開關一端 → GPIO 15（串接 10kΩ 電阻到 3.3V）
  震動開關另一端 → GND
  LED → GPIO 2（串接 220Ω）
"""

import time
from machine import Pin

VIBR_PIN = 15
LED_PIN  = 2

sensor = Pin(VIBR_PIN, Pin.IN)
led    = Pin(LED_PIN,  Pin.OUT)

print("Vibration sensor ready.")

while True:
    if sensor.value() == 1:   # 震動（彈簧脫離 → HIGH）
        led.value(1)
        print("Vibration detected!")
        time.sleep_ms(300)
        led.value(0)
    time.sleep_ms(10)
