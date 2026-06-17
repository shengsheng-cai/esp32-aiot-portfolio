"""
Motor Console v0.5 — Relay + Servo + LED + Stepper
平台: ESP32 MicroPython

=== 接線 ===
  繼電器:  S→D26, VCC→5V, GND→GND
  SG90:    訊號(橘)→D13, VCC(紅)→3.3V（避免 5V，會嚴重抖動）, GND(棕)→GND
  L298N（步進馬達）: IN1→D27, IN2→D25, IN3→D33, IN4→D32
           ENA、ENB 洞接 5V（兩通道常開），VCC→5V, GND→GND
  28BYJ-48：接L298N＿OUT1→橘, OUT2→黃, OUT3→粉, OUT4→藍, 5V端子→馬達紅線
  LED:     正極（長腳）→ 220Ω → D5, 負極（短腳）→ GND

=== 規格 ===
  SG90 (Tower Pro):
    工作電壓: 3.3V ~ 5V / 脈衝範圍: 500~2400µs / 頻率: 50Hz（週期 20ms）
    duty_u16 換算:
      0°   → 500µs  → 500/20000 * 65535 ≈ 1638
      90°  → 1450µs → 1450/20000 * 65535 ≈ 4751
      180° → 2400µs → 2400/20000 * 65535 ≈ 7864
  LED: PWM freq=1000Hz 控制亮度，duty_u16 最大值 65535
  L298N: 5V~35V，2A peak per channel，含 7805 穩壓；此處用全通道驅動步進馬達
  28BYJ-48: 額定 5V，每轉 4096 步（半步序列，含減速比 1:64），步距角 0.09°/步
             每步最少 2~3ms；使用完畢應將所有線圈設 LOW 避免過熱

=== 操作 ===
  relay 1           繼電器吸合，啟用馬達輸出
  relay 0           繼電器斷開，停止馬達
  mode servo        切換到伺服馬達模式
  mode step         切換到步進馬達模式
  angle <0-180>     伺服轉到指定角度（servo 模式）
  sweep             伺服來回掃描 0~180°（servo 模式）
  turn <圈數>       步進馬達轉指定圈數，負數反轉（step 模式）
  steps <步數>      步進馬達轉指定步數，負數反轉（step 模式）
  led on            LED 常亮
  led off           LED 熄滅
  led breathe       LED 呼吸燈（非阻塞，在主迴圈更新）

=== 硬體清單 ===
  ESP32 x1、單路繼電器模組 x1、SG90 x1
  28BYJ-48 步進馬達 + L298N x1
  LED x1、220Ω 電阻 x1、杜邦線若干

=== 注意 ===
  - 繼電器需使用「光耦輸入高電位觸發」模組；低電位觸發型無法直接接 ESP32
  - 建議繼電器電源與 ESP32 電源完全隔離，避免 EMI 造成 MCU 重啟
  - 步進馬達使用完畢應將所有線圈設 LOW，持續通電會過熱
  - L298N ENA/ENB 洞接 5V 讓兩通道常開，不需 PWM 控速
  - GPIO 34、35、36、39 為輸入專用，無法輸出 PWM
"""

import sys
import time
import select
from machine import Pin, PWM

# 繼電器
RELAY_PIN = 26
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0)
relay_enabled = False

# 伺服馬達
SERVO_PIN = 13
PULSE_MIN = 1638
PULSE_MAX = 7864
servo = PWM(Pin(SERVO_PIN), freq=50)
servo.duty_u16(0)

# LED
LED_PIN = 5
LED_FREQ = 1000
LED_STEP = 512
led_pwm = PWM(Pin(LED_PIN), freq=LED_FREQ)
led_pwm.duty_u16(0)
led_mode = "off"
led_duty = 0
led_dir = 1

# 步進馬達（28BYJ-48 + L298N）
STEP_IN1_PIN = 27
STEP_IN2_PIN = 25
STEP_IN3_PIN = 33
STEP_IN4_PIN = 32
STEP_SEQ = [
    [1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0],
    [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1], [1, 0, 0, 1],
]
STEPS_PER_REV = 4096
STEP_DELAY_MS = 3
step_coils = [
    Pin(STEP_IN1_PIN, Pin.OUT),
    Pin(STEP_IN2_PIN, Pin.OUT),
    Pin(STEP_IN3_PIN, Pin.OUT),
    Pin(STEP_IN4_PIN, Pin.OUT),
]
for c in step_coils:
    c.value(0)

current_mode = "servo"


# ── 繼電器 ───────────────────────────────────────────────────


def relay_set(state):
    """流程層: 設定繼電器狀態，relay 0 時同步停止伺服馬達。"""
    global relay_enabled
    relay.value(state)
    relay_enabled = bool(state)
    if not relay_enabled:
        servo.duty_u16(0)
    print("[relay] {}".format("ON" if state else "OFF"))


# ── 伺服馬達 ─────────────────────────────────────────────────


def set_angle(angle):
    """行為層: 換算角度為 duty_u16 並輸出 PWM。"""
    angle = max(0, min(180, angle))
    duty = int(PULSE_MIN + (angle / 180) * (PULSE_MAX - PULSE_MIN))
    servo.duty_u16(duty)
    print("[servo] angle={}".format(angle))


