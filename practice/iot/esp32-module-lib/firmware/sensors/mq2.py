"""
MQ-2 氣體偵測模組
Sensors - mq2

原始課程: 42.ESP32 MQ-2氣體偵測模組
平台: ESP32 MicroPython

功能:
  範例 1: 讀取類比氣體濃度 + 數位警報（LED）

MQ-2 說明:
  MOS 感測器（金屬氧化物半導體）
  可偵測：液化石油氣、酒精、丙烷、氫氣、一氧化碳、甲烷
  偵測範圍：200〜10000 ppm（0.02%〜1%）
  工作電壓 5V（Vcc 接 5V，IO 信號與 3.3V 相容）

重要注意事項:
  使用前需預熱 5〜10 分鐘，才能有效量測
  AO 值隨氣體濃度增加而升高
  DO 輸出與模組信號 LED 成反比（LED 亮 = DO 輸出 LOW = 有氣體）
  VR 可調 DO 的觸發靈敏度，不影響 AO 輸出值

硬體接線:
  MQ-2 Aout → GPIO 34（ADC1，input-only）
  MQ-2 Dout → GPIO 13
  MQ-2 VCC  → 5V（建議），GND → GND
  LED       → GPIO 2（內建）
"""

from machine import Pin, ADC
import time

MQ2_AO_PIN = 34
MQ2_DO_PIN = 13
LED_PIN    = 2

WARMUP_SEC = 10   # 預熱時間（實際使用建議 300 秒）


def _make_adc(pin: int) -> ADC:
    a = ADC(Pin(pin))
    a.atten(ADC.ATTN_11DB)
    return a


# ── 範例：氣體偵測（AO + DO）─────────────────────────────────
def gas_demo():
    """
    AO 讀取氣體濃度（值越高濃度越高）
    DO 數位警報（LOW = 偵測到氣體 → 點亮 LED）
    """
    adc = _make_adc(MQ2_AO_PIN)
    do  = Pin(MQ2_DO_PIN, Pin.IN)
    led = Pin(LED_PIN, Pin.OUT)

    print("MQ-2 warming up for {}s...".format(WARMUP_SEC))
    for i in range(WARMUP_SEC, 0, -1):
        print("  {}s remaining...".format(i))
        time.sleep(1)
    print("MQ-2 ready. Monitoring gas levels.")

    while True:
        adc_val    = adc.read()
        gas_signal = not do.value()   # LOW = 有氣體
        led.value(gas_signal)
        status = "ALERT" if gas_signal else "normal"
        print("Gas Sensor Val: {:4d}  DO: {}".format(adc_val, status))
        time.sleep_ms(500)


# ── 主程式 ────────────────────────────────────────────────────
gas_demo()
