"""
DS1302 實時時鐘模組
Time - ds1302

原始課程: 21.ESP32_DS1302時鐘模組 / 28.DS1302時鐘模組
平台: ESP32 MicroPython

功能:
  範例 1: 讀取目前時間（每秒輸出）
  範例 2: 設定時間後持續讀取

DS1302 說明:
  三線同步串行協議（非 SPI/I2C）：CLK、DAT（雙向）、RST
  時間資料以 BCD 格式儲存
  備用電池（CR2032）斷電後仍保持計時

Arduino RtcDS1302 / DS1302 函式庫 → MicroPython bit-bang 自行實現協議

寄存器位址（bit-bang cmd）:
  秒 0x00  分 0x01  時 0x02  日 0x03
  月 0x04  週 0x05  年 0x06  寫保護 0x07

硬體接線:
  DS1302 CLK  → D5
  DS1302 DAT  → D4
  DS1302 RST  → D2
  DS1302 VCC  → 3.3V（或 5V）
  DS1302 GND  → GND
"""

import time
from machine import Pin

CLK_PIN = 5
DAT_PIN = 4
RST_PIN = 2


def _bcd2dec(bcd: int) -> int:
    return (bcd >> 4) * 10 + (bcd & 0x0F)


def _dec2bcd(dec: int) -> int:
    return (dec // 10) << 4 | (dec % 10)


class DS1302:
    def __init__(self, clk=CLK_PIN, dat=DAT_PIN, rst=RST_PIN):
        self._clk = Pin(clk, Pin.OUT)
        self._dat = Pin(dat, Pin.OUT)
        self._rst = Pin(rst, Pin.OUT)
        self._rst.value(0)
        self._clk.value(0)
        # 關閉寫保護
        self._write_reg(0x07, 0x00)

    def _write_byte(self, byte: int):
        self._dat = Pin(self._dat.id(), Pin.OUT)
        for _ in range(8):
            self._dat.value(byte & 0x01)
            byte >>= 1
            self._clk.value(1)
            self._clk.value(0)

    def _read_byte(self) -> int:
        self._dat = Pin(self._dat.id(), Pin.IN)
        byte = 0
        for i in range(8):
            byte |= (self._dat.value() << i)
            self._clk.value(1)
            self._clk.value(0)
        return byte

    def _write_reg(self, addr: int, val: int):
        cmd = 0x80 | (addr << 1)   # write command
        self._rst.value(1)
        self._write_byte(cmd)
        self._write_byte(val)
        self._rst.value(0)

    def _read_reg(self, addr: int) -> int:
        cmd = 0x81 | (addr << 1)   # read command
        self._rst.value(1)
        self._write_byte(cmd)
        val = self._read_byte()
        self._rst.value(0)
        return val

    def set_time(self, year: int, month: int, day: int,
                 hour: int, minute: int, second: int, weekday: int = 1):
        """
        設定時間
        year: 完整年份（如 2024）
        weekday: 1=週日 … 7=週六（DS1302 慣例）
        """
        self._write_reg(0x00, _dec2bcd(second))
        self._write_reg(0x01, _dec2bcd(minute))
        self._write_reg(0x02, _dec2bcd(hour))       # 24h 模式
        self._write_reg(0x03, _dec2bcd(day))
        self._write_reg(0x04, _dec2bcd(month))
        self._write_reg(0x05, _dec2bcd(weekday))
        self._write_reg(0x06, _dec2bcd(year % 100))

    def get_time(self) -> tuple:
        """
        讀取時間，回傳 (year, month, day, hour, minute, second, weekday)
        year 為 2000 + 讀值
        """
        sec     = _bcd2dec(self._read_reg(0x00) & 0x7F)  # 去掉 CH bit
        minute  = _bcd2dec(self._read_reg(0x01))
        hour    = _bcd2dec(self._read_reg(0x02) & 0x3F)  # 24h 模式
        day     = _bcd2dec(self._read_reg(0x03))
        month   = _bcd2dec(self._read_reg(0x04))
        weekday = _bcd2dec(self._read_reg(0x05))
        year    = 2000 + _bcd2dec(self._read_reg(0x06))
        return year, month, day, hour, minute, sec, weekday

    def datetime_str(self) -> str:
        y, mo, d, h, mi, s, wd = self.get_time()
        DAYS = ["", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        return "{:04d}-{:02d}-{:02d} {} {:02d}:{:02d}:{:02d}".format(
            y, mo, d, DAYS[wd], h, mi, s)


# ── 範例 1：讀取目前時間 ──────────────────────────────────────
def read_time_demo():
    rtc = DS1302()
    print("DS1302 ready. Reading time every second.")
    while True:
        print(rtc.datetime_str())
        time.sleep(1)


# ── 範例 2：先設定時間再讀取 ─────────────────────────────────
def set_and_read_demo():
    """
    第一次使用時執行此函式設定時間
    設定完成後改用 read_time_demo() 即可
    """
    rtc = DS1302()
    # 設定為 2024-01-01 00:00:00 週一（weekday=2）
    rtc.set_time(2024, 1, 1, 0, 0, 0, weekday=2)
    print("Time set. Now reading:")
    while True:
        print(rtc.datetime_str())
        time.sleep(1)


# ── 主程式（選擇一種模式）────────────────────────────────────
read_time_demo()
# set_and_read_demo()
