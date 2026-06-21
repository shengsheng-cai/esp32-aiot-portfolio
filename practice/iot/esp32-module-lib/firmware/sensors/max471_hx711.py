"""
MAX471 電壓電流檢測 + HX711 秤重感測
Sensors - max471_hx711

原始課程:
  47.ESP32 MAX471 電壓電流檢測模組
  48.ESP32 HX711 秤重感測模組

平台: ESP32 MicroPython

MAX471 說明:
  精密高端電流感測 IC，無需外部電源（由被測電源供電）
  VT（電壓）：輸入電壓的 1/5，測量範圍 3〜25V（3.3V 系統最大 16.5V）
  AT（電流）：1V/A 轉換比，測量範圍 0〜3A，精度 2%

HX711 說明:
  24-bit 高精度 ADC，專為電子秤設計（惠斯登電橋）
  非標準協議（2 pin：DOUT + SCK），需 bit-bang 驅動
  使用前需校正（tare 歸零 + 已知砝碼取得 calibration factor）

Arduino HX711 library → MicroPython hx711 驅動
  安裝：mpremote mip install github:robert-hh/hx711/hx711.py
  或手動下載 https://github.com/robert-hh/hx711

硬體接線（MAX471）:
  MAX471 VT  → D32（ADC1_CH4）
  MAX471 AT  → D33（ADC1_CH5）
  MAX471 GND → ESP32 GND
  MAX471 VIN/VOUT 串入被測電路（VOUT 接負載，VIN 接電源正）

硬體接線（HX711）:
  HX711 DOUT → D16
  HX711 SCK  → D4
  HX711 VCC  → 3.3V（或 5V）
  HX711 GND  → GND
  校正按鈕   → D23（PULL_UP）
"""

import time
from machine import Pin, ADC

# MAX471 腳位
VT_PIN = 32
AT_PIN = 33
REF_V  = 3.3   # ESP32 ADC 參考電壓

# HX711 腳位
HX_DOUT = 16
HX_SCK  = 4
CAL_BTN = 23   # 校正按鈕（INPUT_PULLUP）


# ─────────────────────────────────────────────────────────────
# MAX471 電壓電流檢測
# ─────────────────────────────────────────────────────────────
def _read_mv(pin: int) -> float:
    """讀取 GPIO 電壓（mV），ESP32 12-bit ADC"""
    adc = ADC(Pin(pin))
    adc.atten(ADC.ATTN_11DB)
    return adc.read() * (REF_V / 4095) * 1000


def max471_demo():
    """每 500ms 讀取電壓與電流，印出結果"""
    print("MAX471 — VT=GPIO{} AT=GPIO{}".format(VT_PIN, AT_PIN))
    print("Note: VT measures 1/5 of input voltage; AT measures 1V/A")
    while True:
        vt_mv  = _read_mv(VT_PIN)
        at_mv  = _read_mv(AT_PIN)
        voltage = vt_mv / 1000 * 5   # VT = Vin/5
        current = at_mv / 1000       # 1V/A
        print("Voltage: {:.2f} V  Current: {:.3f} A  Power: {:.2f} W".format(
            voltage, current, voltage * current))
        time.sleep_ms(500)


# ─────────────────────────────────────────────────────────────
# HX711 秤重感測
# ─────────────────────────────────────────────────────────────
def hx711_demo():
    """
    HX711 秤重感測器
    - 按下校正按鈕（GPIO 23）進入校正模式
    - 校正流程：空秤歸零 → 放 5g 砝碼 → 計算 factor
    - 校正值可寫入 Flash 保留（本範例僅記憶體保存）

    需先安裝 hx711 驅動：
      mpremote mip install github:robert-hh/hx711/hx711.py
    """
    try:
        from hx711 import HX711
    except ImportError:
        print("hx711 driver not found.")
        print("Install: mpremote mip install github:robert-hh/hx711/hx711.py")
        return

    scale = HX711(d_out=HX_DOUT, pd_sck=HX_SCK)
    btn   = Pin(CAL_BTN, Pin.IN, Pin.PULL_UP)

    calibration = [False]
    factor      = [1.0]

    def on_btn(pin):
        calibration[0] = True

    btn.irq(trigger=Pin.IRQ_FALLING, handler=on_btn)
    print("HX711 ready. Press button (GPIO{}) to calibrate.".format(CAL_BTN))

    scale_time = time.ticks_ms()

    while True:
        if calibration[0]:
            calibration[0] = False
            print("=== Calibration Mode ===")
            scale.set_scale()
            print("Remove all weights. Taring in 5s...")
            time.sleep(5)
            scale.tare()
            print("Tare done. Place 5g weight, reading in 5s...")
            time.sleep(5)
            reading = scale.get_units(20)
            factor[0] = reading / 5.0   # 5g 砝碼
            scale.set_scale(factor[0])
            print("Calibration done. Factor={:.2f}".format(factor[0]))

        if time.ticks_diff(time.ticks_ms(), scale_time) >= 1000:
            try:
                val = scale.get_units(5)
                print("Weight: {:.1f} g".format(val))
            except Exception as e:
                print("Scale error:", e)
            scale_time = time.ticks_ms()


# ── 主程式（選擇一種模式）────────────────────────────────────
max471_demo()
# hx711_demo()
