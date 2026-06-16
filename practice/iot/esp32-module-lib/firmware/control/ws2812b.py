"""
WS2812B RGB LED 燈帶控制
Control - ws2812b

功能:
  跑馬燈、彩虹燈效果
  MicroPython 內建 neopixel 模組，不需額外函式庫

硬體注意事項:
  - 燈帶使用 5V 供電，每顆 LED 全亮約 50mA
  - 30 顆全亮約需 1.5A，建議外接電源
  - 少量 LED（8 顆以內）可由 USB 供電

硬體接線:
  燈帶 DIN → GPIO 2
  燈帶 VCC → 5V
  燈帶 GND → GND
"""

import time
from machine import Pin
from neopixel import NeoPixel

LED_PIN = 2
LED_COUNT = 8

np = NeoPixel(Pin(LED_PIN), LED_COUNT)


def clear():
    for i in range(LED_COUNT):
        np[i] = (0, 0, 0)
    np.write()


def set_brightness(color: tuple, brightness: float) -> tuple:
    """調整顏色亮度，brightness: 0.0~1.0"""
    return tuple(int(c * brightness) for c in color)


# ── 跑馬燈 ────────────────────────────────────────────────────
def chase(color=(255, 0, 0), delay_ms=100):
    for i in range(LED_COUNT):
        clear()
        np[i] = color
        np.write()
        time.sleep_ms(delay_ms)


# ── 彩虹燈（HSV 轉 RGB）──────────────────────────────────────
def hsv_to_rgb(h: int) -> tuple:
    """h: 0~255，回傳 (R, G, B)"""
    h = h % 256
    if h < 85:
        return (255 - h * 3, h * 3, 0)
    elif h < 170:
        h -= 85
        return (0, 255 - h * 3, h * 3)
    else:
        h -= 170
        return (h * 3, 0, 255 - h * 3)


def rainbow(delay_ms=10):
    for offset in range(256):
        for i in range(LED_COUNT):
            np[i] = hsv_to_rgb((offset + i * (256 // LED_COUNT)) % 256)
        np.write()
        time.sleep_ms(delay_ms)


# ── 主程式 ────────────────────────────────────────────────────
while True:
    # 跑馬燈（紅色）
    for _ in range(3):
        chase(color=(255, 0, 0), delay_ms=100)

    # 彩虹一圈
    rainbow(delay_ms=10)
