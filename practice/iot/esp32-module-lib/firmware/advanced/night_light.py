"""
Night Light v0.1 — 六份 core-skills 完整整合
平台: ESP32 MicroPython

整合來源（原 core-skills 六模組，已全數合併至本檔，原獨立檔移除）:
  adc.py           → make_adc（光敏/可調電阻）+ PWM 亮度輸出
  basics.py        → 跑馬燈啟動動畫 + no_repeat 按鈕狀態機
  interrupt.py     → 按鈕 IRQ + PIR IRQ（旗標模式，ISR 不 print）
  sleep_wdt.py     → WDT 保護 + deep sleep（PIR 喚醒）+ boot_count + wakeup_reason
  flash_storage.py → JSON 存模式/門檻 + NVS 存開機次數
  dual_core.py     → Core0 讀感測器控燈；Core1 按鈕+睡眠+WDT；Lock + running 旗標

功能:
  自動模式：天黑 + 有人 → 主燈亮（可調電阻控亮度）；無人 30s → deep sleep
  常亮模式：強制開燈（亮度同可調電阻）
  關閉模式：強制熄燈
  按鈕切換三模式，設定存 flash 斷電保留
  開機跑跑馬燈動畫（deep sleep 喚醒跳過）；印出喚醒原因與開機次數

=== 接線 ===
  光敏電阻  → 一腳 3.3V，一腳 D35；230Ω 一腳 D35，一腳 GND
  可調電阻  → D34（中間腳，兩端 3.3V / GND）
  PIR      → 左腳GND、中腳D27、右腳VIN（可喚醒 deep sleep）
  按鈕     → D21（INPUT_PULLUP，對角兩腳：一腳 GND，另腳 D21）
  主燈 LED → 用板子內建 LED，免接線；PWM 調亮度
  跑馬燈   → 每顆：Dxx → 220Ω → LED長腳 → LED短腳 → GND（D13/D12/D14/D4/D26/D25/D33/D32）

=== 規格 ===
  ADC: 12 bit，0~3.3V → 0~4095
  光敏電阻: 值愈小愈暗（230Ω 實測：亮~150 / 全暗 0，門檻 80）
  PWM: 1kHz，duty_u16 0~65535（0=全滅，65535=全亮）
  WDT: 8000ms
  Deep sleep: PIR 上升沿喚醒（D27，level=1）
  無人超時: 30s（NO_MOTION_S）

=== 操作 ===
  [實體] 按一下按鈕   循環切換模式（自動 → 常亮 → 關閉 → 自動）
  模式存入 flash，斷電後保留

=== 硬體清單 ===
  ESP32 x1、光敏電阻 x1、230Ω x1、可調電阻 x1、PIR x1
  4-pin 按鈕 x1、LED x8（跑馬燈）、220Ω x8、杜邦線若干

=== 注意 ===
  - D34/D35 輸入專用，不可輸出
  - D27 給 PIR（可喚醒 deep sleep）；跑馬燈故意避開（改用 D4）
  - Deep sleep 後 RAM 清空，開機次數靠 NVS 保留
  - ISR 內不可 print；PIR/按鈕事件均用旗標，主迴圈處理
  - Core0 以 running=False 旗標優雅退出後再呼叫 deepsleep()
  - 驗證狀態: 程式層級核對，待實機驗證
"""

import time
import machine
import esp32
import _thread
from machine import Pin, ADC, PWM, WDT

# ── 腳位 ────────────────────────────────────────────────────
LDR_PIN = 35
VR_PIN = 34
PIR_PIN = 27
BTN_PIN = 21
LED_PIN = 2
KNIGHT_PINS = [13, 12, 14, 4, 26, 25, 33, 32]  # D27 留給 PIR，改用 D4

# ── 參數 ────────────────────────────────────────────────────
CONFIG_FILE = "/nightlight_config.json"
NVS_NS = "nightlight"
DARK_DEFAULT = 80  # 低於此值視為天黑（230Ω 實測：亮~150 / 全暗 0，範圍很扁）
NO_MOTION_S = 30  # 自動模式無人超時 → deep sleep
WDT_MS = 8000
MODES = ["auto", "on", "off"]


