from machine import I2C, Pin
import time

LCD_ADDR = 0x27
LCD_COLS = 16
LCD_ROWS = 2

_CMD  = 0x00
_DATA = 0x40

_CLEAR        = 0x01
_HOME         = 0x02
_ENTRY_MODE   = 0x04
_DISPLAY_ON   = 0x0C
_FUNCTION_SET = 0x28  # 4-bit, 2 lines, 5x8

_BACKLIGHT = 0x08
_EN = 0x04
_RW = 0x02
_RS = 0x01


class LCD:
    def __init__(self, sda=21, scl=22, freq=400000):
        self.i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=freq)
        self.addr = LCD_ADDR
        self._init()

    def _write_byte(self, data):
        self.i2c.writeto(self.addr, bytes([data | _BACKLIGHT]))

    def _pulse(self, data):
        self._write_byte(data | _EN)
        time.sleep_us(1)
        self._write_byte(data & ~_EN)
        time.sleep_us(50)

    def _send_nibble(self, nibble, mode=0):
        self._pulse(nibble | mode)

    def _send(self, data, mode=0):
        self._send_nibble(data & 0xF0, mode)
        self._send_nibble((data << 4) & 0xF0, mode)

    def _cmd(self, cmd):
        self._send(cmd, 0)
        if cmd in (_CLEAR, _HOME):
            time.sleep_ms(2)

    def _init(self):
        time.sleep_ms(50)
        for _ in range(3):
            self._send_nibble(0x30)
            time.sleep_ms(5)
        self._send_nibble(0x20)
        time.sleep_ms(1)
        self._cmd(_FUNCTION_SET)
        self._cmd(_DISPLAY_ON)
        self._cmd(_CLEAR)
        self._cmd(_ENTRY_MODE | 0x02)

    def clear(self):
        self._cmd(_CLEAR)

    def home(self):
        self._cmd(_HOME)

    def move_to(self, col, row):
        offsets = [0x00, 0x40]
        self._cmd(0x80 | (offsets[row] + col))

    def putstr(self, text):
        for ch in text:
            self._send(ord(ch), _RS)

    def show(self, line1='', line2=''):
        self.clear()
        self.move_to(0, 0)
        self.putstr(line1[:LCD_COLS])
        if line2:
            self.move_to(0, 1)
            self.putstr(line2[:LCD_COLS])
