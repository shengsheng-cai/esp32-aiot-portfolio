"""
紅外線接收與發射
Interface - ir_remote

原始課程: 22.ESP32_紅外線接收器 / 29.紅外線IR收發
平台: ESP32 MicroPython

功能:
  範例 1: IR 接收（VS1838B），印出 NEC 協議的 addr/data
  範例 2: IR 接收 → 控制 LED（按 0 鍵切換）
  範例 3: IR 發射，按鈕觸發發送一組 NEC 碼

依賴函式庫:
  micropython-ir（Peter Hinch）
  安裝: mpremote mip install github:peterhinch/micropython_ir
  接收端放 ir_rx/ 資料夾，發射端放 ir_tx/ 資料夾

NEC 協議格式:
  前導碼 9ms LOW + 4.5ms HIGH，接著 32 bit（addr8 + ~addr8 + cmd8 + ~cmd8）
  重複碼：前導碼後接 2.5ms HIGH（表示持續按住）

VS1838B 輸出為低電位有效（接收到信號時 OUT 拉 LOW）

硬體接線:
  VS1838B OUT → GPIO 23（PULL_UP 輸入）
  VS1838B VCC → 3.3V
  IR LED 陽極 → GPIO 22（串接 100Ω）
  IR LED 陰極 → GND
  按鈕（發射觸發）→ GPIO 13（PULL_UP）
  LED → GPIO 2（內建）
"""

import time
from machine import Pin

IR_RX_PIN  = 23
IR_TX_PIN  = 22
BTN_PIN    = 13
LED_PIN    = 2


# ── 範例 1：IR 接收，印出收到的碼 ─────────────────────────────
def ir_receive_demo():
    """
    接收 NEC 格式 IR 信號，印出 address 和 command
    需安裝 micropython-ir；ir_rx/ 資料夾放在 ESP32 根目錄
    """
    from ir_rx.nec import NEC_8

    def callback(data, addr, ctrl):
        if data > 0:   # 忽略重複碼（data=0）
            print("addr=0x{:02X}  cmd=0x{:02X}".format(addr, data))

    pin = Pin(IR_RX_PIN, Pin.IN, Pin.PULL_UP)
    ir  = NEC_8(pin, callback)

    print("IR RX ready. Waiting for signals...")
    while True:
        time.sleep_ms(100)


# ── 範例 2：IR 接收 → 控制 LED ─────────────────────────────────
def ir_led_control():
    """
    接收到 NEC cmd=0x45（遙控器「0」鍵）時切換內建 LED
    先執行 ir_receive_demo() 取得自己遙控器的 cmd 值，再修改 TARGET_CMD
    """
    from ir_rx.nec import NEC_8

    TARGET_CMD = 0x45   # 修改為實際遙控器按鍵對應的 cmd
    led = Pin(LED_PIN, Pin.OUT)

    def callback(data, addr, ctrl):
        if data == TARGET_CMD:
            led.value(not led.value())
            print("LED toggled. cmd=0x{:02X}".format(data))

    pin = Pin(IR_RX_PIN, Pin.IN, Pin.PULL_UP)
    ir  = NEC_8(pin, callback)

    print("IR LED control ready. Press button on remote...")
    while True:
        time.sleep_ms(100)


# ── 範例 3：IR 發射（NEC 格式）────────────────────────────────
def ir_transmit_demo():
    """
    按鈕按下後發射 NEC 格式 IR 信號
    需安裝 micropython-ir；ir_tx/ 資料夾放在 ESP32 根目錄
    """
    from ir_tx.nec import NEC

    TX_ADDR    = 0x00  # NEC 位址
    TX_CMD     = 0x45  # NEC 命令（與接收端對應）

    btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)
    ir  = NEC(Pin(IR_TX_PIN, Pin.OUT, value=0))

    print("IR TX ready. Press button to transmit NEC 0x{:02X}".format(TX_CMD))

    prev = 1
    while True:
        val = btn.value()
        if val == 0 and prev == 1:   # 下降沿
            ir.transmit(TX_ADDR, TX_CMD)
            print("Sent addr=0x{:02X} cmd=0x{:02X}".format(TX_ADDR, TX_CMD))
        prev = val
        time.sleep_ms(50)


# ── 主程式（選擇一種模式）────────────────────────────────────
ir_receive_demo()
# ir_led_control()
# ir_transmit_demo()
