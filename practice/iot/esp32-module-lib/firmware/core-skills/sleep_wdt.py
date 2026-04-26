"""
深度睡眠與看門狗計時器
Core-Skills - sleep_wdt

原始課程: 8.ESP32_睡眠模式與任務看門狗計時器
平台: ESP32 MicroPython

功能:
  深度睡眠（Timer 定時喚醒 / 外部 GPIO 喚醒）
  看門狗計時器（超時自動重啟）

ESP32 睡眠模式功耗:
  Active     ~240mA
  Light Sleep ~0.8mA
  Deep Sleep  ~10µA
  Hibernate   ~2.5µA（RTC 關閉，只保留 RTC timer）

注意事項:
  - Deep Sleep 後 RAM 清空，喚醒等同重開機（從 setup 開始執行）
  - 保留資料需使用 RTC memory（MicroPython: rtc.memory()）
  - 外部喚醒只能使用 RTC GPIO（GPIO 0,2,4,12~15,25~27,32~39）

硬體接線（外部喚醒範例）:
  按鈕 → GPIO 33（RTC GPIO，按下接 HIGH）
"""

import machine
import esp32
import time

rtc = machine.RTC()


# ── 開機次數（存於 RTC memory，Deep Sleep 後保留）────────────
def get_boot_count() -> int:
    try:
        return int(rtc.memory().decode())
    except Exception:
        return 0

def save_boot_count(n: int):
    rtc.memory(str(n).encode())


# ── 喚醒原因 ─────────────────────────────────────────────────
def print_wakeup_reason():
    cause = machine.reset_cause()
    reasons = {
        machine.PWRON_RESET:    "Power on / hard reset",
        machine.HARD_RESET:     "Hard reset",
        machine.WDT_RESET:      "Watchdog reset",
        machine.DEEPSLEEP_RESET:"Wake from deep sleep",
        machine.SOFT_RESET:     "Soft reset",
    }
    print("Reset cause:", reasons.get(cause, "Unknown ({})".format(cause)))


# ── 範例 1：Timer 定時喚醒 ────────────────────────────────────
def deep_sleep_timer(seconds: int = 5):
    """進入深度睡眠，幾秒後自動喚醒"""
    count = get_boot_count() + 1
    save_boot_count(count)
    print("Boot count:", count)
    print_wakeup_reason()
    print("Going to deep sleep for {}s...".format(seconds))
    time.sleep_ms(100)   # 等序列埠輸出完畢
    machine.deepsleep(seconds * 1000)


# ── 範例 2：外部 GPIO 喚醒 ────────────────────────────────────
def deep_sleep_ext_wakeup(gpio_num: int = 33, level: int = 1):
    """
    進入深度睡眠，由外部 GPIO 喚醒
    gpio_num: RTC GPIO 編號
    level: 1 = HIGH 喚醒, 0 = LOW 喚醒
    """
    esp32.wake_on_ext0(pin=machine.Pin(gpio_num), level=level)
    print("Deep sleep until GPIO {} goes {}...".format(gpio_num, "HIGH" if level else "LOW"))
    time.sleep_ms(100)
    machine.deepsleep()


# ── 範例 3：看門狗計時器 ──────────────────────────────────────
def watchdog_demo(timeout_ms: int = 5000):
    """
    啟用看門狗，主迴圈內定期餵狗
    若超過 timeout_ms 未餵狗則自動重啟
    按鈕（GPIO 23）按住超過 timeout 即觸發重啟
    """
    wdt = machine.WDT(timeout=timeout_ms)
    btn = machine.Pin(23, machine.Pin.IN, machine.Pin.PULL_UP)
    count = 0

    print("WDT enabled ({}ms). Hold button to trigger reset.".format(timeout_ms))

    while True:
        count += 1
        print("Loop:", count)

        if btn.value() == 1:   # 按鈕未按下時才餵狗
            wdt.feed()

        time.sleep_ms(1000)


# ── 主程式（選擇一種模式）────────────────────────────────────
# deep_sleep_timer(seconds=5)
# deep_sleep_ext_wakeup(gpio_num=33, level=1)
watchdog_demo(timeout_ms=5000)
