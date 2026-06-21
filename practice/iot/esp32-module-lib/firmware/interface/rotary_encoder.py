"""
旋轉編碼器 (Rotary Encoder)
Interface - rotary_encoder

原始課程: 34.ESP32 旋轉編碼器 / 44.旋轉編碼器 Rotary Encoder
平台: ESP32 MicroPython

功能:
  CLK 下降沿觸發硬體中斷，讀取 DT 狀態判斷轉向
  按下 SW 鍵歸零計數

旋轉方向判斷:
  CLK 下降沿時：
    DT = HIGH → 順時針（+1）
    DT = LOW  → 逆時針（-1）

注意事項:
  - ISR 內不可 print()，用 flag 在主迴圈輸出
  - 去彈跳：100ms 內同方向不重複計數
  - MicroPython 的 volatile 等效：ISR 修改全域變數，Python GIL 保護基本資料型態

硬體接線:
  CLK → D22
  DT  → D23
  SW  → D21（PULL_UP）
  +   → 3.3V
  GND → GND
"""

import time
from machine import Pin

CLK_PIN = 22
DT_PIN  = 23
SW_PIN  = 21

clk = Pin(CLK_PIN, Pin.IN)
dt  = Pin(DT_PIN,  Pin.IN)
sw  = Pin(SW_PIN,  Pin.IN, Pin.PULL_UP)

count        = 0
_last_t      = 0
_count_dirty = False  # 旗標：有新的計數需要印出


# ── 中斷處理（CLK 下降沿）────────────────────────────────────
def clk_isr(pin):
    global count, _last_t, _count_dirty
    now = time.ticks_ms()
    if time.ticks_diff(now, _last_t) < 100:   # 去彈跳
        return
    _last_t = now
    count += 1 if dt.value() == 1 else -1
    _count_dirty = True

clk.irq(trigger=Pin.IRQ_FALLING, handler=clk_isr)


# ── 主迴圈 ────────────────────────────────────────────────────
print("Rotary encoder ready. Turn knob or press SW to reset.")

while True:
    if _count_dirty:
        print("count:", count)
        _count_dirty = False

    if sw.value() == 0:
        count = 0
        print("count reset to 0")
        time.sleep_ms(300)   # 防彈跳

    time.sleep_ms(10)