# ── NVS 開機次數（來源 flash_storage.py: nvs_demo / get_boot_count）──
# 用 NVS 而非 RTC memory：硬重置後計數也保留（RTC memory 只撐過 deep sleep）


def get_boot_count() -> int:
    try:
        nvs = esp32.NVS(NVS_NS)
        return nvs.get_i32("boot_count")
    except OSError:
        return 0


def save_boot_count(n: int):
    nvs = esp32.NVS(NVS_NS)
    nvs.set_i32("boot_count", n)
    nvs.commit()


# ── 喚醒原因（來源 sleep_wdt.py: print_wakeup_reason）──────


def get_wakeup_reason() -> int:
    cause = machine.reset_cause()
    names = {
        machine.PWRON_RESET: "Power on",
        machine.HARD_RESET: "Hard reset",
        machine.WDT_RESET: "WDT reset",
        machine.DEEPSLEEP_RESET: "Wake from deep sleep",
        machine.SOFT_RESET: "Soft reset",
    }
    print("[boot] Reset cause:", names.get(cause, "Unknown({})".format(cause)))
    return cause


# ── ADC（來源 adc.py: make_adc）────────────────────────────


def make_adc(pin: int) -> ADC:
    adc = ADC(Pin(pin))
    adc.atten(ADC.ATTN_11DB)
    adc.width(ADC.WIDTH_12BIT)
    return adc


# ── JSON 設定（來源 flash_storage.py: load_config）──────────


def load_config() -> dict:
    import json

    defaults = {"mode": 0, "dark_threshold": DARK_DEFAULT}
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        updated = False
        for k, v in defaults.items():
            if k not in cfg:
                cfg[k] = v
                updated = True
        if updated:
            _save_json(cfg)
        return cfg
    except OSError:
        _save_json(defaults)
        return dict(defaults)


def _save_json(cfg: dict):
    import json

    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)


def save_config(cfg: dict):
    """行為層: 將目前設定（模式、門檻）寫回 JSON 檔。"""
    _save_json(cfg)


# ── 跑馬燈動畫（來源 basics.py: knight_rider_demo）──────────


def knight_rider(rounds: int = 2):
    """流程層: 開機啟動動畫，跑馬燈左右掃兩趟後熄滅。"""
    leds = [Pin(p, Pin.OUT) for p in KNIGHT_PINS]

    def all_off():
        for l in leds:
            l.value(0)

    for _ in range(rounds):
        for i in range(len(leds)):
            leds[i].value(1)
            time.sleep_ms(80)
            all_off()
        for i in range(len(leds) - 2, 0, -1):
            leds[i].value(1)
            time.sleep_ms(80)
            all_off()

    all_off()


# ── PWM 主燈（來源 adc.py: vr_led_demo ADC→PWM 輸出）────────

_led_pwm = PWM(Pin(LED_PIN), freq=1000)


def set_led(brightness_pct: int):
    """行為層: 設定主燈亮度 0~100%，對應 duty_u16 0~65535。"""
    duty = brightness_pct * 65535 // 100
    _led_pwm.duty_u16(duty)


# ── 按鈕 + PIR 中斷（來源 interrupt.py: btn_isr / pir_isr）──

_btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)
_pir = Pin(PIR_PIN, Pin.IN)

_btn_flag = False
_btn_debounce = 0
_pir_flag = False
_pir_last_ms = 0


def btn_isr(_pin):
    global _btn_flag, _btn_debounce
    now = time.ticks_ms()
    if time.ticks_diff(now, _btn_debounce) > 300:
        _btn_flag = True
        _btn_debounce = now


def pir_isr(_pin):
    global _pir_flag, _pir_last_ms
    _pir_flag = True
    _pir_last_ms = time.ticks_ms()


_btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_isr)
_pir.irq(trigger=Pin.IRQ_RISING, handler=pir_isr)

# deep sleep 喚醒來源設定（PIR HIGH 喚醒）
esp32.wake_on_ext0(pin=_pir, level=1)


