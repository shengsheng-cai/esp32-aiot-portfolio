# 繼電器控制模組
# 對應原始：myI2C.py 的 dev_On() / dev_Off()（RPi GPIO 17 → ESP32 machine.Pin）
# HW-482 繼電器接線：S → ESP32 GPIO(RELAY_PIN)，+ → 5V，- → GND

from machine import Pin

RELAY_PIN = 17

_relay = Pin(RELAY_PIN, Pin.OUT)
_relay.value(0)


def on():
    _relay.value(1)


def off():
    _relay.value(0)


def state():
    return _relay.value()
