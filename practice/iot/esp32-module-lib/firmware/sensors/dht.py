"""
DHT11 / DHT22 溫濕度感測模組
Sensors - dht

原始課程: 15.ESP32_DHT11溫濕度感測模組 / 25.DHT11溫濕度感測模組
平台: ESP32 MicroPython

功能:
  範例 1: 持續讀取溫濕度（每 2 秒）
  範例 2: 記錄資料至 CSV 檔

DHT11 規格:
  供電電壓 3.3〜5.5V，數位單線協議
  溫度 0〜50°C，精度 ±2°C
  濕度 20〜80%RH，精度 ±5%

DHT22 (AM2302) 規格:
  溫度 -40〜80°C，精度 ±0.5°C
  濕度 0〜100%RH，精度 ±2%

Arduino DHT library (Adafruit) → MicroPython 內建 dht 模組
  dht.DHT11(pin)  對應 DHT11
  dht.DHT22(pin)  對應 DHT22 / AM2302

硬體接線:
  DHT11/22 DATA → D27
  DHT11/22 VCC  → 3.3V（含背板模組）或 3.3V〜5V（裸 IC 需加 10kΩ 上拉）
  DHT11/22 GND  → GND
"""

import dht
import time
from machine import Pin

DHT_PIN  = 27
DHT_TYPE = "DHT11"   # 改成 "DHT22" 即可切換型號


def _make_sensor(pin=DHT_PIN, sensor_type=DHT_TYPE):
    p = Pin(pin)
    return dht.DHT11(p) if sensor_type == "DHT11" else dht.DHT22(p)


# ── 範例 1：持續讀取溫濕度 ────────────────────────────────────
def read_demo():
    """每 2 秒讀取一次，印出溫度與濕度"""
    sensor = _make_sensor()
    print("DHT{} on GPIO {} — reading every 2s".format(
        "11" if DHT_TYPE == "DHT11" else "22", DHT_PIN))

    while True:
        try:
            sensor.measure()
            t = sensor.temperature()
            h = sensor.humidity()
            print("Temp: {:.1f}°C  Humidity: {:.1f}%".format(t, h))
        except OSError:
            print("Read failed — check wiring")
        time.sleep(2)


# ── 範例 2：記錄資料至 CSV ────────────────────────────────────
def log_demo(count: int = 10, filename: str = "temp_log.csv"):
    """
    讀取 count 筆資料存入 CSV
    欄位：time, temp_C, humidity_%
    """
    sensor = _make_sensor()

    with open(filename, "w") as f:
        f.write("time,temp_C,humidity\n")
        saved = 0
        print("Logging {} readings to {}...".format(count, filename))

        while saved < count:
            try:
                sensor.measure()
                t  = sensor.temperature()
                h  = sensor.humidity()
                ts = time.localtime()
                row = "{:02d}:{:02d}:{:02d},{:.1f},{:.1f}".format(
                    ts[3], ts[4], ts[5], t, h)
                print(row)
                f.write(row + "\n")
                saved += 1
            except OSError:
                print("Read error — retrying")
            time.sleep(2)

    print("Done. Saved to", filename)


# ── 主程式（選擇一種模式）────────────────────────────────────
read_demo()
# log_demo(count=20)
