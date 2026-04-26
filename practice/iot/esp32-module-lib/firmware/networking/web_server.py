"""
HTTP Web Server (raw socket)
Networking - web_server

原始課程: 27.建立http web server / 28.ESP32 WiFi.h建立Web Server 點亮LED /
          29.建立SoftAP_使用ESP32 WebServer函式庫 / 30.ESP32 arg函式讀取URL資料
平台: ESP32 MicroPython

功能:
  範例 1: 基礎 HTTP Server（顯示 Hello World）
  範例 2: LED 控制 Web Server（URL 路徑 /led/on 、/led/off）
  範例 3: URL 查詢參數解析（?a=1&b=2）

工作原理:
  使用 socket 建立 TCP server，接收 HTTP GET request，
  解析路徑後回傳 HTML 字串，行為等同 Arduino WebServer.h

WiFi 模式選擇:
  STA 模式 — 連接到家庭 WiFi，所有同網路裝置可存取
  AP 模式  — ESP32 自建 WiFi，手機/電腦直連（無需路由器）

硬體接線:
  LED → GPIO 2（內建 LED）
"""

import socket
import time
import network
from machine import Pin

WIFI_SSID = "your_ssid"
WIFI_PASS = "your_password"
AP_SSID   = "ESP32-AP"
AP_PASS   = "12345678"
PORT      = 80
LED_PIN   = 2


def connect_wifi(ssid: str = WIFI_SSID, password: str = WIFI_PASS) -> str:
    """連接 WiFi STA 模式，回傳 IP"""
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, password)
    print("Connecting", end="")
    for _ in range(20):
        if sta.isconnected():
            ip = sta.ifconfig()[0]
            print("\nConnected! IP:", ip)
            return ip
        print(".", end="")
        time.sleep(1)
    raise OSError("WiFi connection failed")


def start_soft_ap(ssid: str = AP_SSID, password: str = AP_PASS) -> str:
    """啟動 SoftAP 模式，回傳 IP"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password)
    ip = ap.ifconfig()[0]
    print("SoftAP started. SSID: {}  IP: {}".format(ssid, ip))
    return ip


def _parse_request(raw: str) -> tuple:
    """
    解析 HTTP request 第一行
    回傳 (path, query_dict)
    例：GET /?a=1&b=2 HTTP/1.1
    → ("/", {"a": "1", "b": "2"})
    """
    try:
        first_line = raw.split("\r\n")[0]
        path_full  = first_line.split(" ")[1]  # e.g. "/led/on?x=1"
    except IndexError:
        return "/", {}

    if "?" in path_full:
        path, qs = path_full.split("?", 1)
        args = {}
        for pair in qs.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                args[k] = v
    else:
        path, args = path_full, {}

    return path, args


def _led_page(state: bool) -> str:
    on_off = "ON" if state else "OFF"
    btn_href  = "/led/off" if state else "/led/on"
    btn_label = "Turn OFF" if state else "Turn ON"
    btn_color = "#c0392b" if state else "#27ae60"
    return (
        "<!DOCTYPE html><html><head>"
        "<meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<style>body{{font-family:Helvetica;text-align:center;margin-top:60px}}"
        "a.btn{{display:inline-block;padding:16px 40px;background:{};color:white;"
        "border-radius:6px;text-decoration:none;font-size:24px}}</style></head>"
        "<body><h1>ESP32 Web Server</h1>"
        "<p>LED Status: <b>{}</b></p>"
        "<a class='btn' href='{}'>{}</a>"
        "</body></html>"
    ).format(btn_color, on_off, btn_href, btn_label)


# ── 範例 1：Hello World ───────────────────────────────────────
def hello_world_server(ip: str):
    s = socket.socket()
    s.bind(("", PORT))
    s.listen(5)
    print("Server at http://{}:{}/".format(ip, PORT))

    while True:
        conn, addr = s.accept()
        conn.recv(1024)
        conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(b"<html><body>Hello World!<br>ESP32 MicroPython</body></html>")
        conn.close()


# ── 範例 2：LED 控制 ──────────────────────────────────────────
def led_control_server(ip: str):
    led   = Pin(LED_PIN, Pin.OUT)
    state = False

    s = socket.socket()
    s.bind(("", PORT))
    s.listen(5)
    print("LED server at http://{}:{}/".format(ip, PORT))
    print("  /led/on  — turn LED on")
    print("  /led/off — turn LED off")

    while True:
        conn, addr = s.accept()
        raw  = conn.recv(1024).decode("utf-8", "ignore")
        path, _ = _parse_request(raw)

        if path == "/led/on":
            state = True
            led.value(1)
        elif path == "/led/off":
            state = False
            led.value(0)

        html = _led_page(state)
        conn.send(("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html).encode())
        conn.close()


# ── 範例 3：URL 參數解析 ─────────────────────────────────────
def arg_demo_server(ip: str):
    """
    瀏覽器輸入 http://<ip>/?a=1&b=hello
    印出解析結果
    """
    s = socket.socket()
    s.bind(("", PORT))
    s.listen(5)
    print("Arg demo at http://{}:{}/".format(ip, PORT))
    print("Try: http://{}/?a=1&b=hello".format(ip))

    while True:
        conn, addr = s.accept()
        raw  = conn.recv(1024).decode("utf-8", "ignore")
        path, args = _parse_request(raw)
        print("path={} args={}".format(path, args))

        body = "<h2>URL Args</h2>"
        for k, v in args.items():
            body += "<p>{} = {}</p>".format(k, v)

        conn.send(("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html>" + body + "</html>").encode())
        conn.close()


# ── 主程式（選擇一種模式）────────────────────────────────────
# STA 模式
ip = connect_wifi()
led_control_server(ip)

# AP 模式（不需要外部 WiFi）
# ip = start_soft_ap()
# led_control_server(ip)
