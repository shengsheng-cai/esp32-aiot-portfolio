"""
WiFi 連接、掃描與 NTP 時間同步
Networking - wifi

原始課程: 25.基本概念與WIFI掃瞄 / 26.連接WIFI與網路時間NPT /
          ESP32 靜態IP設定
平台: ESP32 MicroPython

功能:
  範例 1: 掃描附近 AP（SSID / RSSI / 安全類型）
  範例 2: STA 模式連接 WiFi（DHCP / 靜態 IP）
  範例 3: NTP 同步時間（UTC+8）
  範例 4: SoftAP 模式（讓其他裝置連入 ESP32）

WiFi 模式說明:
  STA (Station) — 連接到外部 AP；預設模式
  AP (SoftAP)   — ESP32 自身作為 AP；預設 IP 192.168.4.1
  STA+AP        — 同時使用兩種模式（建立 Mesh 用）

NTP 說明:
  `ntptime.settime()` 同步 UTC 時間到內部 RTC
  台灣時區 UTC+8：取得 time.time() 後加 8*3600 再 localtime()
  取得 NTP 後可斷開 WiFi 節省電力

靜態 IP:
  wlan.ifconfig(('IP', '子網路遮罩', '閘道', 'DNS'))
  需在 wlan.connect() 前呼叫
"""

import time
import network

WIFI_SSID = "your_ssid"
WIFI_PASS = "your_password"
UTC_OFFSET = 8 * 3600  # UTC+8 台灣

AUTH_NAMES = {0: "OPEN", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2"}


# ── 範例 1：掃描附近 AP ───────────────────────────────────────
def scan_wifi():
    """印出附近所有 WiFi AP 的 SSID、RSSI、安全類型"""
    sta = network.WLAN(network.STA_IF)
    sta.active(True)

    print("Scanning Wi-Fi networks...")
    nets = sta.scan()  # (ssid, bssid, channel, RSSI, authmode, hidden)

    print("{} network(s) found:".format(len(nets)))
    for i, n in enumerate(nets):
        ssid     = n[0].decode("utf-8", "ignore")
        rssi     = n[3]
        authmode = AUTH_NAMES.get(n[4], "UNKNOWN")
        print("  {:2d}: {:32s} {:4d} dBm  {}".format(i + 1, ssid, rssi, authmode))


# ── 範例 2：STA 連接 WiFi ────────────────────────────────────
def connect_wifi(ssid: str = WIFI_SSID, password: str = WIFI_PASS,
                 static_ip: tuple | None = None, timeout: int = 20) -> bool:
    """
    連接到 WiFi AP
    static_ip: (ip, netmask, gateway, dns) 或 None（DHCP）
    回傳 True = 連接成功
    """
    sta = network.WLAN(network.STA_IF)
    sta.active(True)

    if sta.isconnected():
        print("Already connected:", sta.ifconfig())
        return True

    if static_ip:
        sta.ifconfig(static_ip)

    print("Connecting to", ssid, end="")
    sta.connect(ssid, password)

    for _ in range(timeout):
        if sta.isconnected():
            print("\nConnected! IP:", sta.ifconfig()[0])
            return True
        print(".", end="")
        time.sleep(1)

    print("\nConnection failed.")
    return False


# ── 範例 3：NTP 時間同步 ─────────────────────────────────────
def sync_ntp(ssid: str = WIFI_SSID, password: str = WIFI_PASS):
    """
    連接 WiFi → 同步 NTP → 斷開 WiFi → 印出本地時間
    """
    import ntptime

    if not connect_wifi(ssid, password):
        return

    try:
        ntptime.host = "pool.ntp.org"
        ntptime.settime()
        print("NTP sync OK")
    except Exception as e:
        print("NTP sync failed:", e)

    # 斷開 WiFi 節省電力
    network.WLAN(network.STA_IF).disconnect()

    _print_local_time()


def _print_local_time():
    t = time.localtime(time.time() + UTC_OFFSET)
    weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    print("{:04d}-{:02d}-{:02d} {} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], weekdays[t[6]], t[3], t[4], t[5]
    ))


# ── 範例 4：SoftAP 模式 ──────────────────────────────────────
def start_soft_ap(ssid: str = "ESP32-AP", password: str = "12345678",
                  max_clients: int = 3):
    """
    啟動 SoftAP，其他裝置可連入 ESP32
    IP: 192.168.4.1（預設）
    """
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password, max_clients=max_clients)

    print("SoftAP started:", ap.ifconfig()[0])
    print("SSID:", ssid)

    while True:
        time.sleep_ms(100)


# ── 主程式（選擇一種模式）────────────────────────────────────
# scan_wifi()

# DHCP 連接
# connect_wifi()

# 靜態 IP 連接
# connect_wifi(static_ip=("192.168.1.100", "255.255.255.0", "192.168.1.1", "8.8.8.8"))

sync_ntp()
# start_soft_ap()
