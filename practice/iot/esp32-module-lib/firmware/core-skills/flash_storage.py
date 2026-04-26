"""
非揮發性儲存（Flash Memory）
Core Skills - flash_storage

原始課程: 2.ESP32數位IO與EEPROM
平台: ESP32 MicroPython

功能:
  範例 1: esp32.NVS（key-value 儲存，最接近 Arduino EEPROM）
  範例 2: JSON 文件儲存（靈活，適合結構化設定）

Arduino EEPROM → MicroPython 替代:
  Arduino: EEPROM.begin(size) / EEPROM.write(addr, val) / EEPROM.commit()
  MicroPython:
    方案 1 — esp32.NVS（key-value，型別安全）
    方案 2 — open() 寫 JSON（適合多筆設定）
    方案 3 — bytearray + open()（按 bytes 存取，最像 EEPROM）

Flash 寫入壽命：約 100,000〜1,000,000 次（與 Arduino EEPROM 相同量級）
建議：非必要不要每次 loop 都寫入，僅在資料改變時寫入

esp32.NVS 說明:
  namespace 類似 EEPROM 分區名稱
  支援型別：i32（整數）、blob（bytes）
  最大 key 長度 15 字元
"""

import time


# ── 範例 1：esp32.NVS ─────────────────────────────────────────
def nvs_demo():
    """
    使用 esp32.NVS 讀寫非揮發性資料
    資料斷電後保留
    """
    import esp32

    nvs = esp32.NVS("myapp")   # namespace（類似 EEPROM 分區）

    # ── 寫入 ──
    nvs.set_i32("counter", 0)
    nvs.set_i32("led_state", 1)
    # blob 用 bytes（最多 4000 bytes）
    nvs.set_blob("name", b"ESP32-Node")
    nvs.commit()   # 必須 commit 才真正寫入 Flash
    print("NVS write done")

    # ── 讀取 ──
    counter   = nvs.get_i32("counter")
    led_state = nvs.get_i32("led_state")
    buf       = bytearray(20)
    nvs.get_blob("name", buf)
    name = bytes(buf).rstrip(b'\x00').decode()

    print("counter={} led_state={} name={}".format(counter, led_state, name))

    # ── 遞增計數器（模擬開機次數）──
    counter += 1
    nvs.set_i32("counter", counter)
    nvs.commit()
    print("Incremented counter to", counter)


def nvs_settings_demo():
    """
    用 NVS 儲存 WiFi 設定（替代 hardcode）
    首次執行會初始化預設值
    """
    import esp32

    nvs = esp32.NVS("wifi_cfg")

    try:
        # 嘗試讀取已存設定
        buf = bytearray(32)
        nvs.get_blob("ssid", buf)
        ssid = bytes(buf).rstrip(b'\x00').decode()
        buf2 = bytearray(32)
        nvs.get_blob("pass", buf2)
        password = bytes(buf2).rstrip(b'\x00').decode()
        print("Loaded WiFi: ssid='{}' pass='{}'".format(ssid, password))
    except OSError:
        # 尚未設定，寫入預設值
        ssid     = "your_ssid"
        password = "your_password"
        nvs.set_blob("ssid", ssid.encode())
        nvs.set_blob("pass", password.encode())
        nvs.commit()
        print("Initialized WiFi settings in NVS")


# ── 範例 2：JSON 文件儲存 ─────────────────────────────────────
CONFIG_FILE = "/config.json"


def json_storage_demo():
    """
    用 JSON 文件儲存結構化設定
    適合多筆、多型別的設定資料
    """
    import json

    # ── 寫入設定 ──
    config = {
        "ssid":      "your_ssid",
        "password":  "your_password",
        "led_state": True,
        "counter":   0,
        "threshold": 2000,
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    print("Config written to", CONFIG_FILE)

    # ── 讀取設定 ──
    with open(CONFIG_FILE, "r") as f:
        loaded = json.load(f)
    print("Config loaded:", loaded)

    # ── 更新單一欄位 ──
    loaded["counter"] += 1
    with open(CONFIG_FILE, "w") as f:
        json.dump(loaded, f)
    print("Counter updated to", loaded["counter"])


def load_config(defaults: dict) -> dict:
    """
    讀取 JSON 設定檔，若不存在則用預設值建立
    使用方法：
        cfg = load_config({"ssid": "", "password": "", "threshold": 500})
        ssid = cfg["ssid"]
    """
    import json

    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        # 補上預設值中新增的 key
        updated = False
        for k, v in defaults.items():
            if k not in cfg:
                cfg[k] = v
                updated = True
        if updated:
            with open(CONFIG_FILE, "w") as f:
                json.dump(cfg, f)
        return cfg
    except OSError:
        with open(CONFIG_FILE, "w") as f:
            json.dump(defaults, f)
        return dict(defaults)


# ── 範例 3：按 bytes 存取（最像 Arduino EEPROM）─────────────
EEPROM_FILE = "/eeprom.bin"
EEPROM_SIZE = 512   # 模擬 512 bytes


def eeprom_write(addr: int, data: bytes):
    """寫入 bytes 到指定位址"""
    try:
        with open(EEPROM_FILE, "rb") as f:
            buf = bytearray(f.read())
        if len(buf) < EEPROM_SIZE:
            buf += bytearray(EEPROM_SIZE - len(buf))
    except OSError:
        buf = bytearray(EEPROM_SIZE)

    buf[addr:addr + len(data)] = data
    with open(EEPROM_FILE, "wb") as f:
        f.write(buf)


def eeprom_read(addr: int, length: int = 1) -> bytes:
    """從指定位址讀取 length bytes"""
    try:
        with open(EEPROM_FILE, "rb") as f:
            f.seek(addr)
            return f.read(length)
    except OSError:
        return bytes(length)


def eeprom_demo():
    """模擬 Arduino EEPROM 讀寫"""
    # 寫入 4 bytes
    eeprom_write(0, bytes([0, 1, 2, 3]))
    print("Before write:", list(eeprom_read(0, 4)))

    eeprom_write(0, bytes([10, 20, 30, 40]))
    print("After write:", list(eeprom_read(0, 4)))


# ── 主程式（選擇一種模式）────────────────────────────────────
# nvs_demo()
# nvs_settings_demo()
json_storage_demo()
# eeprom_demo()
