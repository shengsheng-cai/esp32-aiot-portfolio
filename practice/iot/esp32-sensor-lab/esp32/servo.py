from machine import PWM, Pin
import time

FREQ = 50
# SG90 接線：棕=GND, 紅=5V, 橘=控制訊號 → ESP32 GPIO
# SG90: 0.5ms~2.4ms pulse width @ 50Hz
# duty_u16 range: 0~65535
_MIN_US = 500
_MAX_US = 2400
_PERIOD_US = 20000


def _us_to_duty(us):
    return int(us / _PERIOD_US * 65535)


class Servo:
    def __init__(self, pin=13):
        self.pwm = PWM(Pin(pin), freq=FREQ)
        self.angle = 90
        self.write(90)

    def write(self, angle):
        angle = max(0, min(180, angle))
        us = _MIN_US + (_MAX_US - _MIN_US) * angle // 180
        self.pwm.duty_u16(_us_to_duty(us))
        self.angle = angle

    def sweep(self, start=0, end=180, step=1, delay_ms=10):
        for a in range(start, end + 1, step):
            self.write(a)
            time.sleep_ms(delay_ms)
        for a in range(end, start - 1, -step):
            self.write(a)
            time.sleep_ms(delay_ms)

    def deinit(self):
        self.pwm.deinit()
