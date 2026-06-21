"""
4x4 矩陣鍵盤
Interface - keypad

原始課程: 10.ESP32_鍵盤(4x4)Keypad / 15.鍵盤(4x4)Keypad
平台: ESP32 MicroPython

功能:
  手動掃描 4x4 矩陣鍵盤（無需外部函式庫）
  防止重複觸發（鍵盤釋放後才接受下一次輸入）

掃描原理:
  - COL（行）設為 OUTPUT，依序輸出 LOW
  - ROW（列）設為 INPUT_PULLUP
  - 某 COL 拉 LOW 時，若某 ROW 讀到 LOW，即對應按鍵被按下

硬體接線:
  ROW 1~4 → D32, D33, D25, D26（PULL_UP 輸入）
  COL 1~4 → D27, D14, D12, D13（輸出）
"""

import time
from machine import Pin

ROW_PINS = [32, 33, 25, 26]
COL_PINS = [27, 14, 12, 13]

KEY_MAP = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D'],
]

rows = [Pin(p, Pin.IN,  Pin.PULL_UP) for p in ROW_PINS]
cols = [Pin(p, Pin.OUT)              for p in COL_PINS]

for c in cols:
    c.value(1)


def scan_keypad() -> str | None:
    """掃描一次鍵盤，回傳按下的字元，無按下回傳 None"""
    for ci, col in enumerate(cols):
        col.value(0)
        for ri, row in enumerate(rows):
            if row.value() == 0:
                col.value(1)
                return KEY_MAP[ri][ci]
        col.value(1)
    return None


def read_keypad_loop():
    """
    主迴圈：印出每次按鍵
    防止重複觸發：鍵盤釋放後才接受下一次輸入
    """
    btn_released = True

    print("Keypad ready. Press any key...")

    while True:
        key = scan_keypad()

        if key is not None:
            if btn_released:
                print("Key:", key)
                btn_released = False
        else:
            btn_released = True

        time.sleep_ms(20)


read_keypad_loop()
