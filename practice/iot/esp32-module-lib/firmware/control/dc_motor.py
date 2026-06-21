"""
直流馬達控制 (L298N / L9110)
Control - dc_motor

功能:
  PWM 控制直流馬達轉速與方向
  旋鈕（ADC）控制：中間值停止，往上正轉，往下反轉

硬體規格:
  L298N: 5V~35V，2A peak，含 7805 穩壓
  L9110: 2.5V~12V，800mA 持續，控制邏輯與馬達共用 VCC

L298N 接線:
  IN3 → D16
  IN4 → D17
  ENA → D4（PWM 速度控制）
  VCC → 5V（馬達電源）
  GND → GND

  注意: 使用 PWM 控速時，建議拔除 J8 跳線，將麵包板 5V 分別接 Vin 和 5Vout，
        避免 PWM 控速失效問題

L9110 接線:
  A-IA → D16
  A-IB → D17
  VCC  → 5V（控制邏輯與馬達共用，建議使用 5V 馬達）
  GND  → GND

旋鈕接線:
  VR 中間腳 → D36（注意使用 3.3V）
  VR 兩端   → 3.3V / GND
"""

import time
from machine import Pin, PWM, ADC

IN3_PIN = 16
IN4_PIN = 17
PWM_PIN = 4
VR_PIN = 36

in3 = Pin(IN3_PIN, Pin.OUT)
in4 = Pin(IN4_PIN, Pin.OUT)
pwm = PWM(Pin(PWM_PIN), freq=1000)

in3.value(0)
in4.value(0)
pwm.duty_u16(0)


def forward(speed: int):
    """正轉，speed: 0~65535"""
    in3.value(1)
    in4.value(0)
    pwm.duty_u16(speed)


def backward(speed: int):
    """反轉，speed: 0~65535"""
    in3.value(0)
    in4.value(1)
    pwm.duty_u16(speed)


def stop():
    in3.value(0)
    in4.value(0)
    pwm.duty_u16(0)


# ── 旋鈕控制模式 ──────────────────────────────────────────────
def vr_control():
    vr = ADC(Pin(VR_PIN))
    vr.atten(ADC.ATTN_11DB)

    DEAD_LOW = 1780  # 中間死區下限（停止）
    DEAD_HIGH = 1880  # 中間死區上限（停止）

    while True:
        val = vr.read()  # 0~4095

        if val > DEAD_HIGH:
            speed = (val - DEAD_HIGH) * 65535 // (4095 - DEAD_HIGH)
            forward(speed)
        elif val < DEAD_LOW:
            speed = (DEAD_LOW - val) * 65535 // DEAD_LOW
            backward(speed)
        else:
            stop()

        time.sleep_ms(20)


# ── 主程式（簡易測試）────────────────────────────────────────
print("Forward 3s")
forward(40000)
time.sleep_ms(3000)

print("Backward 3s")
backward(40000)
time.sleep_ms(3000)

stop()
print("Stop")

# 旋鈕控制模式（取消註解啟用）
# vr_control()
