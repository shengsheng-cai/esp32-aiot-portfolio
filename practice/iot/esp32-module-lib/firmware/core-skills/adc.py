"""
ADC 類比輸入
Core-Skills - adc

原始課程: 4.ESP32類比輸入(ADC) / 17.類比輸入與輸出
平台: ESP32 MicroPython

功能:
  讀取 ADC 數值（旋鈕/光敏電阻/搖桿）
  ADC 值對應輸出（PWM 亮度控制）

ESP32 ADC 注意事項:
  - 12 bit，輸入範圍 0~3.3V，輸出 0~4095
  - WiFi 啟用時 ADC2 無法使用（GPIO 0,2,4,12~15,25~27）
  - ADC 非線性，接近 0V 和 3.3V 端點誤差較大
  - 雜訊較大時可在 ADC 輸入端接 0.1µF 電容到 GND

硬體接線:
  旋鈕中間腳 → GPIO 34（ADC1，不受 WiFi 影響）
  旋鈕兩端   → 3.3V / GND
  光敏電阻   → GPIO 35（與 10kΩ 電阻分壓後接入）
  搖桿 VRX   → GPIO 32
  搖桿 VRY   → GPIO 33
  搖桿 SW    → GPIO 25
  LED        → GPIO 5（PWM 輸出，串接 220Ω）
"""

import time
from machine import Pin, ADC, PWM

VR_PIN   = 34
LDR_PIN  = 35
JOY_X    = 32
JOY_Y    = 33
JOY_SW   = 25
LED_PIN  = 5


def make_adc(pin: int) -> ADC:
    adc = ADC(Pin(pin))
    adc.atten(ADC.ATTN_11DB)    # 輸入範圍 0~3.3V
    adc.width(ADC.WIDTH_12BIT)  # 12 bit，0~4095
    return adc


# ── 範例 1：旋鈕讀值 + 控制 LED 亮度 ─────────────────────────
def vr_led_demo():
    vr  = make_adc(VR_PIN)
    led = PWM(Pin(LED_PIN), freq=1000)

    while True:
        val   = vr.read()
        duty  = val * 65535 // 4095
        led.duty_u16(duty)
        print("VR: {:4d}  Duty: {:5d}".format(val, duty))
        time.sleep_ms(100)


# ── 範例 2：光敏電阻讀值 ──────────────────────────────────────
def ldr_demo():
    ldr = make_adc(LDR_PIN)

    while True:
        val = ldr.read()
        print("LDR: {:4d}".format(val))
        time.sleep_ms(500)


# ── 範例 3：雙軸搖桿 ─────────────────────────────────────────
def joystick_demo():
    joy_x  = make_adc(JOY_X)
    joy_y  = make_adc(JOY_Y)
    joy_sw = Pin(JOY_SW, Pin.IN, Pin.PULL_UP)

    while True:
        x  = joy_x.read()
        y  = joy_y.read()
        sw = joy_sw.value()
        print("X: {:4d}  Y: {:4d}  SW: {}".format(x, y, "pressed" if sw == 0 else "released"))
        time.sleep_ms(200)


# ── 主程式（選擇一種模式）────────────────────────────────────
vr_led_demo()
# ldr_demo()
# joystick_demo()
