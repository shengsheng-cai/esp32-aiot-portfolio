"""
ADXL335 三軸加速度感測器 (GY-61)
Sensors - adxl335

原始課程: 39.三軸加速感測器 ADXL335(GY-61)
平台: ESP32 MicroPython

功能:
  範例 1: 讀取 XYZ 原始 ADC 值 + 換算 g 值
  範例 2: 計算傾斜角（roll / pitch）

ADXL335 規格:
  工作電壓 1.8〜3.6V（板載 3.3V 穩壓，可接 5V 系統）
  輸出類比電壓：0g 時 = VCC/2（約 1.65V）；±3g → 0〜3.3V
  工作電流約 350μA
  GPIO 36, 39, 34 為 ESP32 input-only 腳位，適合接類比輸出

類比輸出特性:
  0g → ADC ≈ 2047（12-bit 中值）
  +3g → ADC ≈ 4095
  -3g → ADC ≈ 0
  校正 RawMin / RawMax 可提高精度（靜置量測各軸極值）

硬體接線:
  ADXL335 VCC  → 3.3V
  ADXL335 GND  → GND
  ADXL335 X    → GPIO 36
  ADXL335 Y    → GPIO 39
  ADXL335 Z    → GPIO 34
"""

import math
import time
from machine import Pin, ADC

X_PIN = 36
Y_PIN = 39
Z_PIN = 34

# 12-bit ADC 校正值（靜置旋轉各軸量測，或直接用預設值）
RAW_MIN = 0
RAW_MAX = 4095
SAMPLE_SIZE = 10   # 取樣平均次數


def _make_adc(pin: int) -> ADC:
    a = ADC(Pin(pin))
    a.atten(ADC.ATTN_11DB)   # 0〜3.3V
    return a


def _read_axis(adc: ADC, n: int = SAMPLE_SIZE) -> int:
    """取 n 次平均值"""
    return sum(adc.read() for _ in range(n)) // n


def _to_g(raw: int) -> float:
    """將 ADC 原始值映射到 ±3g（放大 1000 倍後除回）"""
    scaled = (raw - RAW_MIN) * 6000 // (RAW_MAX - RAW_MIN) - 3000
    return scaled / 1000.0


# ── 範例 1：讀取 XYZ 加速度 ──────────────────────────────────
def accel_demo():
    """每 200ms 讀取一次，印出原始值與 g 值"""
    adc_x = _make_adc(X_PIN)
    adc_y = _make_adc(Y_PIN)
    adc_z = _make_adc(Z_PIN)

    print("ADXL335 — X=GPIO{} Y=GPIO{} Z=GPIO{}".format(X_PIN, Y_PIN, Z_PIN))
    while True:
        rx, ry, rz = _read_axis(adc_x), _read_axis(adc_y), _read_axis(adc_z)
        gx, gy, gz = _to_g(rx), _to_g(ry), _to_g(rz)
        print("X={:4d}/{:+.2f}G  Y={:4d}/{:+.2f}G  Z={:4d}/{:+.2f}G".format(
            rx, gx, ry, gy, rz, gz))
        time.sleep_ms(200)


# ── 範例 2：計算傾斜角 ────────────────────────────────────────
def tilt_demo():
    """
    計算 roll（繞 X 軸）與 pitch（繞 Y 軸）
    注意：加速度計無法測量 yaw（偏航），需搭配陀螺儀
    """
    adc_x = _make_adc(X_PIN)
    adc_y = _make_adc(Y_PIN)
    adc_z = _make_adc(Z_PIN)

    print("Tilt demo — roll/pitch in degrees")
    while True:
        gx = _to_g(_read_axis(adc_x))
        gy = _to_g(_read_axis(adc_y))
        gz = _to_g(_read_axis(adc_z))

        roll  = math.atan2(gy, gz) * 180 / math.pi + 180
        pitch = math.atan2(gx, gz) * 180 / math.pi + 180
        print("Roll={:.1f}°  Pitch={:.1f}°  (X={:.2f}G Y={:.2f}G Z={:.2f}G)".format(
            roll, pitch, gx, gy, gz))
        time.sleep_ms(200)


# ── 主程式（選擇一種模式）────────────────────────────────────
accel_demo()
# tilt_demo()
