"""
觸摸感測器
Interface - touch_sensor

原始課程: 6.ESP32內建觸摸感測器與觸控模組 / 40.觸摸感測器 touch_sensor
平台: ESP32 MicroPython

功能:
  範例 1: ESP32 內建電容觸摸（TouchPad）
  範例 2: TTP223 觸摸模組（數位輸入）

ESP32 內建觸摸腳位（10 個）:
  T0=GPIO4, T2=GPIO2, T3=GPIO15, T4=GPIO13, T5=GPIO12
  T6=GPIO14, T7=GPIO27, T8=GPIO33, T9=GPIO32

TouchPad 讀值：越低代表越確定被觸摸
通常空閒值約 500~800，觸摸後降至 100 以下（依環境不同）

TTP223 模組:
  點動模式（預設）：觸摸時 OUT=HIGH，放開後 LOW
  輸出為數位信號，直接用 digitalRead 讀取

硬體接線（範例 1 - 內建觸摸）:
  T8 = GPIO 33（接觸摸片或直接用手指靠近）

硬體接線（範例 2 - TTP223 模組）:
  TTP223 OUT → GPIO 33
  TTP223 VCC → 3.3V
  TTP223 GND → GND
  LED         → GPIO 17（串接 220Ω）
"""

import time
from machine import Pin, TouchPad

TOUCH_PIN    = 33
LED_PIN      = 17
TOUCH_THRESH = 200   # 低於此值視為觸摸（依實際環境調整）


# ── 範例 1：ESP32 內建電容觸摸 ────────────────────────────────
def internal_touch_demo():
    """
    讀取 ESP32 內建電容觸摸值（GPIO 33 = T8）
    印出數值，並在觸摸時點亮 LED
    """
    tp  = TouchPad(Pin(TOUCH_PIN))
    led = Pin(LED_PIN, Pin.OUT)

    print("Internal touch demo. Touch GPIO {} to trigger.".format(TOUCH_PIN))

    while True:
        val = tp.read()
        touched = val < TOUCH_THRESH
        led.value(touched)
        print("Touch val: {:4d}  {}".format(val, "TOUCHED" if touched else ""))
        time.sleep_ms(200)


# ── 範例 2：TTP223 觸摸模組 ───────────────────────────────────
def ttp223_demo():
    """
    TTP223 數位觸摸模組
    觸摸時 OUT=HIGH → 點亮 LED
    """
    sensor = Pin(TOUCH_PIN, Pin.IN)
    led    = Pin(LED_PIN, Pin.OUT)

    print("TTP223 demo. Touch sensor to toggle LED.")

    prev = 0
    while True:
        state = sensor.value()
        led.value(state)

        if state != prev:
            print("Sensor:", "touched" if state else "released")
            prev = state

        time.sleep_ms(50)


# ── 主程式（選擇一種模式）────────────────────────────────────
# internal_touch_demo()
ttp223_demo()
