from machine import UART, PWM, Pin
import time

# 對應 i2c-servo.ino：Arduino I2C slave (0x11) 接收角度 → 控制 SG90
# ESP32 MicroPython 不支援 I2C slave，改用 UART 接收角度值

try:
    from i2c_lcd import LCD
except Exception:
    LCD = None

UART_ID   = 0
BAUD      = 9600
SERVO_PIN = 9
RELAY_PIN = 17

FREQ    = 50
MIN_US  = 500
MAX_US  = 2400
PERIOD  = 20000

uart  = UART(UART_ID, baudrate=BAUD, tx=1, rx=3)
servo = PWM(Pin(SERVO_PIN), freq=FREQ)
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0)

led = Pin(13, Pin.OUT)
led.value(1)
lcd = None


def angle_to_duty(angle):
    us = MIN_US + (MAX_US - MIN_US) * angle // 180
    return int(us / PERIOD * 65535)


def write_angle(angle):
    angle = max(0, min(180, angle))
    servo.duty_u16(angle_to_duty(angle))
    print('angle:', angle)


def set_relay(on):
    relay.value(1 if on else 0)
    print('relay:', 'H' if on else 'L')


def show_lcd(text):
    if lcd is None:
        return False
    s = str(text)
    lcd.show(s[:16], s[16:32])
    print('lcd:', s)
    return True


def handle_line(line):
    line = line.strip()
    if not line:
        return

    if line.startswith('LCD:'):
        ok = show_lcd(line[4:])
        uart.write('LCD:OK\n' if ok else 'LCD:NA\n')
        return

    if line == 'RELAY:H':
        set_relay(True)
        uart.write('RELAY:H\n')
        return

    if line == 'RELAY:L':
        set_relay(False)
        uart.write('RELAY:L\n')
        return

    if line.startswith('A:'):
        line = line[2:]

    try:
        angle = int(line)
        write_angle(angle)
        uart.write(str(angle) + '\n')  # echo back
    except ValueError:
        uart.write('ERR\n')


write_angle(90)

if LCD is not None:
    try:
        lcd = LCD()
        lcd.show('ESP32 READY', 'UART CONTROL')
    except Exception as e:
        print('lcd init fail:', e)

print('Ready!')

buf = b''
while True:
    if uart.any():
        buf += uart.read(uart.any())
        if b'\n' in buf:
            line, buf = buf.split(b'\n', 1)
            try:
                handle_line(line.decode().strip())
            except Exception as e:
                print('cmd error:', e)
                uart.write('ERR\n')
    time.sleep_ms(10)
