"""
Keypad 診斷腳本 - 印出實際 row/col 索引
按每個鍵，對照印出的 (row, col) 來確認接線是否正確
"""
import time
from machine import Pin

ROW_PINS = (5, 13, 14, 15)
COL_PINS = (18, 19, 21, 23)

rows = [Pin(p, Pin.IN, Pin.PULL_UP) for p in ROW_PINS]
cols = [Pin(p, Pin.OUT) for p in COL_PINS]
for col in cols:
    col.value(1)

last = None

while True:
    key = None
    for c_idx, col in enumerate(cols):
        col.value(0)
        for r_idx, row in enumerate(rows):
            if row.value() == 0:
                col.value(1)
                key = (r_idx, c_idx)
                break
        col.value(1)
        if key:
            break

    if key != last:
        if key:
            print("row={} col={}  (ROW_PIN={} COL_PIN={})".format(
                key[0], key[1], ROW_PINS[key[0]], COL_PINS[key[1]]))
        last = key

    time.sleep_ms(50)
