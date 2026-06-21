# esp32-sensor-lab

ESP32 MicroPython 基礎硬體控制學習實驗室。課程來源（泰山職訓局 2025~2026）將 Raspberry Pi 範例移植至 ESP32，全程 MicroPython。

## What I Built
ESP32 感測器節點：DHT11 讀溫濕度 → I2C LCD 顯示 → MQTT 發布，搭配 PC 端 Flask + MongoDB + WebSocket 即時溫度儀表板。另含舵機、蜂鳴器、LED 呼吸燈、NTP 對時等模組。

## Skills Demonstrated
- GPIO / PWM（舵機 · 蜂鳴器 · LED 呼吸燈）
- I2C（LCD 1602 + PCF8574）
- DHT11 溫濕度讀取
- WiFi 連線 + NTP 對時
- MQTT 發布 + 自動重連
- PC 端：Flask · flask-socketio · MongoDB · CanvasJS 即時圖表

## Hardware / Interface
ESP32 · DHT11 · I2C LCD（PCF8574 0x27）· SG90 舵機 · 被動蜂鳴器 · LED
介面：GPIO · PWM · I2C · WiFi · MQTT

```
D21/D22 → I2C SDA/SCL（LCD）
D15 → DHT11    D13 → SG90
D12 → 蜂鳴器   D2 → LED
```

## How to Run
1. 燒錄 MicroPython firmware 至 ESP32
2. 改 `esp32/main.py` 的 WiFi / MQTT 設定
3. 用 Thonny 或 `mpremote` 上傳 `esp32/` 至 ESP32
4. PC 端：`python host/mqtt_sub.py` 看 MQTT 資料，或啟動 `host/iot_dashboard/` 儀表板

## Validation Status
**程式層級練習，邏輯與結構已核對** — ESP32 端 + MQTT 資料流為核心，待實機接線驗證。
> ⚠️ `host/iot_dashboard/` 缺 `templates/index.html` 與 `templates/jquery.canvasjs.min.js`（原始碼未含），儀表板目前無法直接跑起來，需自行補齊。

## Next Step
接 DHT11 + I2C LCD 做最小實機驗證，補接線照片 + 終端 MQTT log；或補 `index.html` + `jquery.canvasjs.min.js` 讓儀表板完整跑通。

---

## 模組

| 模組 | 檔案 | 硬體 | 功能 |
|------|------|------|------|
| I2C LCD | `i2c_lcd.py` | LCD 1602 + PCF8574（0x27） | 字元顯示 |
| PWM 舵機 | `servo.py` | SG90（D13） | 0~180° 控制、掃描 |
| LED 呼吸燈 | `led_breath.py` | LED（D2） | PWM 漸亮漸暗 |
| 蜂鳴器 | `buzzer.py` | 被動蜂鳴器（D12） | Do Re Mi 音階 |
| NTP 時鐘 | `ntp_clock.py` | — | WiFi 對時，取代外接 RTC |
| 主程式 | `main.py` | DHT11（D15） | DHT 讀取 → LCD → MQTT pub |

## 技術棧
- 硬體：ESP32（38-pin 或相容板）
- 語言：MicroPython
- 通訊：WiFi + MQTT（umqtt.simple）
- PC 端：Flask · flask-socketio · pymongo · CanvasJS
