"""
步進馬達 Stepper Motor 控制 (ULN2003 + 28BYJ-48)
Control - stepper

原始課程: 19.ESP32_步進馬達 / 27.步進馬達
平台: ESP32 MicroPython

硬體規格 (28BYJ-48):
  額定電壓: 5V DC
  每轉步數: 2048 步（含減速比 1:64）
  步距角: 0.18°/步
  延時要求: 每步最少 2~3ms

硬體接線:
  ULN2003 IN1 → GPIO 19
  ULN2003 IN2 → GPIO 18
  ULN2003 IN3 → GPIO 5
  ULN2003 IN4 → GPIO 17
  ULN2003 VCC → 5V
  ULN2003 GND → GND

注意事項:
  - ULN2003 輸入輸出為反相（輸入 HIGH → 輸出 LOW）
  - 馬達轉動一步需要 2~3ms，delay 不足會無法動作
  - 使用完畢應將所有線圈腳位設 LOW，避免過熱
"""

import time
from machine import Pin

IN1 = Pin(19, Pin.OUT)
IN2 = Pin(18, Pin.OUT)
IN3 = Pin(5,  Pin.OUT)
IN4 = Pin(17, Pin.OUT)

COILS = [IN1, IN2, IN3, IN4]

# 4 相步進序列（全步）
STEP_SEQ = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
]

STEPS_PER_REV = 2048   # 轉一圈所需步數
STEP_DELAY_MS = 3      # 每步延時（ms），最低約 2~3ms


def step_once(seq_index: int):
    for i, coil in enumerate(COILS):
        coil.value(STEP_SEQ[seq_index % 4][i])


def release():
    """關閉所有線圈，避免持續通電過熱"""
    for coil in COILS:
        coil.value(0)


def move(steps: int, delay_ms: int = STEP_DELAY_MS):
    """
    轉動指定步數
    steps > 0：順時針
    steps < 0：逆時針
    """
    direction = 1 if steps >= 0 else -1
    for i in range(abs(steps)):
        step_once(i * direction)
        time.sleep_ms(delay_ms)
    release()


def rotate(revolutions: float, delay_ms: int = STEP_DELAY_MS):
    """轉動指定圈數（支援小數，例如 0.5 = 半圈）"""
    steps = int(STEPS_PER_REV * revolutions)
    move(steps, delay_ms)


# ── 主程式 ───────────────────────────────────────────────────
print("Stepper: rotate 1 revolution clockwise")
rotate(1)
time.sleep_ms(1000)

print("Stepper: rotate 1 revolution counter-clockwise")
rotate(-1)
time.sleep_ms(1000)
