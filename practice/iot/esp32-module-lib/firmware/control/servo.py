"""
伺服馬達 Servo Motor 控制
Control - servo

原始課程: 16.ESP32_伺服馬達 / 20.伺服馬達 Servo Motor
平台: ESP32 MicroPython

功能:
  以 PWM 控制 SG90 伺服馬達角度（0~180 度）
  範例 1: 自動來回掃描 0→180→0
  範例 2: 旋鈕（ADC）控制角度

硬體規格 (Tower Pro SG90):
  工作電壓: 3.3V ~ 5V
  脈衝範圍: 500~2400 µs
  頻率: 50 Hz（週期 20ms）

  duty_u16 換算:
    0°   → 500µs  → 500/20000 * 65535 ≈ 1638
    90°  → 1450µs → 1450/20000 * 65535 ≈ 4751
    180° → 2400µs → 2400/20000 * 65535 ≈ 7864

硬體接線:
  SG90 訊號線 (橘) → GPIO 13
  SG90 VCC   (紅) → 3.3V（USB 供電時避免使用 5V，會嚴重抖動）
  SG90 GND   (棕) → GND

  旋鈕（選用）:
  VR 中間腳 → GPIO 34（ADC 輸入）
  VR 兩端   → 3.3V / GND
"""

import time
from machine import Pin, PWM, ADC

SERVO_PIN = 13
VR_PIN    = 34

PULSE_MIN = 1638   # 0°
PULSE_MAX = 7864   # 180°

servo = PWM(Pin(SERVO_PIN), freq=50)


def set_angle(angle: int):
    """設定伺服馬達角度 (0~180)"""
    angle = max(0, min(180, angle))
    duty = int(PULSE_MIN + (angle / 180) * (PULSE_MAX - PULSE_MIN))
    servo.duty_u16(duty)


# ── 範例 1：自動來回掃描 ──────────────────────────────────────
def sweep():
    while True:
        for angle in range(0, 181, 1):
            set_angle(angle)
            time.sleep_ms(15)
        for angle in range(180, -1, -1):
            set_angle(angle)
            time.sleep_ms(15)


# ── 範例 2：旋鈕控制角度 ─────────────────────────────────────
def vr_control():
    vr = ADC(Pin(VR_PIN))
    vr.atten(ADC.ATTN_11DB)   # 輸入範圍 0~3.3V
    while True:
        val   = vr.read()      # 0~4095
        angle = val * 180 // 4095
        set_angle(angle)
        time.sleep_ms(15)


# ── 主程式（選擇一種模式）────────────────────────────────────
sweep()
# vr_control()
