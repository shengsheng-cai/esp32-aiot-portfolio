"""
七段顯示器
Interface - seven_segment

原始課程: 14.七段顯示器與74HC595移位暫存器 / 16.四位數七段顯示器 /
          43.ESP32 七段顯示時鐘模組 TM1637
平台: ESP32 MicroPython

功能:
  範例 1: 直接 GPIO 控制共陽四位數七段（多工掃描）
  範例 2: 74HC595 移位暫存器 + 共陰四位數七段（bitbang SPI）
  範例 3: TM1637 模組計數 / 軟體時鐘（需安裝 micropython-tm1637）

74HC595 操作流程:
  STCP LOW → 送 8 bit 資料（SH_CP 時脈）→ STCP HIGH（鎖存輸出）

硬體接線（範例 1 - 直接 GPIO，共陽）:
  a,b,c,d,e,f,g → D2, D4, D5, D12, D13, D14, D15
  COM D1~D4 → D16, D17, D18, D19（HIGH = 選中）

硬體接線（範例 2 - 74HC595，共陰）:
  SH_CP(CLK)  → D18
  ST_CP(LATCH)→ D19
  DS(DATA)    → D23
  COM D1~D4   → D16, D17, D21, D22（LOW = 選中）
  74HC595 MR  → 3.3V（不重置），OE → GND（輸出致能）

硬體接線（範例 3 - TM1637）:
  CLK → D22
  DIO → D23
"""

import time
from machine import Pin

# ── 範例 1：直接 GPIO 控制共陽四位數七段 ──────────────────────

SEG_PINS        = [2, 4, 5, 12, 13, 14, 15]  # a,b,c,d,e,f,g
COM_PINS_ANODE  = [16, 17, 18, 19]           # D1,D2,D3,D4

# 共陽數字表（bit 0=a … bit 6=g；0=LOW=亮）
DIGITS_ANODE = [
    0b0000001,  # 0
    0b1001111,  # 1
    0b0010010,  # 2
    0b0000110,  # 3
    0b1001100,  # 4
    0b0100100,  # 5
    0b0100000,  # 6
    0b0001111,  # 7
    0b0000000,  # 8
    0b0000100,  # 9
]


def _split_digits(number: int) -> list:
    return [
        number // 1000 % 10,
        number // 100  % 10,
        number // 10   % 10,
        number         % 10,
    ]


def direct_gpio_demo(number: int = 1234):
    """直接 GPIO 多工掃描，顯示四位整數（共陽）"""
    segs = [Pin(p, Pin.OUT) for p in SEG_PINS]
    coms = [Pin(p, Pin.OUT) for p in COM_PINS_ANODE]

    for s in segs: s.value(1)  # 全段滅
    for c in coms: c.value(0)  # 全位滅

    digits = _split_digits(number)
    print("Displaying:", number)

    while True:
        for pos, d in enumerate(digits):
            for c in coms: c.value(0)            # 關所有位
            bits = DIGITS_ANODE[d]
            for i, s in enumerate(segs):
                s.value((bits >> i) & 1)
            coms[pos].value(1)                   # 選中此位
            time.sleep_ms(2)


# ── 範例 2：74HC595 + 共陰四位數七段 ──────────────────────────

CLK_PIN          = 18
LATCH_PIN        = 19
DATA_PIN         = 23
COM_PINS_CATHODE = [16, 17, 21, 22]  # D1~D4（LOW = 選中）

# 共陰數字表（LSBFIRST；bit0=a … bit7=dp）
DIGITS_CATHODE = [
    0b11111100,  # 0
    0b01100000,  # 1
    0b11011010,  # 2
    0b11110010,  # 3
    0b01100110,  # 4
    0b10110110,  # 5
    0b10111110,  # 6
    0b11100000,  # 7
    0b11111110,  # 8
    0b11110110,  # 9
]


def _shift_out_lsb(data_pin, clk_pin, latch_pin, val):
    """74HC595 bitbang：LSBFIRST，STCP 上升沿鎖存"""
    latch_pin.value(0)
    for i in range(8):
        data_pin.value((val >> i) & 1)
        clk_pin.value(1)
        clk_pin.value(0)
    latch_pin.value(1)


def hc595_demo(number: int = 1234):
    """74HC595 多工掃描，顯示四位整數（共陰）"""
    clk   = Pin(CLK_PIN,   Pin.OUT)
    latch = Pin(LATCH_PIN, Pin.OUT)
    data  = Pin(DATA_PIN,  Pin.OUT)
    coms  = [Pin(p, Pin.OUT) for p in COM_PINS_CATHODE]

    for c in coms: c.value(1)  # 全位滅

    digits = _split_digits(number)
    print("Displaying:", number)

    while True:
        for pos, d in enumerate(digits):
            for c in coms: c.value(1)                      # 關所有位
            _shift_out_lsb(data, clk, latch, DIGITS_CATHODE[d])
            coms[pos].value(0)                             # 選中此位
            time.sleep_ms(2)


# ── 範例 3：TM1637 模組 ────────────────────────────────────────
# 需安裝 micropython-tm1637（tm1637.py 放入 ESP32 根目錄）
# https://github.com/mcauser/micropython-tm1637

TM_CLK = 22
TM_DIO = 23


def tm1637_demo():
    """TM1637 計數顯示，0000 → 9999 循環"""
    import tm1637
    tm = tm1637.TM1637(clk=Pin(TM_CLK), dio=Pin(TM_DIO))
    tm.brightness(7)

    print("TM1637 counting demo")
    n = 0
    while True:
        tm.number(n)
        time.sleep_ms(500)
        n = (n + 1) % 10000


def tm1637_clock(start_hour: int = 12, start_min: int = 0):
    """
    TM1637 軟體計時時鐘（無需 NTP）
    冒號每 500ms 閃爍
    """
    import tm1637
    tm = tm1637.TM1637(clk=Pin(TM_CLK), dio=Pin(TM_DIO))
    tm.brightness(7)

    hour, minute, second = start_hour, start_min, 0
    last_tick = time.ticks_ms()
    colon = False

    print("Clock started at {:02d}:{:02d}:00".format(hour, minute))

    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_tick) >= 1000:
            second += 1
            if second >= 60:
                second = 0
                minute += 1
            if minute >= 60:
                minute = 0
                hour = (hour + 1) % 24
            last_tick = now

        colon = not colon
        tm.numbers(hour, minute, colon=colon)
        time.sleep_ms(500)


# ── 主程式（選擇一種模式）────────────────────────────────────
# direct_gpio_demo(1234)
# hc595_demo(5678)
# tm1637_demo()
tm1637_clock(start_hour=12, start_min=0)
