"""
ESP8266 ESP-01 AT 指令控制
Networking - esp01

原始課程: 37.ESP8266_ESP01
平台: ESP32 MicroPython（ESP32 透過 UART 控制 ESP-01）

功能:
  ESP-01 AT 指令透通（REPL ↔ ESP-01）
  WiFi 連接 + HTTP GET 上傳資料

ESP-01 常用 AT 指令:
  AT                  — 測試（回應 OK）
  AT+RST              — 重置模組
  AT+GMR              — 查看版本
  AT+UART=9600,8,1,0,0 — 設定鮑率
  AT+CWMODE=1         — STA 模式（2=AP, 3=STA+AP）
  AT+CWJAP="ssid","pass" — 連接 AP
  AT+CWJAP?           — 查詢當前連接
  AT+CIFSR            — 顯示 IP
  AT+CIPMUX=0         — 單通道連線
  AT+CIPSTART=0,"TCP","192.168.1.1",80 — 建立 TCP
  AT+CIPSEND=0,<len>  — 傳送資料

注意事項:
  - ESP-01 工作電壓 3.3V，VCC 和 CH_PD 都要接 3.3V
  - IO 雖可承受 3.3V，不可接 5V，否則模組燒燬
  - 預設鮑率依韌體版本而異，通常 9600 或 115200
  - 在 ESP32 上使用 ESP-01 實用性較低（ESP32 自帶 WiFi）
    本模組主要供 Arduino UNO 搭配 ESP-01 使用的課程參考

硬體接線（ESP32 ↔ ESP-01）:
  ESP-01 TX  → D16（ESP32 UART2 RX）
  ESP-01 RX  → D17（ESP32 UART2 TX）
  ESP-01 VCC → 3.3V（需能供應至少 200mA）
  ESP-01 CH_PD(EN) → 3.3V
  ESP-01 GND → GND
"""

import sys
import time
from machine import UART, Pin

ESP01_RX   = 16   # ESP32 UART2 RX ← ESP-01 TX
ESP01_TX   = 17   # ESP32 UART2 TX → ESP-01 RX
ESP01_BAUD = 115200  # 依 ESP-01 韌體設定（9600 或 115200）

WIFI_SSID = "your_ssid"
WIFI_PASS = "your_password"


def _send_at(uart: UART, cmd: str, wait_ms: int = 1000) -> str:
    """傳送 AT 指令，等待回應"""
    uart.write(cmd + "\r\n")
    time.sleep_ms(wait_ms)
    resp = b""
    while uart.any():
        resp += uart.read()
    decoded = resp.decode("utf-8", "ignore")
    print(">> " + cmd)
    print("<< " + decoded.strip())
    return decoded


# ── 範例 1：AT 指令透通 ───────────────────────────────────────
def at_passthrough():
    """
    REPL 輸入 AT 指令，轉發給 ESP-01 並印出回應
    輸入 quit 退出
    """
    uart = UART(2, baudrate=ESP01_BAUD, rx=ESP01_RX, tx=ESP01_TX)
    print("ESP-01 AT passthrough. Type AT commands. 'quit' to exit.")
    print("Baud:", ESP01_BAUD)

    while True:
        cmd = input("> ").strip()
        if cmd.lower() == "quit":
            break
        uart.write(cmd + "\r\n")
        time.sleep_ms(500)
        while uart.any():
            data = uart.read()
            print(data.decode("utf-8", "ignore"), end="")


# ── 範例 2：連接 WiFi 並以 GET 上傳資料 ─────────────────────
def http_get_demo(server_ip: str, path: str = "/api?value=42"):
    """
    ESP-01 連接 WiFi，建立 TCP 連線，發送 HTTP GET
    server_ip: 目標伺服器 IP（同區網）
    path: GET 路徑，如 /api?sensor=25
    """
    uart = UART(2, baudrate=ESP01_BAUD, rx=ESP01_RX, tx=ESP01_TX)

    _send_at(uart, "AT+RST",       wait_ms=3000)
    _send_at(uart, "AT+CWMODE=1",  wait_ms=500)
    _send_at(uart, 'AT+CWJAP="{}","{}"'.format(WIFI_SSID, WIFI_PASS), wait_ms=8000)
    _send_at(uart, "AT+CIFSR",     wait_ms=500)
    _send_at(uart, "AT+CIPMUX=0",  wait_ms=500)
    _send_at(uart, 'AT+CIPSTART=0,"TCP","{}",80'.format(server_ip), wait_ms=3000)

    get_cmd = "GET {} HTTP/1.1\r\nHost: {}\r\n\r\n".format(path, server_ip)
    _send_at(uart, "AT+CIPSEND=0,{}".format(len(get_cmd)), wait_ms=500)
    uart.write(get_cmd)
    time.sleep_ms(2000)
    while uart.any():
        print(uart.read().decode("utf-8", "ignore"), end="")

    print("\nGET sent to {}{}".format(server_ip, path))


# ── 主程式（選擇一種模式）────────────────────────────────────
at_passthrough()
# http_get_demo(server_ip="192.168.1.100", path="/api?temp=25")
