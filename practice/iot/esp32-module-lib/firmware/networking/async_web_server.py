"""
非同步 Web Server + 靜態文件服務
Networking - async_web_server

原始課程: 37.AsyncWebServer非同步網頁伺服器 / 38.ESP32 Web Server SPIFFS
平台: ESP32 MicroPython

功能:
  範例 1: 基礎非同步 Web Server（純文字 Hello World）
  範例 2: LED 控制（HTML 內嵌，帶 URL 參數處理）
  範例 3: 靜態文件服務（從 /www/ 讀取 HTML/CSS，替代 SPIFFS）

替代說明:
  Arduino ESPAsyncWebServer → MicroPython microdot（非同步 web 框架）
  Arduino SPIFFS             → ESP32 文件系統（直接 open('/www/index.html')）
  PROGMEM R"rawliteral"     → Python 多行字串或外部 .html 檔案

依賴函式庫:
  microdot (v2.x)
  安裝: mpremote mip install github:miguelgrinberg/microdot/src/microdot.py
       mpremote mip install github:miguelgrinberg/microdot/src/microdot_asyncio.py

SPIFFS → 文件系統對比:
  Arduino: 將 /data 資料夾上傳至 SPIFFS（需插件）
  MicroPython: 用 mpremote cp html/index.html :/www/index.html 上傳

硬體接線:
  LED → D2（內建 LED）
"""

import asyncio
import network
import time
from machine import Pin

WIFI_SSID = "your_ssid"
WIFI_PASS = "your_password"
LED_PIN   = 2


def connect_wifi() -> str:
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(WIFI_SSID, WIFI_PASS)
    print("Connecting", end="")
    for _ in range(20):
        if sta.isconnected():
            ip = sta.ifconfig()[0]
            print("\nConnected! IP:", ip)
            return ip
        print(".", end="")
        time.sleep(1)
    raise OSError("WiFi failed")


# ── 範例 1：Hello World ───────────────────────────────────────
def run_hello_server():
    from microdot import Microdot

    app = Microdot()

    @app.route("/")
    def index(request):
        return "Hello World! (MicroPython microdot)"

    @app.route("/json")
    def json_endpoint(request):
        return {"status": "ok", "msg": "Hello from ESP32"}

    ip = connect_wifi()
    print("Microdot server at http://{}:5000/".format(ip))
    app.run(port=5000)


# ── 範例 2：LED 控制（URL 路徑 + HTML 回應）─────────────────
LED_PAGE = """\
<!DOCTYPE html><html>
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font-family:Helvetica;text-align:center;margin-top:60px}}
a.btn{{display:inline-block;padding:16px 40px;border-radius:6px;
color:white;text-decoration:none;font-size:24px;background:{color}}}
</style></head>
<body>
<h1>ESP32 Async Web Server</h1>
<p>LED: <b>{state}</b></p>
<a class="btn" href="/led/{action}">{label}</a>
</body></html>"""


def run_led_server():
    from microdot import Microdot

    app = Microdot()
    led = Pin(LED_PIN, Pin.OUT)

    def led_page(state: bool) -> str:
        return LED_PAGE.format(
            state="ON" if state else "OFF",
            action="off" if state else "on",
            label="Turn OFF" if state else "Turn ON",
            color="#c0392b" if state else "#27ae60",
        )

    @app.route("/")
    def index(request):
        return led_page(led.value()), 200, {"Content-Type": "text/html"}

    @app.route("/led/on")
    def led_on(request):
        led.value(1)
        return led_page(True), 200, {"Content-Type": "text/html"}

    @app.route("/led/off")
    def led_off(request):
        led.value(0)
        return led_page(False), 200, {"Content-Type": "text/html"}

    SAFE_PINS = {2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33}

    @app.route("/update")
    def update(request):
        """URL 參數版本：/update?output=2&state=1"""
        output = int(request.args.get("output", 2))
        state  = int(request.args.get("state",  0))
        if output not in SAFE_PINS:
            return "Invalid pin", 400
        Pin(output, Pin.OUT).value(state)
        return "OK"

    ip = connect_wifi()
    print("LED server at http://{}:80/".format(ip))
    app.run(port=80)


# ── 範例 3：靜態文件服務（替代 SPIFFS）─────────────────────
def run_static_server():
    """
    從 ESP32 文件系統 /www/ 目錄讀取 HTML 文件
    使用方法：
      1. 在本地建立 www/index.html 和 www/style.css
      2. 上傳：mpremote cp -r www :/www
      3. 執行此函式
    """
    from microdot import Microdot
    import os

    app = Microdot()

    def read_file(path: str) -> str:
        with open(path, "r") as f:
            return f.read()

    @app.route("/")
    def index(request):
        try:
            html = read_file("/www/index.html")
            # 替換模板變數（相當於 SPIFFS processor）
            led_state = "ON" if Pin(LED_PIN).value() else "OFF"
            html = html.replace("%STATE%", led_state)
            return html, 200, {"Content-Type": "text/html"}
        except OSError:
            return "index.html not found in /www/", 404

    @app.route("/style.css")
    def css(request):
        try:
            return read_file("/www/style.css"), 200, {"Content-Type": "text/css"}
        except OSError:
            return "", 404

    @app.route("/on")
    def led_on(request):
        Pin(LED_PIN, Pin.OUT).value(1)
        html = read_file("/www/index.html").replace("%STATE%", "ON")
        return html, 200, {"Content-Type": "text/html"}

    @app.route("/off")
    def led_off(request):
        Pin(LED_PIN, Pin.OUT).value(0)
        html = read_file("/www/index.html").replace("%STATE%", "OFF")
        return html, 200, {"Content-Type": "text/html"}

    # 列出文件系統上的檔案（除錯用）
    try:
        print("Files in /www/:", os.listdir("/www"))
    except OSError:
        print("/www/ directory not found. Upload HTML files first.")

    ip = connect_wifi()
    print("Static server at http://{}:80/".format(ip))
    app.run(port=80)


# ── 主程式（選擇一種模式）────────────────────────────────────
# run_hello_server()
run_led_server()
# run_static_server()
