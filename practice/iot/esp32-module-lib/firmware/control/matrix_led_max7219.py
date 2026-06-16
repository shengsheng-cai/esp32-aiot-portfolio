"""
8x8 矩陣 LED 控制 (MAX7219)
Control - matrix_led_max7219


功能:
  點亮單顆 LED、整列輸出、文字捲動跑馬燈

硬體注意事項:
  - MAX7219 模組分 FC16 與 GENERIC 兩種 layout，方向不同
  - 串接 4 組以上建議外接電源
  - SPI 通訊，MISO 不使用

硬體接線:
  DIN  → GPIO 23 (MOSI)
  CLK  → GPIO 18 (SCK)
  CS   → GPIO 21 (SS)
  VCC  → 5V
  GND  → GND

依賴:
  micropython-max7219 函式庫
  安裝: mpremote mip install github:mcauser/micropython-max7219
  或直接下載 max7219.py 到 ESP32:
  https://github.com/mcauser/micropython-max7219
"""

import time
from machine import Pin, SPI
import max7219

SPI_ID = 1
CLK_PIN = 18
MOSI_PIN = 23
CS_PIN = 21
NUM_DEVICES = 1  # 串接模組數量

spi = SPI(
    SPI_ID, baudrate=10000000, polarity=0, phase=0, sck=Pin(CLK_PIN), mosi=Pin(MOSI_PIN)
)
cs = Pin(CS_PIN, Pin.OUT)

display = max7219.Matrix8x8(spi, cs, NUM_DEVICES)
display.brightness(4)  # 0~15


# ── 點亮單顆 LED ──────────────────────────────────────────────
def test_single_pixel():
    display.fill(0)
    display.pixel(2, 0, 1)  # (col, row, on)
    display.show()
    time.sleep_ms(1000)


# ── 笑臉圖案（整列輸出）──────────────────────────────────────
SMILE = [0x3C, 0x42, 0xA5, 0x81, 0xA5, 0x99, 0x42, 0x3C]


def show_smile():
    display.fill(0)
    for row, byte in enumerate(SMILE):
        for col in range(8):
            display.pixel(col, row, (byte >> (7 - col)) & 1)
    display.show()
    time.sleep_ms(2000)


# ── 文字捲動跑馬燈 ────────────────────────────────────────────
def scroll_text(text: str, delay_ms=80):
    """從右到左捲動文字"""
    for char in text:
        # 取得字元的 8x8 點陣（每個字元 8 欄）
        display.fill(0)
        display.text(char, 0, 0, 1)
        display.show()
        # 向左捲動 8 欄
        for _ in range(8):
            display.scroll(-1, 0)
            display.show()
            time.sleep_ms(delay_ms)


# ── 主程式 ────────────────────────────────────────────────────
test_single_pixel()
show_smile()

while True:
    scroll_text("Hello ESP32 ", delay_ms=60)
