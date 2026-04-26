"""
OTA 無線更新韌體
Networking - ota

原始課程: 31.Arduino IDE以無線方式燒錄程式碼(OTA)
平台: ESP32 MicroPython

功能:
  方式 1: WebREPL — 等同 Arduino OTA，讓 MicroPython WebREPL 工具透過 WiFi 上傳 .py 檔案
  方式 2: HTTP 檔案上傳 Server — 透過瀏覽器上傳新的 main.py 並重啟

MicroPython OTA 說明:
  MicroPython 沒有 ArduinoOTA，但有等效機制：
  1. WebREPL：啟動後可用 webrepl_cli.py 無線上傳/執行檔案
     工具: webrepl_cli.py <file> <ip>:/<dest>
  2. HTTP upload：自建 multipart upload server，接收 .py 後寫入並重啟

注意事項:
  - WebREPL 啟用後所有網路用戶都可嘗試連線，生產環境請設定強密碼
  - HTTP 上傳 server 沒有 TLS，僅適用受信任的內網
  - 上傳 main.py 後執行 machine.reset() 即完成更新
"""

import time
import network
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


# ── 方式 1：WebREPL ───────────────────────────────────────────
def start_webrepl(password: str = "micropython"):
    """
    啟動 WebREPL，允許透過 WiFi 上傳檔案
    上傳工具: webrepl_cli.py（需另外下載）
    瀏覽器版: http://micropython.org/webrepl/

    用法:
      python webrepl_cli.py main.py 192.168.x.x:/main.py
    """
    import webrepl

    ip  = connect_wifi()
    led = Pin(LED_PIN, Pin.OUT)
    led.value(1)

    webrepl.start(password=password)
    print("WebREPL started at ws://{}:8266/".format(ip))
    print("Password:", password)
    print("LED on to indicate server running.")

    while True:
        time.sleep(1)


# ── 方式 2：HTTP 檔案上傳 Server ─────────────────────────────
def start_http_upload_server():
    """
    HTTP multipart 上傳 server
    瀏覽器開啟 http://<ip>/ → 選擇 main.py → 上傳後自動重啟

    注意：僅支援上傳 main.py；上傳後 ESP32 會立即 reset
    """
    import socket
    import machine

    ip = connect_wifi()

    UPLOAD_PAGE = b"""<!DOCTYPE html><html><head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<style>body{font-family:Helvetica;text-align:center;margin-top:60px}
input,button{padding:12px 24px;font-size:16px;margin:8px}
button{background:#2980b9;color:white;border:none;border-radius:4px;cursor:pointer}</style>
</head><body>
<h1>ESP32 Firmware Upload</h1>
<form method='POST' enctype='multipart/form-data' action='/upload'>
<input type='file' name='firmware' accept='.py'><br>
<button type='submit'>Upload &amp; Reboot</button>
</form></body></html>"""

    s = socket.socket()
    s.bind(("", 80))
    s.listen(3)
    print("HTTP upload server at http://{}:80/".format(ip))

    while True:
        conn, _ = s.accept()
        raw = conn.recv(4096)

        if b"POST /upload" in raw:
            # 找到 multipart body（跳過兩個 \r\n\r\n 邊界）
            parts = raw.split(b"\r\n\r\n", 2)
            if len(parts) >= 3:
                content = parts[2]
                # 去掉 multipart 結尾邊界
                if b"\r\n--" in content:
                    content = content.rsplit(b"\r\n--", 1)[0]
                try:
                    with open("main.py", "wb") as f:
                        f.write(content)
                    print("main.py uploaded ({} bytes). Rebooting...".format(len(content)))
                    conn.send(b"HTTP/1.1 200 OK\r\n\r\n<html><body>Upload OK! Rebooting...</body></html>")
                    conn.close()
                    time.sleep_ms(500)
                    machine.reset()
                except OSError as e:
                    print("Write failed:", e)
                    conn.send(b"HTTP/1.1 500 Internal Server Error\r\n\r\n<html><body>Upload failed!</body></html>")
                    conn.close()
        else:
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.send(UPLOAD_PAGE)

        conn.close()


# ── 主程式（選擇一種模式）────────────────────────────────────
start_webrepl(password="micropython")
# start_http_upload_server()
