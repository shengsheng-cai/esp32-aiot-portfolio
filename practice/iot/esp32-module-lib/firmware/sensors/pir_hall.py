"""
PIR 人體紅外線感應 + 霍爾效應感測器
Sensors - pir_hall

原始課程:
  38.人體紅外線感應模組 (HC-SR501)
  41.霍爾感應器 Hall effect sensor
  5.ESP32內建霍爾感應器（已廢棄，僅說明）

平台: ESP32 MicroPython

HC-SR501 說明:
  全自動感應，人進入感應範圍輸出 HIGH，離開後延時轉 LOW
  兩種觸發模式（跳線選擇）：
    L = 不可重複觸發（輸出 HIGH 後延時結束即轉 LOW）
    H = 可重複觸發（延時期間持續有人則保持 HIGH）
  初始化時間約 1 分鐘，通電後請等待穩定
  調整兩個 VR：靈敏度（感應距離）+ 延時時間

霍爾感應器（外接模組）說明:
  AO 類比輸出：磁場越強，讀值越大
  DO 數位輸出：磁場超過閾值時輸出 LOW（平時 HIGH）

ESP32 內建霍爾感應器說明:
  Arduino IDE 3.0+ 已刪除 hallRead() 函式
  MicroPython 亦無對應 API → 不建議使用
  若需要霍爾感應，請改用外接 Hall sensor 模組

硬體接線:
  HC-SR501  OUT → GPIO 14  VCC → 5V  GND → GND
  霍爾模組  AO  → GPIO 34  DO  → GPIO 33  VCC → 3.3V  GND → GND
  LED           → GPIO 2（內建）
"""

from machine import Pin, ADC
import time

LED_PIN = 2
PIR_PIN = 14

HALL_AO_PIN = 34
HALL_DO_PIN = 33


# ── 範例 1：PIR 人體偵測 ──────────────────────────────────────
def pir_demo():
    """
    偵測到人體移動時 LED 亮並印出提示
    注意：通電後等待約 1 分鐘讓模組初始化完成
    """
    pir = Pin(PIR_PIN, Pin.IN)
    led = Pin(LED_PIN, Pin.OUT)

    print("HC-SR501 PIR on GPIO{} — waiting 5s for warmup...".format(PIR_PIN))
    time.sleep(5)
    print("Ready. Detecting motion...")

    while True:
        if pir.value():
            print("Motion detected!")
            led.value(1)
        else:
            print("No motion")
            led.value(0)
        time.sleep(1)


def pir_interrupt_demo():
    """PIR 使用中斷（上升緣觸發），偵測瞬間反應"""
    pir = Pin(PIR_PIN, Pin.IN)
    led = Pin(LED_PIN, Pin.OUT)

    def motion_isr(pin):
        led.value(pin.value())
        print("IRQ:", "MOTION" if pin.value() else "CLEAR")

    pir.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=motion_isr)
    print("PIR IRQ ready. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)


# ── 範例 2：霍爾感應器（外接模組）────────────────────────────
def hall_demo():
    """
    磁鐵靠近時 AO 值變化，DO 由 HIGH 變 LOW
    可用於轉速計（計算 DO 脈衝次數）或磁場偵測
    """
    adc = ADC(Pin(HALL_AO_PIN))
    adc.atten(ADC.ATTN_11DB)
    do  = Pin(HALL_DO_PIN, Pin.IN)
    led = Pin(LED_PIN, Pin.OUT)

    print("Hall sensor — AO=GPIO{} DO=GPIO{}".format(HALL_AO_PIN, HALL_DO_PIN))
    while True:
        val = adc.read()
        detected = not do.value()   # DO 平時 HIGH；磁鐵靠近變 LOW
        print("Magnet Read={:4d}  DO={}".format(val, "DETECT" if detected else "none"))
        led.value(detected)
        time.sleep(1)


def hall_rpm_demo(sample_sec: int = 5):
    """
    計算轉速：將磁鐵固定在旋轉體上，DO 每轉一圈觸發一次
    sample_sec 秒內計算脈衝數，換算 RPM
    """
    do = Pin(HALL_DO_PIN, Pin.IN)
    count = [0]

    def pulse_isr(pin):
        count[0] += 1

    do.irq(trigger=Pin.IRQ_FALLING, handler=pulse_isr)
    print("Counting pulses for {} seconds...".format(sample_sec))
    time.sleep(sample_sec)
    do.irq(handler=None)

    rpm = count[0] * (60 / sample_sec)
    print("Pulses={} → {:.1f} RPM".format(count[0], rpm))


# ── 主程式（選擇一種模式）────────────────────────────────────
pir_demo()
# pir_interrupt_demo()
# hall_demo()
# hall_rpm_demo()
