"""
MAX30100 心率血氧偵測模組
Sensors - max30100

原始課程: 44.ESP32 MAX30100心率血氧偵測模組
平台: ESP32 MicroPython

功能:
  範例 1: 讀取心率（BPM）與血氧飽和度（SpO2）
  範例 2: 讀取晶片溫度

MAX30100 說明:
  I2C 介面，位址 0x57（課程中說明；部分文件寫 0x57，晶片規格書為 0x57）
  兩個 LED：紅光（650nm）+ 紅外線（880nm）
  透過光電體積描記法（PPG）偵測心率與血氧

模組已知問題（課程中特別說明）:
  部分模組上拉電阻接 1.8V 而非 3.3V，導致 I2C 無法通訊
  解法 1：切斷 1.8V 連線，改接跳線到 3.3V
  解法 2：移除模組 4.7kΩ 上拉電阻，自行外接上拉到 3.3V

Arduino MAX30100lib → MicroPython max30100 驅動
  安裝：mpremote mip install github:n-elia/MAX30100-micropython/max30100.py
  或手動下載 https://github.com/n-elia/MAX30100-micropython

補充：MAX30102（更新版本）相容性更好，可考慮替換

硬體接線:
  MAX30100 SCL → GPIO 22
  MAX30100 SDA → GPIO 21
  MAX30100 VCC → 3.3V（或 5V，視模組穩壓設計）
  MAX30100 GND → GND
"""

import time
from machine import I2C, Pin

I2C_SCL = 22
I2C_SDA = 21
MAX30100_ADDR = 0x57   # 確認時用 I2C scanner

REPORT_INTERVAL_MS = 1000


def _init_i2c():
    return I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400_000)


def i2c_scan():
    """掃描 I2C 裝置，確認 MAX30100 是否正確連線"""
    i2c = _init_i2c()
    devices = i2c.scan()
    if devices:
        print("I2C devices:", [hex(d) for d in devices])
    else:
        print("No I2C devices found — check wiring and pull-up resistors")
    return devices


# ── 範例 1：心率與血氧（使用 max30100 驅動）─────────────────
def hr_spo2_demo():
    """
    讀取心率（BPM）與血氧（SpO2）
    需先安裝 max30100 MicroPython 驅動：
      mpremote mip install github:n-elia/MAX30100-micropython/max30100.py
    將手指穩定放在感測器上，等待數秒後讀值趨於穩定
    """
    try:
        from max30100 import MAX30100
    except ImportError:
        print("max30100 driver not found.")
        print("Install: mpremote mip install github:n-elia/MAX30100-micropython/max30100.py")
        return

    i2c = _init_i2c()
    sensor = MAX30100(i2c=i2c)
    sensor.enable_spo2()
    # IR LED 電流降低至 7.6mA（課程建議：預設 50mA 可能導致讀值異常）
    sensor.set_led_current_red(7.6)
    sensor.set_led_current_ir(7.6)

    print("MAX30100 ready. Place finger on sensor.")
    ts_last = 0

    while True:
        sensor.read_sensor()
        now = time.ticks_ms()
        if time.ticks_diff(now, ts_last) >= REPORT_INTERVAL_MS:
            hr   = sensor.heart_rate
            spo2 = sensor.spo2
            if hr and spo2:
                print("Heart Rate: {:.1f} bpm  SpO2: {:.1f}%".format(hr, spo2))
            else:
                print("Detecting... (keep finger steady)")
            ts_last = now


# ── 範例 2：晶片溫度 ─────────────────────────────────────────
def temperature_demo():
    """
    讀取 MAX30100 晶片內建溫度感測器
    範圍 -40〜+85°C，用於補償環境變化
    直接讀 I2C 寄存器，不需完整驅動
    """
    i2c = _init_i2c()
    addr = MAX30100_ADDR

    # 寄存器 0x08 = MODE_CONFIG；設定 TEMP_EN bit
    def read_temp():
        # Trigger temperature measurement（bit3=1）
        mode = i2c.readfrom_mem(addr, 0x06, 1)[0]
        i2c.writeto_mem(addr, 0x06, bytes([mode | 0x08]))
        time.sleep_ms(50)
        msb  = i2c.readfrom_mem(addr, 0x16, 1)[0]
        frac = i2c.readfrom_mem(addr, 0x17, 1)[0] * 0.0625
        if msb & 0x80:
            msb -= 256
        return msb + frac

    print("MAX30100 temperature demo")
    while True:
        try:
            temp = read_temp()
            print("Chip Temp: {:.2f} °C".format(temp))
        except OSError as e:
            print("I2C error:", e)
        time.sleep(1)


# ── 主程式（選擇一種模式）────────────────────────────────────
# i2c_scan()       # 先執行確認連線
hr_spo2_demo()
# temperature_demo()
