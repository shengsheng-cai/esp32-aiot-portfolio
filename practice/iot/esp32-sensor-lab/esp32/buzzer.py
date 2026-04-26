from machine import PWM, Pin
import time

NOTES = {
    'Do': 523,
    'Re': 587,
    'Mi': 659,
    'Fa': 698,
    'Sol': 784,
    'La': 880,
    'Si': 988,
}


class Buzzer:
    def __init__(self, pin=12):
        self.pin = pin
        self.pwm = None

    def _on(self, freq):
        self.pwm = PWM(Pin(self.pin), freq=freq, duty=512)

    def _off(self):
        if self.pwm:
            self.pwm.deinit()
            self.pwm = None

    def play(self, note, duration_ms=500):
        freq = NOTES.get(note, 440)
        self._on(freq)
        time.sleep_ms(duration_ms)
        self._off()
        time.sleep_ms(50)

    def do_re_mi(self):
        for note in ['Do', 'Re', 'Mi']:
            print(note)
            self.play(note, 800)
