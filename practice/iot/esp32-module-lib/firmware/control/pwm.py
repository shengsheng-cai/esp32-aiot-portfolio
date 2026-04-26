"""
PWM 輸出控制
Control - pwm

原始課程: 9.ESP32_PWM
平台: ESP32 MicroPython

功能:
  以 PWM 控制 LED 亮度（呼吸燈效果）
  ESP32 幾乎每支 GPIO 都可輸出 PWM

注意事項:
  - GPIO 34、35、36、39 為輸入專用，無法輸出 PWM
  - GPIO 1、3、5、14、15 開機時狀態會改變，不建議用於 PWM

硬體接線:
  LED 正極 → GPIO 5（串接 220Ω 限流電阻）
  LED 負極 → GND
"""

import time
from machine import Pin, PWM

LED_PIN  = 5
FREQ     = 1000   # Hz
MAX_DUTY = 65535  # 16-bit resolution

led = PWM(Pin(LED_PIN), freq=FREQ)


# ── 呼吸燈 ────────────────────────────────────────────────────
def breathe(step=256, delay_ms=10):
    """LED 亮度漸增漸減"""
    while True:
        for duty in range(0, MAX_DUTY, step):
            led.duty_u16(duty)
            time.sleep_ms(delay_ms)
        for duty in range(MAX_DUTY, 0, -step):
            led.duty_u16(duty)
            time.sleep_ms(delay_ms)


# ── 主程式 ────────────────────────────────────────────────────
breathe()
