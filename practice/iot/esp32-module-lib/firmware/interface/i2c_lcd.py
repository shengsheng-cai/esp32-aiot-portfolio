"""
I2C LCD（HD44780 + PCF8574）
interface - i2c_lcd

原始課程: linux-iot/iot-hardware/ai-rpi-i2c (lcdtime.py)
平台: ESP32 MicroPython

功能:
  範例 1: 基本操作（文字輸出、游標、背光、清除）
  範例 2: 時鐘顯示（本地時間每秒更新）
  範例 3: 自訂字元（CGRAM，最多 8 個）

LCD 規格:
  16x2 字元型液晶，HD44780 控制器
  透過 PCF8574 I2C 擴充板連接，預設位址 0x27（部分模組為 0x3F）
  用 i2c_scan() 確認位址

驅動安裝:
  需要 lcd_api.py 和 machine_i2c_lcd.py（已放在 lib/）
  上傳到 ESP32：
    mpremote cp lib/lcd_api.py :lib/lcd_api.py
    mpremote cp lib/machine_i2c_lcd.py :lib/machine_i2c_lcd.py

與 NTP 搭配:
  時鐘顯示需先執行 ntptime.settime()（見 networking/wifi.py ntp_sync_demo）
  或讓 ESP32 連 WiFi 後自動同步

硬體接線:
  LCD 模組 SDA → GPIO 21
  LCD 模組 SCL → GPIO 22
  LCD 模組 VCC → 5V（部分模組支援 3.3V，視模組設計）
  LCD 模組 GND → GND
"""

import time
from machine import I2C, Pin

I2C_SDA = 21
I2C_SCL = 22
LCD_ADDR = 0x27   # 若無顯示改試 0x3F
LCD_ROWS = 2
LCD_COLS = 16


def _init_i2c():
    return I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400_000)


def i2c_scan():
    """掃描 I2C 裝置，確認 LCD 位址"""
    i2c = _init_i2c()
    devices = i2c.scan()
    print("I2C devices:", [hex(d) for d in devices])
    return devices


def _init_lcd():
    try:
        from machine_i2c_lcd import I2cLcd
    except ImportError:
        raise ImportError(
            "LCD driver not found.\n"
            "Upload lib/lcd_api.py and lib/machine_i2c_lcd.py to ESP32."
        )
    i2c = _init_i2c()
    lcd = I2cLcd(i2c, LCD_ADDR, LCD_ROWS, LCD_COLS)
    lcd.backlight_on()
    return lcd


# ── 範例 1：基本操作 ──────────────────────────────────────
def basic_demo():
    """文字輸出、游標移動、背光控制、清除"""
    lcd = _init_lcd()

    # 第一行
    lcd.move_to(0, 0)
    lcd.putstr("Hello ESP32!")

    # 第二行
    lcd.move_to(0, 1)
    lcd.putstr("MicroPython")

    time.sleep(2)

    # 清除後顯示計數
    print("Basic demo — counting up")
    for i in range(10):
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Count: {}".format(i))
        time.sleep(1)

    # 背光關閉
    lcd.backlight_off()
    time.sleep(1)
    lcd.backlight_on()
    lcd.clear()


# ── 範例 2：時鐘顯示 ──────────────────────────────────────
def clock_demo():
    """
    每秒更新顯示本地時間（UTC+8）
    需先執行 ntptime.settime() 同步時間，否則顯示開機後的相對時間
    """
    lcd = _init_lcd()
    print("Clock demo — press Ctrl+C to stop")

    while True:
        t = time.localtime(time.mktime(time.localtime()) + 28800)
        date_str = "{0}/{1:02d}/{2:02d}".format(t[0], t[1], t[2])
        time_str = "{0:02d}:{1:02d}:{2:02d}".format(t[3], t[4], t[5])

        lcd.move_to(0, 0)
        lcd.putstr("Date: " + date_str)
        lcd.move_to(0, 1)
        lcd.putstr("Time: " + time_str)

        time.sleep(1)


# ── 範例 3：自訂字元 ──────────────────────────────────────
def custom_char_demo():
    """
    CGRAM 最多存 8 個 5x8 自訂字元（chr(0)〜chr(7)）
    常用於：溫度符號、心跳圖示、電池圖示等
    """
    lcd = _init_lcd()

    # 自訂心形圖案（5x8 bitmap）
    heart = [
        0b00000,
        0b01010,
        0b11111,
        0b11111,
        0b01110,
        0b00100,
        0b00000,
        0b00000,
    ]
    lcd.custom_char(0, bytearray(heart))

    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Hello " + chr(0) + " World!")
    time.sleep(3)
    lcd.clear()


# ── 主程式（選擇一種模式）────────────────────────────────
# i2c_scan()
# basic_demo()
clock_demo()
# custom_char_demo()
