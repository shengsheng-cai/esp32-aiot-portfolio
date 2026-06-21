"""
DS3231 高精度實時時鐘模組
Time - ds3231

原始課程: 21-5.ESP32_DS3231時鐘模組
平台: ESP32 MicroPython

功能:
  範例 1: 讀取時間（每秒輸出，含溫度）
  範例 2: 設定時間後持續讀取

DS3231 vs DS1302:
  DS3231 使用 I2C（更簡單，只需 SCL/SDA）
  內建溫度補償振盪器（TCXO），精度 ±2min/年
  I2C 位址 0x68；板載 24C32 EEPROM 位址 0x57

Arduino RTClib → MicroPython machine.I2C 直接讀寫寄存器

注意（DS3231 模組）:
  部分模組帶充電電路（200Ω + 二極體），設計給 LIR2032 可充電電池
  若使用不可充電 CR2032，必須移除 200Ω 電阻，否則有爆炸風險

寄存器位址:
  0x00 秒  0x01 分  0x02 時  0x03 週  0x04 日
  0x05 月  0x06 年  0x11 溫度 MSB  0x12 溫度 LSB（高 2bit）

硬體接線:
  DS3231 SCL → D22
  DS3231 SDA → D21
  DS3231 VCC → 3.3V（或 5V）
  DS3231 GND → GND
"""

import time
from machine import I2C, Pin

I2C_SCL  = 22
I2C_SDA  = 21
DS3231_ADDR = 0x68


def _bcd2dec(bcd: int) -> int:
    return (bcd >> 4) * 10 + (bcd & 0x0F)


def _dec2bcd(dec: int) -> int:
    return (dec // 10) << 4 | (dec % 10)


class DS3231:
    def __init__(self, scl=I2C_SCL, sda=I2C_SDA, addr=DS3231_ADDR):
        self._i2c = I2C(0, scl=Pin(scl), sda=Pin(sda), freq=400_000)
        self._addr = addr

    def _read_reg(self, reg: int, n: int = 1) -> bytes:
        self._i2c.writeto(self._addr, bytes([reg]))
        return self._i2c.readfrom(self._addr, n)

    def _write_reg(self, reg: int, val: int):
        self._i2c.writeto(self._addr, bytes([reg, val]))

    def set_time(self, year: int, month: int, day: int,
                 hour: int, minute: int, second: int, weekday: int = 1):
        """
        設定時間
        year: 完整年份（如 2024）
        weekday: 1=週日 … 7=週六
        """
        data = bytes([
            0x00,                        # 起始寄存器
            _dec2bcd(second),
            _dec2bcd(minute),
            _dec2bcd(hour),              # 24h 模式（bit6=0）
            _dec2bcd(weekday),
            _dec2bcd(day),
            _dec2bcd(month),
            _dec2bcd(year % 100),
        ])
        self._i2c.writeto(self._addr, data)

    def get_time(self) -> tuple:
        """
        讀取時間，回傳 (year, month, day, hour, minute, second, weekday)
        year 為 2000 + 讀值
        """
        buf = self._read_reg(0x00, 7)
        second  = _bcd2dec(buf[0] & 0x7F)
        minute  = _bcd2dec(buf[1])
        hour    = _bcd2dec(buf[2] & 0x3F)   # 24h 模式
        weekday = _bcd2dec(buf[3])
        day     = _bcd2dec(buf[4])
        month   = _bcd2dec(buf[5] & 0x1F)   # 去掉世紀 bit
        year    = 2000 + _bcd2dec(buf[6])
        return year, month, day, hour, minute, second, weekday

    def get_temperature(self) -> float:
        """讀取晶片溫度（°C），精度 ±3°C"""
        buf = self._read_reg(0x11, 2)
        msb = buf[0]
        frac = (buf[1] >> 6) * 0.25
        # MSB bit7 為符號位
        if msb & 0x80:
            msb = msb - 256
        return msb + frac

    def datetime_str(self) -> str:
        y, mo, d, h, mi, s, wd = self.get_time()
        DAYS = ["", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        return "{:04d}-{:02d}-{:02d} {} {:02d}:{:02d}:{:02d}".format(
            y, mo, d, DAYS[wd], h, mi, s)


# ── 範例 1：讀取時間與溫度 ────────────────────────────────────
def read_time_demo():
    rtc = DS3231()
    print("DS3231 ready. Reading time every second.")
    while True:
        print("{} | {:.2f} °C".format(rtc.datetime_str(), rtc.get_temperature()))
        time.sleep(1)


# ── 範例 2：先設定時間再讀取 ─────────────────────────────────
def set_and_read_demo():
    """
    注意：若模組斷電後 lostPower，須先切斷模組電源讓其歸零，
    再重新上電並執行本函式設定時間（Arduino 課程中的注意事項同樣適用）
    """
    rtc = DS3231()
    # 設定為 2024-01-01 00:00:00 週一（weekday=2）
    rtc.set_time(2024, 1, 1, 0, 0, 0, weekday=2)
    print("Time set. Now reading:")
    while True:
        print("{} | {:.2f} °C".format(rtc.datetime_str(), rtc.get_temperature()))
        time.sleep(1)


# ── 主程式（選擇一種模式）────────────────────────────────────
read_time_demo()
# set_and_read_demo()
