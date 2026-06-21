"""
OLED SSD1306 顯示器
Interface - oled_ssd1306

原始課程: 33.OLED SSD1306 顯示器 / 43.OLED SSD1306 顯示器
平台: ESP32 MicroPython

功能:
  範例 1: 文字輸出（Hello World）
  範例 2: 繪圖（像素點、線、矩形、圓形）
  範例 3: 自訂 bitmap 圖像（8x8 笑臉）
  範例 4: 動態計數（清除 → 重繪）

依賴函式庫:
  ssd1306.py - MicroPython 固件通常內建；若無，可安裝：
  mpremote mip install ssd1306

SSD1306 規格:
  128×64 像素，單色
  I2C 位址：0x3C（通常）
  工作電壓：3~5V

注意事項:
  - 每次修改後必須呼叫 oled.show() 才會更新畫面
  - framebuf 內建 line、rect、fill_rect、ellipse（MicroPython v1.22+）
  - 三角形需用三條線組合

硬體接線:
  SSD1306 SCL → D22
  SSD1306 SDA → D21
  SSD1306 VCC → 3.3V
  SSD1306 GND → GND
"""

import time
import framebuf
from machine import I2C, Pin
import ssd1306

I2C_SCL = 22
I2C_SDA = 21
I2C_ADDR = 0x3C
WIDTH  = 128
HEIGHT = 64


def make_oled() -> ssd1306.SSD1306_I2C:
    i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400_000)
    return ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=I2C_ADDR)


# ── 範例 1：文字輸出 ──────────────────────────────────────────
def text_demo():
    oled = make_oled()
    oled.fill(0)

    oled.text("Hello, World!", 0, 0)            # 基本文字（8px 字高）
    oled.text("SSD1306 OLED", 0, 16)
    oled.text("128 x 64", 0, 32)
    oled.text("MicroPython", 0, 48)

    oled.show()
    print("Text displayed")

    # 反白（inverse）
    time.sleep_ms(2000)
    oled.invert(1)
    time.sleep_ms(2000)
    oled.invert(0)


# ── 範例 2：繪圖 ──────────────────────────────────────────────
def draw_demo():
    oled = make_oled()
    oled.fill(0)

    # 點
    oled.pixel(64, 32, 1)

    # 線
    oled.line(0, 0, 127, 20, 1)

    # 矩形（空心 / 實心）
    oled.rect(20, 10, 40, 20, 1)
    oled.fill_rect(70, 10, 20, 20, 1)

    # 圓（用 ellipse，需 MicroPython v1.22+）
    oled.ellipse(64, 50, 12, 10, 1)         # 空心橢圓
    oled.ellipse(20, 50, 8, 8, 1, True)     # 實心圓

    # 三角形（三條線組合）
    oled.line(100, 44, 115, 60, 1)
    oled.line(115, 60, 85,  60, 1)
    oled.line(85,  60, 100, 44, 1)

    oled.show()
    print("Drawing displayed")


# ── 範例 3：自訂 bitmap 圖像 ──────────────────────────────────
def bitmap_demo():
    """顯示 8×8 笑臉 bitmap（framebuf.MONO_HLSB 格式）"""
    oled = make_oled()
    oled.fill(0)

    # 8×8 笑臉（每 byte = 1 row，bit 7=左，bit 0=右）
    SMILEY = bytearray([
        0b00111100,  # ..XXXX..
        0b01000010,  # .X....X.
        0b10100101,  # X.X..X.X
        0b10000001,  # X......X
        0b10100101,  # X.X..X.X
        0b10011001,  # X..XX..X
        0b01000010,  # .X....X.
        0b00111100,  # ..XXXX..
    ])

    fb = framebuf.FrameBuffer(SMILEY, 8, 8, framebuf.MONO_HLSB)

    # 在畫面中央顯示，放大 4 倍（手動繪製每個像素）
    scale = 4
    cx, cy = (WIDTH - 8 * scale) // 2, (HEIGHT - 8 * scale) // 2
    for y in range(8):
        for x in range(8):
            if fb.pixel(x, y):
                oled.fill_rect(cx + x * scale, cy + y * scale, scale, scale, 1)

    oled.show()
    print("Smiley displayed")


# ── 範例 4：動態計數 ──────────────────────────────────────────
def counter_demo():
    """畫面每秒更新一次，顯示計數器"""
    oled = make_oled()
    n = 0

    print("Counter demo running...")
    while True:
        oled.fill(0)
        oled.text("Counter:", 0, 20)
        oled.text(str(n), 0, 36)
        oled.show()
        n += 1
        time.sleep_ms(1000)


# ── 主程式（選擇一種模式）────────────────────────────────────
# text_demo()
# draw_demo()
# bitmap_demo()
counter_demo()
