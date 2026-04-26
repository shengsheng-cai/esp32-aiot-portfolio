# ESP32 MicroPython 功能清單

整理自課程資料 + 現有專案規劃，用於後續商業模式評估。

> 難度：⭐ 入門 / ⭐⭐ 中等 / ⭐⭐⭐ 進階
> 硬體成本：台幣（NT$），參考來源 [台灣物聯科技 TaiwanIOT](https://www.taiwaniot.com.tw)，未稅零售價，僅供估算

---

## 核心技術 (core-skills)

| 功能 | 技術細節 | 硬體成本 | 難度 | 課程來源 |
|------|----------|----------|------|----------|
| 硬體中斷 | GPIO 事件觸發，不阻塞主程式 | — | ⭐⭐ | arduino/12, esp32/7 |
| 深度睡眠 | 2.5µA 低功耗，timer/GPIO 喚醒 | — | ⭐⭐ | arduino/12, esp32/8 |
| 看門狗計時器 | 異常自動重啟，提高可靠性 | — | ⭐⭐ | arduino/12, esp32/8 |
| PWM 輸出 | 類比控制（馬達速度、LED 亮度、蜂鳴頻率） | — | ⭐ | esp32/9 |
| ADC 類比輸入 | 讀取連續變化的感測數值（土壤濕度、光敏等） | — | ⭐ | esp32/4 |
| EEPROM 儲存 | 掉電後保留設定值 | — | ⭐ | esp32/2 |
| 雙核心處理 | Core0/Core1 分工，提升即時性 | — | ⭐⭐⭐ | esp32/32 |

---

## 感測器輸入 (sensors)

| 功能 | 技術細節 | 硬體成本 | 難度 | 課程來源 |
|------|----------|----------|------|----------|
| 溫濕度感測 | DHT11（±2°C, ±5%RH），室內環境監測 | NT$60 | ⭐ | arduino/25, esp32/15 |
| 聲音偵測 | 麥克風模組，數位觸發或類比音量 | NT$40 | ⭐ | arduino/22, esp32/17 |
| 水位感測 | 導電式，偵測有無水或液位高低 | NT$40 | ⭐ | arduino/23 |
| 雨水感測 | 同水位原理，偵測降雨或濺水 | NT$60 | ⭐ | arduino/24, esp32/18 |
| 火焰感測 | IR 光偵測，觸發警報 | NT$40 | ⭐ | arduino/34 |
| 人體紅外線 (PIR) | 偵測移動中的人體熱源 | NT$40 | ⭐ | arduino/38, esp32/7 |
| 霍爾感應器 | 偵測磁場，可用於轉速計數或門窗磁鐵 | NT$40 | ⭐⭐ | arduino/41, esp32/5 |
| 超音波測距 | HC-SR04，測距 2~400cm | NT$60 | ⭐ | elderly-care-radar |
| 三軸加速度 | ADXL335，偵測震動、傾斜、跌落 | NT$100~ | ⭐⭐ | esp32/39 |
| 氣體偵測 | MQ-2，偵測煙霧/瓦斯/可燃氣體 | NT$60 | ⭐⭐ | esp32/42 |
| 心率血氧 | MAX30100，SpO2 + BPM | NT$140 | ⭐⭐⭐ | esp32/44 |
| 電壓電流 | MAX471，監控供電狀態 | NT$40 | ⭐⭐ | esp32/47 |
| 秤重感測 | HX711，0.1g 精度 | NT$40 | ⭐⭐ | esp32/48 |
| RFID 讀取 | MFRC522，讀取 Mifare 標籤 UID | NT$140 | ⭐⭐ | boardgame-rfid-helper |

---

## 無線通訊 (networking)

| 功能 | 技術細節 | 硬體成本 | 難度 | 課程來源 |
|------|----------|----------|------|----------|
| WiFi 連線 | 連接 AP，獲取 IP，NTP 對時 | — | ⭐ | esp32/25, 26 |
| 靜態 IP | 固定 ESP32 的 IP 位址 | — | ⭐ | esp32/靜態IP |
| HTTP Web Server | 建立網頁伺服器，提供 UI 或 API | — | ⭐⭐ | esp32/27~29 |
| AsyncWebServer | 非同步處理多請求，效能更好 | — | ⭐⭐ | esp32/37 |
| URL 參數讀取 | GET 請求傳參數控制 GPIO | — | ⭐⭐ | esp32/30 |
| SPIFFS 靜態檔案 | 儲存 HTML/CSS/JS 到 flash | — | ⭐⭐ | esp32/38 |
| WebSocket | 雙向即時通訊，多客戶端同步更新 | — | ⭐⭐⭐ | esp32/45 |
| OTA 無線燒錄 | 不用接線更新韌體 | — | ⭐⭐⭐ | esp32/31 |
| Soft AP 模式 | ESP32 自己當 AP，不依賴路由器 | — | ⭐⭐ | esp32/29 |
| ESP-NOW | ESP32 間點對點無線通訊，不需 WiFi | — | ⭐⭐⭐ | esp32/36 |
| 藍牙 BLE | 低功耗藍牙，手機 App 連接 | — | ⭐⭐⭐ | esp32/24, BLE_test |
| 藍牙 SPP | 傳統藍牙串口，類似 USB 串口 | — | ⭐⭐ | arduino/35 |
| nRF24L01 | 2.4GHz 無線收發，低功耗遠距離 | NT$60 | ⭐⭐ | arduino/36 |
| MQTT 發布 | 感測器資料定時上傳至 broker | — | ⭐⭐ | networking/mqtt_publish.py |
| MQTT 訂閱 | 接收指令控制 Servo / Relay / LCD | — | ⭐⭐⭐ | networking/mqtt_control.py |

---

## 輸出控制 (control)

| 功能 | 技術細節 | 硬體成本 | 難度 | 課程來源 |
|------|----------|----------|------|----------|
| 繼電器控制 | 控制高壓/高電流設備（燈、幫浦、插座） | NT$40 | ⭐ | arduino/30, esp32/12 |
| 伺服馬達 | 0~180° 精確角度控制 | NT$60 | ⭐ | arduino/20, esp32/16 |
| 步進馬達 | 精確步數控制，用於位置精度高的場合 | NT$120 | ⭐⭐ | arduino/27, esp32/19 |
| 直流馬達 | L298N/L9110 驅動，正反轉速度控制 | NT$60 | ⭐⭐ | esp32/20 |
| LED 燈帶 | WS2812B 全彩 RGB，每顆獨立控制 | NT$200~/m | ⭐⭐ | arduino/45, esp32/35 |
| 蜂鳴器 | 無源蜂鳴器 PWM 驅動，分頻率警報 | NT$40 | ⭐ | elderly-care-radar |
| 8x8 矩陣 LED | MAX7219，顯示圖案或數字 | NT$80 | ⭐⭐ | esp32/46 |

---

## 人機介面 (interface)

| 功能 | 技術細節 | 硬體成本 | 難度 | 課程來源 |
|------|----------|----------|------|----------|
| OLED 顯示 | SSD1306 128x64，I2C，顯示文字/圖形 | NT$100 | ⭐⭐ | arduino/43, esp32/33 |
| TFT 彩色螢幕 | ST7735 128x128，SPI，彩色顯示 | NT$300 | ⭐⭐ | esp32/41 |
| I2C LCD | 16x2 點陣液晶，低成本文字顯示 | NT$80 | ⭐ | interface/i2c_lcd.py |
| 七段顯示器 | 數字顯示，TM1637 時鐘模組 | NT$40 | ⭐ | arduino/14~16, esp32/43 |
| 4x4 矩陣 Keypad | 16 鍵數字鍵盤輸入 | NT$40 | ⭐ | arduino/15, esp32/10 |
| 旋轉編碼器 | 旋鈕輸入，可無限旋轉 + 按壓 | NT$40 | ⭐⭐ | arduino/44, esp32/34 |
| 觸摸感測器 | 電容式觸控偵測 | NT$40~ | ⭐ | arduino/40, esp32/6 |
| 震動開關 | 偵測震動或傾斜 | NT$40 | ⭐ | arduino/39 |
| 紅外線遙控 | 接收遙控器訊號 | NT$80 | ⭐⭐ | arduino/29, esp32/22 |

---

## 時間/計時 (time)

| 功能 | 技術細節 | 硬體成本 | 難度 | 課程來源 |
|------|----------|----------|------|----------|
| DS1302 RTC | 即時時鐘模組，掉電後保時（精度較低） | NT$40~ | ⭐ | arduino/28, esp32/21 |
| DS3231 RTC | 高精度即時時鐘（溫度補償），更準確 | NT$100 | ⭐ | esp32/21-5 |
| NTP 網路對時 | 透過 WiFi 同步網路時間，不需 RTC | — | ⭐ | esp32/26 |

---

## 進階功能 (advanced)

| 功能 | 技術細節 | 硬體成本 | 難度 | 課程來源 |
|------|----------|----------|------|----------|
| DHT11 Web Server | ESP32 感測數據直接顯示在網頁 | NT$60 | ⭐⭐ | esp32/40 |
| Camera Web Server | ESP32-CAM 串流影像至網頁 | NT$300~ | ⭐⭐⭐ | CameraWebServer |
| MicroPython 基礎 | LED + DHT11 Python 實作範例 | — | ⭐ | 01_led_dht11 |
| 綜合應用 | Keypad + LCD 門禁管制機 | — | ⭐⭐ | arduino/19 |

---

## 待補課程（courses 裡尚未整理）

| 功能 | 備註 |
|------|------|
| 超音波測距 | 課程 PPTX 未移入（elderly-care-radar 引用的 esp32/13） |
| 蜂鳴器 | 課程 PPTX 未移入（esp32/14） |

---

## 基礎語法 (reference)

| 功能 | 技術細節 | 難度 | 課程來源 |
|------|----------|------|----------|
| Serial 調試 | 透過 UART 輸出 log，開發必備 | ⭐ | esp32/1-1 |
| GPIO 數位輸出 | LED 控制，基礎 blink | ⭐ | esp32/1-2 |
| For/While 迴圈 | 流水燈、跑馬燈邏輯 | ⭐ | esp32/1-3 |
| 按鈕輸入 + If 判斷 | 讀取 GPIO 狀態，條件控制 | ⭐ | esp32/1-4 |
| 按鈕防重複觸發 | millis() 計時，避免單次按壓多次觸發 | ⭐ | esp32/1-5 |
| 按鈕防彈跳 | 官方 debounce 實作 | ⭐⭐ | esp32/1-6 |

---

## MicroPython 實作範例 (firmware)

| 功能 | 技術細節 | 難度 | 來源 |
|------|----------|------|------|
| DHT11 + MQTT 發布 | WiFi 連線 → 讀溫濕度 → umqtt.robust 發布 | ⭐⭐ | networking/mqtt_publish.py |
| MQTT 訂閱控制硬體 | 接收指令控制 Servo / Relay / LCD | ⭐⭐⭐ | networking/mqtt_control.py |
| WiFi 自動重連 | 連線失敗後 retry + 斷線偵測重連 | ⭐⭐ | networking/mqtt_publish.py |
| NTP 時間同步 | ntptime.settime() + UTC+8 轉換 | ⭐⭐ | networking/wifi.py |
| MQTT 錯誤處理 | try/except 包覆 publish，失敗不中斷 | ⭐⭐ | networking/mqtt_publish.py |
| LED 狀態指示 | 用 LED 閃爍模式表示運行/錯誤狀態 | ⭐ | networking/mqtt_publish.py |
| I2C LCD 時鐘顯示 | PCF8574 I2C 介面，每秒更新時間 | ⭐ | interface/i2c_lcd.py |

---

## 統計

- 核心技術：7 種
- 感測器輸入：14 種
- 無線通訊：14 種
- 輸出控制：7 種
- 人機介面：10 種
- 時間/計時：3 種
- 基礎語法：6 種
- MicroPython 實作範例：7 種
- **合計：68 種功能**
