"""
ESP-NOW 點對點無線通訊
Networking - esp_now

原始課程: 36.ESP32 NOW
平台: ESP32 MicroPython

功能:
  範例 1: ESP-NOW 傳送端（發送結構化資料）
  範例 2: ESP-NOW 接收端（接收並解析）
  範例 3: 雙向通訊（同一支程式可收可發）

ESP-NOW 說明:
  不需 WiFi 路由器，ESP32 之間直接點對點通訊
  最大 250 bytes / 封包；最多配對 20 個裝置
  須先取得對方 MAC Address（見 get_mac_address()）
  發送端與接收端皆需設定 WIFI_STA 模式

依賴模組:
  `espnow` — MicroPython v1.19+ 已內建（需 ESP32 固件 ≥ 1.19）

結構化資料打包:
  MicroPython 用 struct.pack/unpack 替代 C struct
  例：struct.pack("32s?", b"hello", True) — 32字節字串 + bool

硬體接線:
  無（ESP32 內建 2.4GHz 天線）
"""

import struct
import time
import network
import espnow

# ── 取得本機 MAC Address（兩台都要先執行，互換後填入對方的 MAC）
def get_mac_address():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    mac = sta.config("mac")
    print("MAC:", ":".join("{:02X}".format(b) for b in mac))
    return mac


def _init_espnow() -> espnow.ESPNow:
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    e = espnow.ESPNow()
    e.active(True)
    return e


# ── 封包格式：msg(32 bytes) + led_state(bool) ─────────────────
MSG_FMT  = "32s?"
MSG_SIZE = struct.calcsize(MSG_FMT)


def pack_msg(msg: str, led_state: bool) -> bytes:
    return struct.pack(MSG_FMT, msg.encode()[:32].ljust(32, b'\x00'), led_state)


def unpack_msg(data: bytes) -> tuple:
    raw_msg, led_state = struct.unpack(MSG_FMT, data)
    return raw_msg.rstrip(b'\x00').decode("utf-8", "ignore"), led_state


# ── 範例 1：傳送端 ────────────────────────────────────────────
def sender_demo():
    """
    每 2 秒傳送一次資料給接收端
    PEER_MAC 填入接收端的 MAC（由 get_mac_address() 取得）
    """
    PEER_MAC = b'\xFF\xFF\xFF\xFF\xFF\xFF'  # 廣播（改為對方 MAC 更可靠）

    e = _init_espnow()
    e.add_peer(PEER_MAC)

    led_state = False
    count = 0

    print("ESP-NOW Sender ready")
    while True:
        msg = "count: {}".format(count)
        data = pack_msg(msg, led_state)
        success = e.send(PEER_MAC, data)
        print("Sent: '{}' led={} {}".format(msg, led_state, "OK" if success else "FAIL"))
        led_state = not led_state
        count += 1
        time.sleep_ms(2000)


# ── 範例 2：接收端 ────────────────────────────────────────────
def receiver_demo():
    """
    等待接收 ESP-NOW 封包，解析後印出並控制 LED
    """
    from machine import Pin
    led = Pin(2, Pin.OUT)

    e = _init_espnow()
    print("ESP-NOW Receiver ready. Waiting...")

    while True:
        host, data = e.recv()
        if data:
            msg, led_state = unpack_msg(data)
            mac = ":".join("{:02X}".format(b) for b in host)
            print("From: {}  msg='{}' led={}".format(mac, msg, led_state))
            led.value(led_state)


# ── 主程式（選擇一種模式）────────────────────────────────────
# get_mac_address()   # 先執行，取得 MAC
# sender_demo()
receiver_demo()
