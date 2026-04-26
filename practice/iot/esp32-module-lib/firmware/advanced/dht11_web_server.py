"""
DHT11 Web Server
Advanced - ESP32 網頁溫濕度顯示

原始課程: 40.ESP32 DHT11 Web Server
平台: ESP32 MicroPython

功能:
  ESP32 連上 WiFi 後啟動 HTTP 伺服器
  瀏覽器開啟 ESP32 IP 即可查看溫濕度
  網頁每 10 秒自動更新

硬體接線:
  DHT11 DATA → GPIO 23
  DHT11 VCC  → 3.3V
  DHT11 GND  → GND

使用說明:
  1. 修改下方 SSID 與 PASSWORD
  2. 燒錄後開啟序列埠監控，取得 ESP32 IP
  3. 瀏覽器輸入該 IP 即可查看
"""

import network
import socket
import dht
import time
from machine import Pin

# ── WiFi 設定 ────────────────────────────────────────────────
SSID     = "your_ssid"
PASSWORD = "your_password"

# ── 硬體初始化 ───────────────────────────────────────────────
sensor = dht.DHT11(Pin(23))

# ── 網頁模板 ─────────────────────────────────────────────────
HTML = """\
<!DOCTYPE HTML><html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ESP32 DHT Server</title>
  <style>
    html { font-family: Arial; text-align: center; }
    h2   { font-size: 3rem; }
    p    { font-size: 3rem; }
    .units { font-size: 1.2rem; }
    .label { font-size: 1.5rem; vertical-align: middle; }
  </style>
</head>
<body>
  <h2>ESP32 DHT Server</h2>
  <p><span class="label">Temperature</span>
     <span id="temperature">--</span>
     <sup class="units">&deg;C</sup></p>
  <p><span class="label">Humidity</span>
     <span id="humidity">--</span>
     <sup class="units">%</sup></p>
  <script>
    function update(id, url) {
      var x = new XMLHttpRequest();
      x.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200)
          document.getElementById(id).innerHTML = this.responseText;
      };
      x.open('GET', url, true);
      x.send();
    }
    setInterval(function() { update('temperature', '/temperature'); }, 10000);
    setInterval(function() { update('humidity',    '/humidity');    }, 10000);
    update('temperature', '/temperature');
    update('humidity',    '/humidity');
  </script>
</body></html>
"""


# ── 感測器讀取 ────────────────────────────────────────────────
def read_temperature():
    try:
        sensor.measure()
        return str(sensor.temperature())
    except OSError:
        return "--"


def read_humidity():
    try:
        sensor.measure()
        return str(sensor.humidity())
    except OSError:
        return "--"


# ── WiFi 連線 ─────────────────────────────────────────────────
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
    print()
    print("WiFi Connected:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]


# ── HTTP 伺服器 ───────────────────────────────────────────────
def serve(ip):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print("Server running at http://{}".format(ip))

    while True:
        conn, _ = s.accept()
        request = conn.recv(1024).decode()
        path = request.split(" ")[1] if " " in request else "/"

        if path == "/temperature":
            body = read_temperature()
            conn.send(("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" + body).encode())
        elif path == "/humidity":
            body = read_humidity()
            conn.send(("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" + body).encode())
        else:
            conn.send(("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + HTML).encode())
        conn.close()


# ── 主程式 ────────────────────────────────────────────────────
ip = connect_wifi()
serve(ip)
