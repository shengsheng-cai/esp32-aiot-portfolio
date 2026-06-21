"""
TFT ST7735 彩色液晶顯示器
Interface - tft_st7735

原始課程: 41.ESP32 TFT ST7735 彩色液晶模組
平台: ESP32 MicroPython

規格:
  尺寸: 1.8 吋
  解析度: 128 × 160 像素
  顏色: RGB 65536 色（RGB 5-6-5）
  介面: SPI

依賴函式庫:
  micropython-st7735 (boochow 版本)
  https://github.com/boochow/MicroPython-ST7735
  將 st7735.py 和 sysfont.py 放入 ESP32 根目錄

顏色格式 RGB565:
  每個顏色 16 bit = R(5) + G(6) + B(5)
  TFT.BLACK=0x0000, TFT.WHITE=0xFFFF, TFT.RED=0xF800
  TFT.GREEN=0x07E0, TFT.BLUE=0x001F, TFT.YELLOW=0xFFE0
  自訂色: from st7735 import TFTColor; TFTColor(r, g, b)

注意事項:
  - SPI1 on ESP32: SCLK=GPIO18, MOSI=GPIO23（固定 SPI 腳位）
  - DC/RST/CS 可自定義
  - initr() 適用黑色邊框版本（INITR_BLACKTAB）

硬體接線:
  SCL(SCLK) → D18
  SDA(MOSI) → D23
  RES(RST)  → D5
  DC        → D17
  CS        → D16
  BL(背光)   → 3.3V（或 GPIO 控制）
  VCC       → 3.3V
  GND       → GND
"""

import time
from machine import SPI, Pin

TFT_SCK  = 18
TFT_MOSI = 23
TFT_RST  = 5
TFT_DC   = 17
TFT_CS   = 16


def make_tft():
    from st7735 import TFT
    spi = SPI(1, baudrate=20_000_000, sck=Pin(TFT_SCK), mosi=Pin(TFT_MOSI))
    tft = TFT(spi, aDC=Pin(TFT_DC), aReset=Pin(TFT_RST), aCS=Pin(TFT_CS))
    tft.initr()    # INITR_BLACKTAB
    tft.rgb(True)  # RGB 顏色排列
    return tft


# ── 範例 1：文字輸出 ──────────────────────────────────────────
def text_demo():
    from st7735 import TFT
    from sysfont import sysfont

    tft = make_tft()
    tft.fill(TFT.BLACK)

    tft.text(sysfont, "Hello, World!", 0,  0,  TFT.WHITE)
    tft.text(sysfont, "ST7735 TFT",    0, 16, TFT.RED)
    tft.text(sysfont, "128 x 160",     0, 32, TFT.GREEN)
    tft.text(sysfont, "MicroPython",   0, 48, TFT.BLUE)

    print("Text demo done")


# ── 範例 2：繪圖 ──────────────────────────────────────────────
def draw_demo():
    from st7735 import TFT, TFTColor

    tft = make_tft()
    tft.fill(TFT.BLACK)

    # 線條
    tft.line((0, 0), (127, 159), TFT.YELLOW)

    # 矩形
    tft.rect((20, 20), (60, 50), TFT.GREEN)
    tft.fillrect((70, 20), (110, 50), TFT.RED)

    # 圓形
    tft.circle((64, 100), 30, TFT.CYAN)
    tft.fillcircle((100, 100), 15, TFT.MAGENTA)

    print("Draw demo done")


# ── 範例 3：填色動畫 ──────────────────────────────────────────
def color_cycle_demo():
    from st7735 import TFT

    tft = make_tft()
    colors = [TFT.BLACK, TFT.RED, TFT.GREEN, TFT.BLUE,
              TFT.YELLOW, TFT.CYAN, TFT.MAGENTA, TFT.WHITE]

    print("Color cycle demo. Press Ctrl+C to stop.")
    while True:
        for c in colors:
            tft.fill(c)
            time.sleep_ms(500)


# ── 範例 4：顯示 DHT11 溫溼度 ─────────────────────────────────
def dht_display_demo(dht_pin: int = 27):
    """在 TFT 上即時顯示 DHT11 溫溼度"""
    import dht
    from st7735 import TFT, TFTColor
    from sysfont import sysfont

    tft  = make_tft()
    d    = dht.DHT11(Pin(dht_pin))
    GRAY = TFTColor(80, 80, 80)

    tft.fill(TFT.BLACK)
    tft.text(sysfont, "Temp:",  0,  5, TFT.WHITE)
    tft.text(sysfont, "Humi:",  0, 50, TFT.WHITE)

    print("DHT display demo running...")
    while True:
        try:
            d.measure()
            t = d.temperature()
            h = d.humidity()
        except OSError:
            t, h = 0, 0

        # 清除舊數值（填灰色塊再重寫）
        tft.fillrect((50, 5), (127, 20), TFT.BLACK)
        tft.fillrect((50, 50), (127, 65), TFT.BLACK)
        tft.text(sysfont, "{}C".format(t), 50,  5, TFT.ORANGE if t else GRAY)
        tft.text(sysfont, "{}%".format(h), 50, 50, TFT.BLUE)

        print("T={}C  H={}%".format(t, h))
        time.sleep_ms(2000)


# ── 主程式（選擇一種模式）────────────────────────────────────
# text_demo()
# draw_demo()
# color_cycle_demo()
dht_display_demo(dht_pin=27)
