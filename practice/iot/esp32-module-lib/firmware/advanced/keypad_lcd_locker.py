"""
Keypad + I2C LCD 門禁管制機
Advanced - 綜合應用

原始課程: 19.Keypad加LCD門禁管制機(綜合應用)
平台: ESP32 MicroPython

功能:
  4x4 鍵盤輸入密碼，比對後以 I2C LCD 顯示結果
  * 鍵：清除已輸入字元
  # 鍵：確認送出

硬體接線:
  Keypad 列 (ROW)  → GPIO 13, 14, 15, 16
  Keypad 行 (COL)  → GPIO 17, 18, 19, 23
  LCD I2C SDA      → GPIO 21（ESP32 預設）
  LCD I2C SCL      → GPIO 22（ESP32 預設）

依賴:
  i2c_lcd.py、lcd_api.py
  下載: https://github.com/dhylands/python_lcd
"""

import time
from machine import Pin, I2C
from i2c_lcd import I2cLcd

# ── 鍵盤配置 ─────────────────────────────────────────────────
KEYMAP = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D'],
]
ROW_PINS = [13, 14, 15, 16]
COL_PINS = [17, 18, 19, 23]

# ── 硬體初始化 ───────────────────────────────────────────────
rows = [Pin(p, Pin.OUT) for p in ROW_PINS]
cols = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in COL_PINS]

i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# ── 密碼設定 ─────────────────────────────────────────────────
PASSCODE = "4321"
input_code = ""
accept_key = True


# ── 鍵盤掃描 ─────────────────────────────────────────────────
def get_key():
    for r_idx, row in enumerate(rows):
        row.value(1)
        for c_idx, col in enumerate(cols):
            if col.value():
                row.value(0)
                time.sleep_ms(20)  # 防彈跳
                if col.value():
                    return KEYMAP[r_idx][c_idx]
        row.value(0)
    return None


# ── LCD 操作 ─────────────────────────────────────────────────
def clear_row(start_col):
    """從 start_col 開始清除 LCD 第二行"""
    lcd.move_to(start_col, 1)
    for _ in range(16 - start_col):
        lcd.putstr(" ")
    lcd.move_to(start_col, 1)


def reset_locker():
    global input_code, accept_key
    lcd.clear()
    lcd.putstr("Knock, Knock...")
    lcd.move_to(0, 1)
    lcd.putstr("PIN: ")
    input_code = ""
    accept_key = True


def check_pin():
    global accept_key
    accept_key = False
    clear_row(0)
    if input_code == PASSCODE:
        lcd.putstr("Welcome home!")
    else:
        lcd.putstr("***WRONG!!***")
    time.sleep_ms(3000)
    reset_locker()


# ── 主程式 ───────────────────────────────────────────────────
reset_locker()

while True:
    key = get_key()
    if accept_key and key:
        if key == '*':
            clear_row(5)        # 從 "PIN: " 後第 5 格開始清除
            input_code = ""
        elif key == '#':
            check_pin()
        else:
            input_code += key
            lcd.putstr('*')
    time.sleep_ms(50)