def sweep():
    """流程層: 伺服來回掃描 0~180°。"""
    print("[servo] sweep start")
    for angle in range(0, 181, 2):
        servo.duty_u16(int(PULSE_MIN + (angle / 180) * (PULSE_MAX - PULSE_MIN)))
        time.sleep_ms(15)
    for angle in range(180, -1, -2):
        servo.duty_u16(int(PULSE_MIN + (angle / 180) * (PULSE_MAX - PULSE_MIN)))
        time.sleep_ms(15)
    print("[servo] sweep done")


# ── LED ──────────────────────────────────────────────────────


def led_set(mode):
    """流程層: 設定 LED 模式（on/off/breathe），breathe 在主迴圈非阻塞更新。"""
    global led_mode, led_duty, led_dir
    led_mode = mode
    if mode == "on":
        led_pwm.duty_u16(65535)
    elif mode == "off":
        led_pwm.duty_u16(0)
    elif mode == "breathe":
        led_duty = 0
        led_dir = 1
    print("[led] {}".format(mode))


def led_tick():
    """行為層: 呼吸燈每輪主迴圈更新一步，僅在 breathe 模式有效。"""
    global led_duty, led_dir
    if led_mode != "breathe":
        return
    led_duty += LED_STEP * led_dir
    if led_duty >= 65535:
        led_duty = 65535
        led_dir = -1
    elif led_duty <= 0:
        led_duty = 0
        led_dir = 1
    led_pwm.duty_u16(led_duty)


# ── 步進馬達 ─────────────────────────────────────────────────


def step_release():
    """行為層: 關閉所有線圈，避免持續通電過熱。"""
    for c in step_coils:
        c.value(0)


def step_move(steps):
    """流程層: 轉動指定步數，steps>0 順時針，steps<0 逆時針，完成後 release。"""
    direction = 1 if steps >= 0 else -1
    idx = 0
    for _ in range(abs(steps)):
        seq = STEP_SEQ[idx % 8]
        for j, c in enumerate(step_coils):
            c.value(seq[j])
        time.sleep_ms(STEP_DELAY_MS)
        idx += direction
    step_release()
    print("[step] done ({} steps)".format(steps))


def step_turn(revolutions):
    """流程層: 轉動指定圈數（支援小數），轉換為步數後呼叫 step_move。"""
    steps = int(STEPS_PER_REV * revolutions)
    print("[step] turning {} rev = {} steps".format(revolutions, steps))
    step_move(steps)


# ── 指令派發 ─────────────────────────────────────────────────


def handle_cmd(line):
    """流程層: 解析序列埠指令並依 mode 派發給對應模組。"""
    global current_mode
    parts = line.strip().split()
    if not parts:
        return
    cmd = parts[0]

    if cmd == "relay":
        if len(parts) < 2:
            print("[err] relay 1 or relay 0")
            return
        relay_set(int(parts[1]))

    elif cmd == "mode":
        if len(parts) < 2 or parts[1] not in ("servo", "step"):
            print("[err] mode servo | mode step")
            return
        current_mode = parts[1]
        print("[mode] {}".format(current_mode))

    elif cmd == "led":
        if len(parts) < 2 or parts[1] not in ("on", "off", "breathe"):
            print("[err] led on | led off | led breathe")
            return
        led_set(parts[1])

    elif cmd == "sweep":
        if not relay_enabled:
            print("[err] relay is OFF")
            return
        if current_mode != "servo":
            print("[err] switch to servo mode first")
            return
        sweep()

    elif cmd == "angle":
        if not relay_enabled:
            print("[err] relay is OFF")
            return
        if current_mode != "servo":
            print("[err] switch to servo mode first")
            return
        if len(parts) < 2:
            print("[err] angle <0-180>")
            return
        set_angle(int(parts[1]))

    elif cmd == "turn":
        if not relay_enabled:
            print("[err] relay is OFF")
            return
        if current_mode != "step":
            print("[err] switch to step mode first")
            return
        if len(parts) < 2:
            print("[err] turn <圈數>")
            return
        step_turn(float(parts[1]))

    elif cmd == "steps":
        if not relay_enabled:
            print("[err] relay is OFF")
            return
        if current_mode != "step":
            print("[err] switch to step mode first")
            return
        if len(parts) < 2:
            print("[err] steps <步數>")
            return
        step_move(int(parts[1]))

    else:
        print("[err] unknown: {}".format(cmd))


print("Motor Console v0.5")
print("relay 1/0 | mode servo/step | angle/sweep | turn/steps | led on/off/breathe")

poller = select.poll()
poller.register(sys.stdin, select.POLLIN)
sys.stdout.write("> ")

buf = ""
while True:
    while poller.poll(0):  # 一次讀完緩衝區所有字元，避免快打掉字
        ch = sys.stdin.read(1)
        if ch in ("\r", "\n"):
            sys.stdout.write("\r\n")
            if buf:
                handle_cmd(buf)
                buf = ""
            sys.stdout.write("> ")
        elif ch in ("\x08", "\x7f"):  # 退格鍵：刪掉 buf 末字並清畫面
            if buf:
                buf = buf[:-1]
                sys.stdout.write("\x08 \x08")
        elif " " <= ch <= "~":
            buf += ch
            sys.stdout.write(ch)  # 回顯，讓使用者看到自己打的字
    led_tick()
    time.sleep_ms(5)
