"""
類比感測模組：聲音 / 雨水 / 水位 / 火焰
Sensors - analog_sensors

原始課程:
  17.ESP32_聲音檢測模組 / 22.聲音檢測模組
  18.ESP32_雨水感測模組 / 24.雨水感測模組
  23.水位感測模組
  34.火焰傳感器

平台: ESP32 MicroPython

共同特點:
  模組均以 LM393 雙比較器為核心
  提供 AO（類比，反映強度）與 DO（數位，超過閾值觸發）
  ESP32 ADC 範圍 0〜4095（12-bit），與 Arduino 0〜1023（10-bit）不同

ESP32 ADC 注意:
  GPIO 34〜39 僅能輸入（input-only），適合 AO
  ADC2 在 WiFi 啟用時無法使用；優先選 ADC1（GPIO 32〜39）

硬體接線（以下為 ESP32 腳位，可自行調整）:
  聲音模組  AO → D34  DO → D35  VCC→3.3V  GND→GND
  雨水模組  AO → D34  DO → D35  VCC→3.3V  GND→GND
  水位模組  AO → D34           VCC→3.3V  GND→GND（感測探頭與供電分開）
  火焰感測  AO → D34           VCC→3.3V  GND→GND
  LED           → D2（內建）
"""

from machine import Pin, ADC
import time

LED_PIN   = 2
AO_PIN    = 34   # 類比輸出（input-only）
DO_PIN    = 35   # 數位輸出


def _adc(pin: int) -> ADC:
    a = ADC(Pin(pin))
    a.atten(ADC.ATTN_11DB)   # 0〜3.3V 範圍
    return a


# ── 範例 1：聲音偵測 ──────────────────────────────────────────
SOUND_THRESHOLD = 2000  # 課程建議 ESP32 約 2000〜2100（3.3V 供電）


def sound_demo():
    """
    讀取麥克風 AO 值並印出；超過閾值時 LED 亮
    調整模組上的 VR 電阻，使環境靜音時 AO 值穩定在 SOUND_THRESHOLD 以下
    """
    adc = _adc(AO_PIN)
    led = Pin(LED_PIN, Pin.OUT)
    print("Sound sensor — threshold={}".format(SOUND_THRESHOLD))

    while True:
        val = adc.read()
        if val > SOUND_THRESHOLD:
            print("Sound! val={}".format(val))
            led.value(1)
        else:
            led.value(0)
        time.sleep_ms(50)


def sound_clap_demo():
    """拍手偵測：聲音超過閾值時切換 LED 狀態"""
    adc = _adc(AO_PIN)
    led = Pin(LED_PIN, Pin.OUT)
    state = False

    print("Clap detector ready")
    while True:
        val = adc.read()
        if val > SOUND_THRESHOLD:
            state = not state
            led.value(state)
            print("Clap! LED:", "ON" if state else "OFF")
            time.sleep_ms(300)   # 防抖
        time.sleep_ms(20)


# ── 範例 2：雨水感測 ──────────────────────────────────────────
def rain_demo():
    """
    AO 越小 → 水越多（雨水越多短路路徑越多，阻抗越小，輸出越低）
    完全乾燥時 AO ≈ 4095；DO: HIGH=乾燥 / LOW=有雨（模組指示燈與 DO 反相）
    """
    adc = _adc(AO_PIN)
    do  = Pin(DO_PIN, Pin.IN)
    led = Pin(LED_PIN, Pin.OUT)

    print("Rain sensor — AO=GPIO{} DO=GPIO{}".format(AO_PIN, DO_PIN))
    while True:
        val   = adc.read()
        state = do.value()   # 0=有雨（LED 亮），1=無雨
        print("AO={:4d}  DO={}  {}".format(
            val, state, "DRY" if state else "RAIN"))
        led.value(not state)   # DO 低電位（有雨）時點亮 LED
        time.sleep_ms(500)


# ── 範例 3：水位感測 ──────────────────────────────────────────
WATER_MAX_ADC  = 3800   # 校正值：感測板全浸時的 ADC 讀值
WATER_MAX_DEPTH_CM = 4  # 感測板最大量測深度（cm）

RED_PIN    = 32
YELLOW_PIN = 33
GREEN_PIN  = 25


def water_level_demo():
    """
    將 AO 值映射為水位深度（cm）
    HIGH: 指示燈紅 + 蜂鳴  MIDDLE: 黃  LOW: 綠  NONE: 全暗
    """
    adc = _adc(AO_PIN)

    print("Water level sensor")
    while True:
        val   = adc.read()
        depth = (val / WATER_MAX_ADC) * WATER_MAX_DEPTH_CM

        if val > 2764:          # > 4095 * 0.67 — HIGH
            level = "HIGH"
        elif val > 2600:
            level = "MIDDLE"
        elif val > 400:
            level = "LOW"
        else:
            level = "NO WATER"

        print("AO={:4d}  depth≈{:.1f}cm  {}".format(val, depth, level))
        time.sleep_ms(500)


# ── 範例 4：火焰感測 ──────────────────────────────────────────
FLAME_THRESHOLD = 500   # 課程建議：有火焰時 AO 值較低（越接近 0 越強）


def flame_demo():
    """
    火焰感測器（紅外接收三極管）：有火焰時 AO 值降低
    可加蜂鳴器做警報器
    """
    adc = _adc(AO_PIN)
    led = Pin(LED_PIN, Pin.OUT)

    print("Flame sensor — threshold={}".format(FLAME_THRESHOLD))
    while True:
        val = adc.read()
        if val < FLAME_THRESHOLD:
            print("FLAME detected! val={}".format(val))
            led.value(1)
        else:
            led.value(0)
        time.sleep_ms(200)


# ── 主程式（選擇一種模式）────────────────────────────────────
sound_demo()
# sound_clap_demo()
# rain_demo()
# water_level_demo()
# flame_demo()
