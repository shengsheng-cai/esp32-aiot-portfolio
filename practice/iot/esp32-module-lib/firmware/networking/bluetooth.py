"""
藍牙通訊
Networking - bluetooth

原始課程: 24.ESP32 藍芽SPP / 35.藍芽HC-05
平台: ESP32 MicroPython

功能:
  範例 1: BLE Nordic UART Service (NUS) — 替代 Classic BT SPP
  範例 2: HC-05 外接藍牙模組 UART 透通

MicroPython 藍牙說明:
  標準 MicroPython 固件只支援 BLE（Bluetooth Low Energy）
  不支援 Classic BT（SPP / BluetoothSerial.h）
  BLE NUS（Nordic UART Service）是手機 APP 與 BLE 裝置通訊的常用 Profile
  支援的手機 APP：nRF Toolbox、Serial Bluetooth Terminal（選 BLE UART）

NUS Service UUID:
  Service: 6E400001-B5A3-F393-E0A9-E50E24DCCA9E
  RX (接收): 6E400002-... (write)
  TX (發送): 6E400003-... (notify)

HC-05 AT 常用指令（進入 AT 模式：長按 KEY 按鈕後通電）:
  AT           — 測試（回應 OK）
  AT+VERSION?  — 韌體版本
  AT+NAME=TSDE — 設定名稱
  AT+PSWD=1234 — 設定配對碼
  AT+UART=9600,0,0 — 設定透通鮑率
  AT+ADDR?     — 查詢位址
  AT+ROLE=1    — 設為主機（0=從機）
  AT+ORGL      — 恢復預設設定

HC-05 AT 模式固定鮑率 38400，透通模式鮑率依設定（預設 V2=38400、V3=9600）

硬體接線（範例 2 - HC-05）:
  HC-05 TXD → D16（ESP32 UART2 RX）
  HC-05 RXD → D17（ESP32 UART2 TX）
  HC-05 VCC → 5V（或 3.3V，視模組版本）
  HC-05 GND → GND
"""

import time
import bluetooth
from machine import Pin, UART

LED_PIN = 2

# ── 範例 1：BLE Nordic UART Service ──────────────────────────
NUS_SVC_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
NUS_RX_UUID  = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
NUS_TX_UUID  = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

_FLAG_NOTIFY = 0x0010
_FLAG_WRITE  = 0x0008

_NUS_SERVICE = (
    NUS_SVC_UUID,
    (
        (NUS_TX_UUID, _FLAG_NOTIFY),   # 0: ESP32 → 手機（notify）
        (NUS_RX_UUID, _FLAG_WRITE),    # 1: 手機 → ESP32（write）
    ),
)


def ble_uart_demo(device_name: str = "ESP32-BLE"):
    """
    BLE Nordic UART Service
    - 手機 APP 傳來的資料印到 REPL
    - 每秒向手機發送一行計數資料
    支援的手機 APP: nRF Toolbox > UART、Serial Bluetooth Terminal（選 BLE UART）
    """
    ble = bluetooth.BLE()
    ble.active(True)

    ((tx_handle, rx_handle),) = ble.gatts_register_services((_NUS_SERVICE,))

    _conn_handle = [None]
    _buf = bytearray()

    def _irq(event, data):
        if event == 1:   # Central connected
            _conn_handle[0] = data[0]
            print("BLE connected, handle:", _conn_handle[0])
        elif event == 2:  # Central disconnected
            _conn_handle[0] = None
            print("BLE disconnected, advertising again...")
            _advertise()
        elif event == 3:  # Write
            val = ble.gatts_read(rx_handle)
            msg = val.decode("utf-8", "ignore").strip()
            print("Received:", msg)
            _buf.extend(val)

    def _advertise():
        name_enc = device_name.encode()
        # AD: flags + complete local name
        adv = bytes([2, 0x01, 0x06, len(name_enc) + 1, 0x09]) + name_enc
        ble.gap_advertise(100_000, adv_data=adv)
        print("BLE advertising as '{}'".format(device_name))

    ble.irq(_irq)
    _advertise()

    count = 0
    while True:
        if _conn_handle[0] is not None:
            msg = "count: {}\n".format(count)
            ble.gatts_notify(_conn_handle[0], tx_handle, msg.encode())
            count += 1
        time.sleep_ms(1000)


# ── 範例 2：HC-05 UART 透通 ───────────────────────────────────
HC05_RX = 16   # ESP32 UART2 RX ← HC-05 TXD
HC05_TX = 17   # ESP32 UART2 TX → HC-05 RXD
HC05_BAUD = 9600   # 依 HC-05 AT+UART? 設定值填寫（V3 預設 9600）


def hc05_passthrough():
    """
    HC-05 透通：ESP32 橋接 USB Serial ↔ HC-05 UART
    電腦端終端機輸入 → 藍牙發送
    藍牙接收 → 電腦端終端機輸出

    進入 AT 模式：長按 KEY 後通電（鮑率自動切到 38400）
    透通模式：鮑率依 AT+UART 設定
    """
    import sys

    uart = UART(2, baudrate=HC05_BAUD, rx=HC05_RX, tx=HC05_TX)
    led  = Pin(LED_PIN, Pin.OUT)

    print("HC-05 passthrough ready. Baud={}".format(HC05_BAUD))

    while True:
        # HC-05 → REPL
        if uart.any():
            data = uart.read()
            if data:
                led.value(1)
                print(data.decode("utf-8", "ignore"), end="")
                led.value(0)

        # REPL → HC-05（透過 stdin 逐字讀取）
        if sys.stdin in __import__('select').select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)
            uart.write(ch)

        time.sleep_ms(10)


# ── 主程式（選擇一種模式）────────────────────────────────────
ble_uart_demo(device_name="ESP32-BLE")
# hc05_passthrough()
