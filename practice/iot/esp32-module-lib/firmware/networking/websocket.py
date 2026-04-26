"""
WebSocket 雙向通訊
Networking - websocket

原始課程: 45.ESP32 WebSocket
平台: ESP32 MicroPython

功能:
  範例 1: WebSocket LED 切換（瀏覽器按鈕 ↔ ESP32）
  範例 2: WebSocket 感測器串流（伺服器定時推送資料給所有客戶端）

ESP32 WebSocket 說明:
  Arduino ESPAsyncWebServer + AsyncWebSocket
    → MicroPython microdot + microdot.websocket
  ws.textAll()  廣播給所有客戶端
    → 逐一呼叫 ws.send() 給各連線
  ws.cleanupClients() 清理斷線客戶端
    → microdot 自動管理連線生命週期

依賴函式庫:
  microdot (v2.x) + websocket 支援
  安裝:
    mpremote mip install github:miguelgrinberg/microdot/src/microdot.py
    mpremote mip install github:miguelgrinberg/microdot/src/microdot_asyncio.py
    mpremote mip install github:miguelgrinberg/microdot/src/microdot_websocket.py

硬體接線:
  LED → GPIO 2（內建 LED）
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


# ── 範例 1：WebSocket LED 切換 ────────────────────────────────
INDEX_HTML = """\
<!DOCTYPE html><html>
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:Helvetica;text-align:center;margin-top:60px}
button{padding:16px 40px;border-radius:6px;border:none;
cursor:pointer;font-size:24px;background:#27ae60;color:white}
</style></head>
<body>
<h1>ESP32 WebSocket Server</h1>
<p>LED State: <b><span id="state">-</span></b></p>
<button onclick="sendToggle()">Toggle LED</button>
<script>
var ws = new WebSocket('ws://' + location.host + '/ws');
ws.onopen    = function()  { console.log('WS connected'); };
ws.onmessage = function(e) {
  document.getElementById('state').textContent = e.data == '1' ? 'ON' : 'OFF';
};
ws.onclose   = function()  { console.log('WS closed'); };
function sendToggle() { if (ws.readyState == 1) ws.send('toggle'); }
</script>
</body></html>
"""


def run_ws_led_server():
    """
    WebSocket LED 切換伺服器
    瀏覽器開啟 http://<ip>:80/ → 按 Toggle 按鈕 → ESP32 切換 LED
    """
    from microdot import Microdot
    from microdot.websocket import with_websocket

    app = Microdot()
    led = Pin(LED_PIN, Pin.OUT)
    led_state = [False]          # 用 list 以便 closure 修改

    @app.route("/")
    def index(request):
        return INDEX_HTML, 200, {"Content-Type": "text/html"}

    @app.route("/ws")
    @with_websocket
    async def ws_handler(request, ws):
        """接收 'toggle' 指令，切換 LED，廣播新狀態"""
        print("WebSocket client connected")
        # 送出初始狀態
        await ws.send("1" if led_state[0] else "0")

        while True:
            try:
                msg = await ws.receive()
            except Exception:
                break
            if msg == "toggle":
                led_state[0] = not led_state[0]
                led.value(1 if led_state[0] else 0)
                val = "1" if led_state[0] else "0"
                print("LED:", "ON" if led_state[0] else "OFF")
                await ws.send(val)

        print("WebSocket client disconnected")

    ip = connect_wifi()
    print("WebSocket LED server at http://{}:80/".format(ip))
    app.run(port=80, debug=True)


# ── 範例 2：WebSocket 感測器串流（定時推送）─────────────────
STREAM_HTML = """\
<!DOCTYPE html><html>
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:Helvetica;text-align:center;margin-top:60px}
#log{text-align:left;display:inline-block;width:300px;height:200px;
overflow-y:auto;border:1px solid #ccc;padding:8px;font-size:14px}
</style></head>
<body>
<h1>ESP32 Sensor Stream</h1>
<div id="log"></div>
<script>
var ws = new WebSocket('ws://' + location.host + '/stream');
ws.onmessage = function(e) {
  var log = document.getElementById('log');
  log.innerHTML += e.data + '<br>';
  log.scrollTop = log.scrollHeight;
};
</script>
</body></html>
"""


def run_ws_stream_server():
    """
    WebSocket 感測器串流：伺服器每秒主動推送模擬感測器資料
    瀏覽器開啟 http://<ip>:80/ 即可即時看到資料流
    """
    from microdot import Microdot
    from microdot.websocket import with_websocket
    import random

    app = Microdot()

    @app.route("/")
    def index(request):
        return STREAM_HTML, 200, {"Content-Type": "text/html"}

    @app.route("/stream")
    @with_websocket
    async def stream_handler(request, ws):
        print("Stream client connected")
        count = 0
        try:
            while True:
                # 模擬感測器值（實際可換成 DHT/ADC 讀值）
                temp  = 25.0 + random.uniform(-2, 2)
                humid = 60.0 + random.uniform(-5, 5)
                msg   = "#{} T={:.1f}°C H={:.1f}%".format(count, temp, humid)
                await ws.send(msg)
                print("Stream:", msg)
                count += 1
                await asyncio.sleep(1)
        except Exception:
            pass
        print("Stream client disconnected")

    ip = connect_wifi()
    print("WebSocket stream server at http://{}:80/".format(ip))
    app.run(port=80, debug=True)


# ── 主程式（選擇一種模式）────────────────────────────────────
run_ws_led_server()
# run_ws_stream_server()
