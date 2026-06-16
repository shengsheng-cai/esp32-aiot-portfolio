"""
Keypad 門禁 + DHT11 Web Server

平台: ESP32 系列 MicroPython

流程層:
  1) 啟動後背景連 WiFi，連上後啟動 HTTP server
  2) 瀏覽器可先開首頁，但溫濕度預設為 LOCKED
  3) Keypad 輸入 4321 再按 *（或 #）解鎖
  4) 解鎖後 /temperature、/humidity 才回傳真實值
"""

import dht
import network
import socket
import time
from machine import Pin

# 系統常數
HTTP_PORT = 80
HTTP_BACKLOG = 2
HTTP_RECV_BYTES = 1024
WIFI_RETRY_MS = 5000
MAIN_LOOP_DELAY_MS = 20

# Keypad / DHT 常數
KEY_DEBOUNCE_MS = 20
DHT11_MIN_INTERVAL_MS = 2000
PASSCODE = "4321"
DHT11_SDA_PIN = 4

# WiFi（真機測試請填入你的基地台帳密）
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

# Keypad 接線（保持你目前可用版本）
ROW_PINS = (13, 14, 15, 16)
COL_PINS = (17, 18, 19, 23)
KEYMAP = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"],
]

# 硬體初始化
rows = [Pin(p, Pin.IN, Pin.PULL_UP) for p in ROW_PINS]
cols = [Pin(p, Pin.OUT) for p in COL_PINS]
for col in cols:
    col.value(1)  # active-low：平時拉高，掃描時逐列拉低
sensor = dht.DHT11(Pin(DHT11_SDA_PIN))

# 全域狀態
input_code = ""
locker_state = "LOCKED"
last_pin_result = "N/A"
web_access_granted = False

wlan = None
server = None
last_wifi_retry_ms = 0
last_pressed_key = None

last_dht_ms = None
last_temp = "--"
last_hum = "--"

HTML = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ESP32 Locker DHT11</title>
  <style>
    html { font-family: Arial; text-align: center; }
    h2 { font-size: 2rem; margin-bottom: 0.6rem; }
    p { font-size: 1.2rem; margin: 0.4rem 0; }
    .v { font-weight: bold; }
  </style>
</head>
<body>
  <h2>ESP32 Locker + DHT11</h2>
  <p>Locker: <span id="locker" class="v">__LOCKER_STATE__</span></p>
  <p>Last PIN: <span id="pin_result" class="v">__PIN_RESULT__</span></p>
  <p>Temperature: <span id="temperature" class="v">--</span> &deg;C</p>
  <p>Humidity: <span id="humidity" class="v">--</span> %</p>
  <p>PIN: 4321 + *（或 #）解鎖；D 清除</p>
  <script>
    function update(id, url) {
      var x = new XMLHttpRequest();
      x.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          document.getElementById(id).textContent = this.responseText;
        }
      };
      x.open("GET", url, true);
      x.send();
    }
    function poll() {
      update("temperature", "/temperature");
      update("humidity", "/humidity");
    }
    poll();
    setInterval(poll, 10000);
  </script>
