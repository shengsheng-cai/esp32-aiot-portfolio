"""
繼電器 Relay 控制
Control - relay

原始課程: 12.ESP32_繼電器Relay / 30.繼電器Relay
平台: ESP32 MicroPython

功能:
  透過序列埠輸入控制繼電器 ON/OFF
  傳送 '1' → 繼電器吸合（HIGH）
  傳送 '0' → 繼電器釋放（LOW）

硬體注意事項:
  - 使用兩路光耦繼電器模組（低電位觸發型無法直接接 ESP32，需外加電路）
  - 此範例使用「低電位觸發但光耦輸入為高電位」的雙路模組，ESP32 可正常驅動
  - 繼電器後端接馬達時，需注意 EMI 干擾可能造成 LCD/OLED 顯示錯誤或 MCU 重啟
  - 建議繼電器電源與 ESP32 電源完全隔離以降低干擾

硬體接線:
  繼電器 IN1 → GPIO 26
  繼電器 VCC → 5V
  繼電器 GND → GND
"""

import sys
from machine import Pin, UART

RELAY_PIN = 26

relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0)  # 預設關閉

print("Relay control ready. Send '1' to ON, '0' to OFF.")

while True:
    if not sys.stdin.any():
        continue
    cmd = sys.stdin.read(1)
    if cmd == '1':
        relay.value(1)
        print("Relay ON")
    elif cmd == '0':
        relay.value(0)
        print("Relay OFF")
