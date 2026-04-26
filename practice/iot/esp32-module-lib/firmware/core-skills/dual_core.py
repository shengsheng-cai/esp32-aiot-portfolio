"""
ESP32 雙核心並行任務
Core-Skills - dual_core

原始課程: 32.ESP32 使用雙核心
平台: ESP32 MicroPython

功能:
  使用 _thread 模組在 Core0/Core1 各自執行獨立任務
  範例：LED1 快閃（Core1）、LED2 慢閃（Core0 主執行緒）

ESP32 雙核心說明:
  - Core0：通常負責 WiFi/BT 協定棧
  - Core1：預設執行 MicroPython 主程式
  - MicroPython 使用 _thread 模組建立第二執行緒（跑在 Core0）

注意事項:
  - 兩個執行緒共用變數時需注意競態，可用 Lock 保護
  - 執行緒內迴圈至少需要 1ms 延時，否則可能造成 WDT 重啟
  - MicroPython 的 _thread 不能像 FreeRTOS 那樣指定核心，
    但 ESP32 的 _thread 預設會跑在 Core0

硬體接線:
  LED1 → GPIO 2（串接 220Ω）
  LED2 → GPIO 4（串接 220Ω）
  按鈕 → GPIO 23（按下觸發，內建 PULL_UP）
"""

import time
import _thread
from machine import Pin

LED1_PIN = 2
LED2_PIN = 4
BTN_PIN  = 23

led1 = Pin(LED1_PIN, Pin.OUT)
led2 = Pin(LED2_PIN, Pin.OUT)
btn  = Pin(BTN_PIN,  Pin.IN, Pin.PULL_UP)

# 共用狀態（用 Lock 保護寫入）
lock         = _thread.allocate_lock()
led2_state   = False
running      = True


# ── Core0 執行緒：LED1 快閃（700ms）──────────────────────────
def task1():
    print("Task1 running (LED1 fast blink)")
    while running:
        led1.value(1)
        time.sleep_ms(700)
        led1.value(0)
        time.sleep_ms(700)


# ── Core1 主執行緒：LED2 慢閃（5s）+ 按鈕切換 ────────────────
def task2():
    global led2_state
    print("Task2 running (LED2 slow blink + button)")
    while True:
        # 按鈕按下時切換 LED2 狀態
        if btn.value() == 0:
            with lock:
                led2_state = not led2_state
                led2.value(led2_state)
            time.sleep_ms(300)   # 防彈跳
        else:
            led2.value(1)
            time.sleep_ms(5000)
            led2.value(0)
            time.sleep_ms(5000)


# ── 啟動 ──────────────────────────────────────────────────────
_thread.start_new_thread(task1, ())
task2()