</body>
</html>
"""


def build_html():
    """流程層: 用目前門禁狀態組首頁 HTML。"""
    return HTML.replace("__LOCKER_STATE__", locker_state).replace(
        "__PIN_RESULT__", last_pin_result
    )


def scan_keypad_raw():
    """行為層: 掃描一次 4x4 keypad，回傳按鍵字元或 None。"""
    for c_idx, col in enumerate(cols):
        col.value(0)
        for r_idx, row in enumerate(rows):
            if row.value() == 0:
                col.value(1)
                return KEYMAP[r_idx][c_idx]
        col.value(1)
    return None


def get_key_event():
    """流程層: 單次按壓只觸發一次，避免按住連續觸發。"""
    global last_pressed_key
    key = scan_keypad_raw()

    if key is None:
        last_pressed_key = None
        return None

    if key == last_pressed_key:
        return None

    # 二次確認防彈跳
    time.sleep_ms(KEY_DEBOUNCE_MS)
    if scan_keypad_raw() != key:
        return None

    last_pressed_key = key
    return key


def read_dht_cached():
    """流程層: 2 秒快取保護，避免 DHT11 讀取過頻。"""
    global last_dht_ms, last_temp, last_hum
    now = time.ticks_ms()

    if (
        last_dht_ms is None
        or time.ticks_diff(now, last_dht_ms) >= DHT11_MIN_INTERVAL_MS
    ):
        try:
            sensor.measure()
            last_temp = str(sensor.temperature())
            last_hum = str(sensor.humidity())
        except OSError:
            last_temp = "--"
            last_hum = "--"
        last_dht_ms = now

    return last_temp, last_hum


def submit_pin():
    """流程層: 驗證 PIN 並更新門禁與網頁授權狀態。"""
    global input_code, locker_state, last_pin_result, web_access_granted

    success = input_code == PASSCODE
    input_code = ""

    if success:
        locker_state = "UNLOCKED"
        last_pin_result = "OK"
        web_access_granted = True
        temp, hum = read_dht_cached()
        print("[LOCKER] UNLOCKED | T:{} H:{}".format(temp, hum))
    else:
        locker_state = "LOCKED"
        last_pin_result = "FAIL"
        web_access_granted = False
        print("[LOCKER] FAIL")


def handle_keypad_once():
    """流程層: 處理一次 keypad 事件。"""
    global input_code
    key = get_key_event()
    if key is None:
        return

    if key == "D":
        input_code = ""
        print("[PIN] Cleared")
        return

    if key in ("*", "#"):
        submit_pin()
        return

    if len(input_code) < len(PASSCODE):
        input_code += key
    print("[PIN] " + "*" * len(input_code))


def init_wifi():
    """流程層: 初始化 WiFi 並發出第一次連線請求。"""
    global wlan, last_wifi_retry_ms
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    last_wifi_retry_ms = time.ticks_ms()
    print("[WiFi] Background connect started.")
    print("[LOCKER] Ready. Enter PIN, 'D' clear, '*' or '#' submit.")


def start_server(ip):
    """行為層: 啟動非阻塞 HTTP server。"""
    addr = socket.getaddrinfo(ip, HTTP_PORT)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(HTTP_BACKLOG)
    s.setblocking(False)
    print("Server running at http://{}".format(ip))
    return s


def maintain_wifi_and_server(now_ms):
    """流程層: 背景維護 WiFi，連上後啟動 server。"""
    global last_wifi_retry_ms, server

    if wlan is None:
        return

    if wlan.isconnected():
        if server is None:
            ip = wlan.ifconfig()[0]
            print("WiFi Connected:", ip)
            server = start_server(ip)
        return

    if time.ticks_diff(now_ms, last_wifi_retry_ms) >= WIFI_RETRY_MS:
        try:
            wlan.connect(SSID, PASSWORD)
        except OSError:
            pass
        last_wifi_retry_ms = now_ms
        print("[WiFi] Retry connect...")


def get_request_path(request):
    """行為層: 解析 HTTP request path。"""
    first_line = request.split("\r\n", 1)[0]
    parts = first_line.split(" ")
    return parts[1] if len(parts) >= 2 else "/"


def get_http_response(path):
    """流程層: 依路由與授權狀態回傳內容。"""
    if path == "/temperature":
        if web_access_granted:
            return "text/plain", read_dht_cached()[0]
        return "text/plain", "LOCKED"

    if path == "/humidity":
        if web_access_granted:
            return "text/plain", read_dht_cached()[1]
        return "text/plain", "LOCKED"

    return "text/html", build_html()


def send_response(conn, content_type, body):
    """行為層: 傳送 HTTP 200 回應。"""
    payload = (
        "HTTP/1.1 200 OK\r\nContent-Type: {}\r\nConnection: close\r\n\r\n{}"
    ).format(content_type, body)
    conn.send(payload.encode())


def handle_http_once():
    """流程層: 每輪最多處理一個 HTTP 連線。"""
    if server is None:
        return

    try:
        conn, _ = server.accept()
    except OSError:
        return

    try:
        try:
            conn.settimeout(0.05)
        except AttributeError:
            pass

        request = conn.recv(HTTP_RECV_BYTES).decode()
        path = get_request_path(request)
        content_type, body = get_http_response(path)
        send_response(conn, content_type, body)
    except OSError:
        pass
    finally:
        conn.close()


def main():
    """程式入口: 輪詢 keypad + WiFi + HTTP。"""
    init_wifi()

    while True:
        now_ms = time.ticks_ms()
        handle_keypad_once()
        maintain_wifi_and_server(now_ms)
        handle_http_once()
        time.sleep_ms(MAIN_LOOP_DELAY_MS)


main()
