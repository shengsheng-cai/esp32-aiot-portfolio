"""
4 切指撥開關 (DIP Switch)
Interface - dip_switch

原始課程: 13.DipSW(4切指撥開關)
平台: ESP32 MicroPython

功能:
  讀取 4 個指撥開關，位移計算轉為十進位編碼（0~15）
  數值變化時才印出

DIP Switch 編碼原理:
  SW1 = bit 0 (值 1)
  SW2 = bit 1 (值 2)
  SW3 = bit 2 (值 4)
  SW4 = bit 3 (值 8)
  全 OFF = 0, 全 ON = 15

硬體接線:
  SW1~SW4 → D14, D27, D26, D25（每個串接 10kΩ 下拉電阻到 GND）
  開關另一端 → 3.3V
"""

import time
from machine import Pin

SW_PINS = [14, 27, 26, 25]   # SW1~SW4 對應 bit 0~3

switches = [Pin(p, Pin.IN) for p in SW_PINS]

last_val = -1
print("DIP switch ready. Change switches to update value.")

while True:
    val = sum(switches[i].value() << i for i in range(4))

    if val != last_val:
        print("DIP value: {:2d}  (binary: {:04b})".format(val, val))
        last_val = val

    time.sleep_ms(50)
