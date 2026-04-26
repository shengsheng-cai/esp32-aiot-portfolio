from machine import PWM, Pin
import time


class LedBreath:
    def __init__(self, pin=2, freq=1000):
        self.pwm = PWM(Pin(pin), freq=freq)

    def breath(self, steps=100, delay_ms=10):
        for dc in range(0, steps + 1):
            self.pwm.duty(dc * 1023 // steps)
            time.sleep_ms(delay_ms)
        for dc in range(steps, -1, -1):
            self.pwm.duty(dc * 1023 // steps)
            time.sleep_ms(delay_ms)

    def off(self):
        self.pwm.duty(0)

    def deinit(self):
        self.pwm.deinit()
