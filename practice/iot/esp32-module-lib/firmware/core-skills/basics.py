"""
ESP32 MicroPython 基礎操作
Core Skills - basics

原始課程:
  1-1.Serial 序列終端機
  1-2.LED Blink
  1-3.For迴圈製作霹靂燈（跑馬燈）
  1-4.If 條件判斷（按鈕開關控制）
  1-5.按鈕開關防止重複觸發
  1-6.按鈕開關防彈跳（官方版）

平台: ESP32 MicroPython

Arduino → MicroPython 對應:
  Serial.begin() / Serial.println() → print()（直接用，不需初始化）
  pinMode(pin, OUTPUT)              → Pin(pin, Pin.OUT)
  pinMode(pin, INPUT_PULLUP)        → Pin(pin, Pin.IN, Pin.PULL_UP)
  digitalWrite(pin, HIGH)           → pin.value(1)
  digitalRead(pin)                  → pin.value()
  delay(ms)                         → time.sleep_ms(ms)
  millis()                          → time.ticks_ms()

硬體接線:
  LED      → GPIO 23（外接）或 GPIO 2（內建）
  跑馬燈  → GPIO 13, 12, 14, 27, 26, 25, 33, 32
  按鈕    → GPIO 21（INPUT_PULLUP，另端接 GND）
"""

import time
from machine import Pin

LED_PIN    = 23
BTN_PIN    = 21
KNIGHT_PINS = [13, 12, 14, 27, 26, 25, 33, 32]


# ── 範例 1：Serial（print）──────────────────────────────────
def serial_demo():
    """
    Arduino Serial.println() → MicroPython print()
    在 REPL 直接印出，無需設定鮑率
    """
    count = 0
    while True:
        print("Hello ESP32! count={}".format(count))
        count += 1
        time.sleep(1)


# ── 範例 2：LED Blink ─────────────────────────────────────────
def blink_demo(pin: int = LED_PIN, interval_ms: int = 1000):
    """每 interval_ms 毫秒切換一次 LED"""
    led = Pin(pin, Pin.OUT)
    while True:
        led.value(1)
        time.sleep_ms(interval_ms)
        led.value(0)
        time.sleep_ms(interval_ms)


# ── 範例 3：霹靂燈（跑馬燈）─────────────────────────────────
def knight_rider_demo():
    """8 顆 LED 左右輪流點亮（Knight Rider 效果）"""
    leds = [Pin(p, Pin.OUT) for p in KNIGHT_PINS]

    def all_off():
        for led in leds:
            led.value(0)
        time.sleep_ms(20)

    print("Knight Rider — GPIO:", KNIGHT_PINS)
    while True:
        for i in range(len(leds)):
            leds[i].value(1)
            time.sleep_ms(100)
            all_off()
        for i in range(len(leds) - 2, 0, -1):
            leds[i].value(1)
            time.sleep_ms(100)
            all_off()


# ── 範例 4：按鈕控制 LED（INPUT_PULLUP）──────────────────────
def button_demo():
    """
    按鈕接 GPIO 21（INPUT_PULLUP）：按下 → LOW
    按下時切換 LED
    """
    btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)
    led = Pin(LED_PIN, Pin.OUT)

    print("Button on GPIO{} (PULL_UP) — press to toggle LED".format(BTN_PIN))
    while True:
        if btn.value() == 0:   # 按下（LOW）
            led.value(1)
        else:
            led.value(0)
        time.sleep_ms(10)


# ── 範例 5：防止重複觸發（btn_released 狀態機）───────────────
def no_repeat_demo():
    """
    每次按下只觸發一次（需等待放開才能再次觸發）
    避免長按時連續切換
    """
    btn    = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)
    led    = Pin(LED_PIN, Pin.OUT)
    state  = False
    released = True   # 記錄按鈕是否已放開

    print("No-repeat button demo")
    while True:
        pressed = (btn.value() == 0)

        if pressed and released:   # 按下 + 上次已放開 → 觸發
            state = not state
            led.value(state)
            print("Toggle! LED:", "ON" if state else "OFF")
            released = False

        if not pressed:            # 放開時重置 released
            released = True

        time.sleep_ms(10)


# ── 範例 6：防彈跳（millis debounce）────────────────────────
DEBOUNCE_MS = 50


def debounce_demo():
    """
    使用 ticks_ms() 實現防彈跳（Arduino 官方方法移植）
    只有電位穩定超過 DEBOUNCE_MS 毫秒，才確認狀態改變
    """
    btn            = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)
    led            = Pin(LED_PIN, Pin.OUT)
    led_state      = False
    btn_state      = 1    # 目前確認的按鈕狀態
    last_reading   = 1    # 上次讀取值
    last_change_ms = 0    # 上次電位改變的時間

    print("Debounce demo — debounce={}ms".format(DEBOUNCE_MS))
    while True:
        reading = btn.value()

        if reading != last_reading:
            last_change_ms = time.ticks_ms()   # 電位改變，重新計時

        if time.ticks_diff(time.ticks_ms(), last_change_ms) > DEBOUNCE_MS:
            if reading != btn_state:
                btn_state = reading
                if btn_state == 0:             # 確認按下
                    led_state = not led_state
                    led.value(led_state)
                    print("Button pressed! LED:", "ON" if led_state else "OFF")

        last_reading = reading
        time.sleep_ms(5)


# ── 主程式（選擇一種模式）────────────────────────────────────
# serial_demo()
# blink_demo()
# knight_rider_demo()
# button_demo()
# no_repeat_demo()
debounce_demo()
