"""
硬體中斷 (Hardware Interrupt)
Core-Skills - interrupt

原始課程: 7.ESP32_硬體中斷與人體紅外線感應模組 / 12.硬體中斷與睡眠省電
平台: ESP32 MicroPython

功能:
  按鈕觸發硬體中斷，切換 LED 狀態
  PIR 人體紅外線感應模組觸發中斷

注意事項:
  - 中斷回呼 (ISR) 內不可使用 print()，容易造成當機重啟
  - ISR 內處理時間需盡可能短
  - 按鈕防彈跳：ISR 內以 ticks_diff 判斷距上次觸發時間

硬體接線:
  按鈕     → GPIO 2（內建 PULL_UP）
  綠色 LED → GPIO 12（串接 220Ω）
  紅色 LED → GPIO 13（串接 220Ω）
  PIR OUT  → GPIO 27
"""

import time
from machine import Pin

BTN_PIN    = 2
LED_G_PIN  = 12
LED_R_PIN  = 13
PIR_PIN    = 27

btn   = Pin(BTN_PIN,   Pin.IN,  Pin.PULL_UP)
led_g = Pin(LED_G_PIN, Pin.OUT)
led_r = Pin(LED_R_PIN, Pin.OUT)
pir   = Pin(PIR_PIN,   Pin.IN)

led_g.value(1)
led_r.value(0)

# ── 按鈕中斷（含防彈跳）──────────────────────────────────────
_debounce_ms = 0

def btn_isr(pin):
    global _debounce_ms
    now = time.ticks_ms()
    if time.ticks_diff(now, _debounce_ms) > 300:
        led_g.value(not led_g.value())
        _debounce_ms = now

btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_isr)


# ── PIR 人體紅外線中斷 ────────────────────────────────────────
_pir_detected  = False
_pir_triggered = 0

def pir_isr(pin):
    global _pir_detected, _pir_triggered
    _pir_detected  = True
    _pir_triggered = time.ticks_ms()

pir.irq(trigger=Pin.IRQ_RISING, handler=pir_isr)


# ── 主迴圈：紅燈閃爍（展示中斷不影響主程式）────────────────
print("Running. Press button to toggle green LED.")
print("Walk past PIR to trigger detection.")

while True:
    # 紅燈每 5 秒閃爍（模擬主程式有 delay 時中斷仍可運作）
    led_r.value(1)
    time.sleep_ms(5000)
    led_r.value(0)
    time.sleep_ms(5000)

    # 主迴圈內處理 PIR 偵測訊息（不在 ISR 內 print）
    if _pir_detected:
        if pir.value() == 0:
            elapsed = time.ticks_diff(time.ticks_ms(), _pir_triggered) // 1000
            print("Motion stopped. Duration: {}s".format(elapsed))
            _pir_detected = False
        else:
            print("Motion detected!")