# ── 雙核心共用狀態（來源 dual_core.py: lock / running）──────

lock = _thread.allocate_lock()
running = True  # Core0 生命週期旗標（False → 執行緒自動退出）
_sleep_requested = False  # Core0 偵測到無人超時，通知 Core1 進入 deep sleep


# ── Core0：感測器讀值 + 控燈（來源 dual_core.py: task1）─────


def sensor_task():
    """Core0：持續讀光敏電阻 / 可調電阻 / PIR，依模式更新主燈亮度。"""
    global _sleep_requested
    ldr = make_adc(LDR_PIN)
    vr = make_adc(VR_PIN)
    no_motion_start = time.ticks_ms()

    while running:
        with lock:
            mode = config["mode"]
            threshold = config["dark_threshold"]
            # PIR 曾觸發 且 在 NO_MOTION_S 秒內
            has_pir = _pir_flag and time.ticks_diff(time.ticks_ms(), _pir_last_ms) < NO_MOTION_S * 1000

        ldr_val = ldr.read()
        vr_val = vr.read()
        is_dark = ldr_val < threshold
        brightness = vr_val * 100 // 4095  # ADC 0~4095 → 0~100%

        if mode == 0:  # 自動
            if is_dark and has_pir:
                set_led(brightness)
                no_motion_start = time.ticks_ms()
            else:
                set_led(0)
                elapsed = time.ticks_diff(time.ticks_ms(), no_motion_start)
                if elapsed > NO_MOTION_S * 1000:
                    with lock:
                        _sleep_requested = True
        elif mode == 1:  # 常亮
            set_led(brightness)
            no_motion_start = time.ticks_ms()
        else:  # 關閉
            set_led(0)
            no_motion_start = time.ticks_ms()

        time.sleep_ms(200)


# ── 初始化 ──────────────────────────────────────────────────

boot_count = get_boot_count() + 1
save_boot_count(boot_count)
wakeup = get_wakeup_reason()
print("[boot] count={} mode=boot".format(boot_count))

config = load_config()
wdt = WDT(timeout=WDT_MS)

# deep sleep 喚醒時跳過跑馬燈（sleep_wdt.py: DEEPSLEEP_RESET）
if wakeup != machine.DEEPSLEEP_RESET:
    print("[boot] Startup animation...")
    knight_rider()
else:
    # PIR 喚醒：直接視為有人，更新旗標
    with lock:
        _pir_flag = True
        _pir_last_ms = time.ticks_ms()

print(
    "[nightlight] mode={} dark_threshold={}".format(
        MODES[config["mode"]], config["dark_threshold"]
    )
)

_thread.start_new_thread(sensor_task, ())  # 啟動 Core0


# ── Core1 主迴圈（來源 dual_core.py: task2）─────────────────

btn_released = True  # no_repeat 狀態機（來源 basics.py: no_repeat_demo）

while True:
    wdt.feed()  # 來源 sleep_wdt.py

    # ── 按鈕 no_repeat（basics.py）──────────────────────────
    # ISR 設旗標（interrupt.py），Core1 以 no_repeat 狀態機處理，每按只觸發一次
    if _btn_flag and btn_released:
        _btn_flag = False
        btn_released = False
        with lock:
            config["mode"] = (config["mode"] + 1) % len(MODES)
            new_mode = config["mode"]
        save_config(config)
        print("[mode] →", MODES[new_mode])

    if _btn.value() == 1:
        btn_released = True

    # ── Deep sleep 請求（sleep_wdt.py: deepsleep）───────────
    with lock:
        do_sleep = _sleep_requested

    if do_sleep:
        with lock:
            running = False  # 停止 Core0（dual_core.py: running 旗標）
        time.sleep_ms(300)  # 等 Core0 退出
        set_led(0)
        save_config(config)
        print("[sleep] No motion {}s → deep sleep. PIR will wake.".format(NO_MOTION_S))
        time.sleep_ms(100)
        machine.deepsleep()  # PIR HIGH 喚醒（esp32.wake_on_ext0）

    time.sleep_ms(10)
