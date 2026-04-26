# ESP32 MicroPython 模組化感測器範例

ESP32 MicroPython 常用功能的範例程式碼，以及硬體接線參考圖。

> **注意**：本庫為課程學習記錄，程式碼未全數在硬體上驗證，使用前請依實際板子與 MicroPython 版本測試調整。

---

## 硬體參考圖 (`hardware/`)

開始之前先確認你用的是哪一塊板子，腳位定義會不一樣。

| 檔案 | 說明 |
|------|------|
| `ESP32-30pin-GPIO-mapping.png` | 30 腳位版 GPIO 對應表（最常見款） |
| `ESP32-DEV-KIT-DevKitC-v4-pinout-(nodemcu_32s).png` | DevKitC v4 / NodeMCU-32S 腳位圖 |
| `ESP32_DOIT_KIT_Pinout.jpg` | DOIT 開發板腳位圖 |
| `ESP32-WeMos-LOLIN-D32-pinout-mischianti.jpg` | Wemos LOLIN D32 腳位圖 |
| `ESP32-WeMos-LOLIN-D32-4mb-flash-schematic.jpg` | LOLIN D32 電路圖 |
| `ESP32-CAM-pinout-mischianti-1536x727.jpg` | ESP32-CAM 腳位圖 |
| `ESP32-I2C-hardware-wiring.png` | I2C 接線方式（SDA/SCL） |

---

## 韌體範例 (`firmware/`)

所有範例都是 MicroPython，直接燒錄到 ESP32 執行。

### 環境需求

- MicroPython firmware 已燒錄至 ESP32
- 建議工具：[Thonny IDE](https://thonny.org)（免費，適合初學）


### 目錄結構

```
firmware/
  core-skills/    核心技術（中斷、睡眠、PWM、ADC、Flash 儲存、雙核心）
  sensors/        感測器（溫濕度、氣體、加速度、心率、秤重等）
  control/        輸出控制（繼電器、馬達、WS2812B 燈帶、MAX7219）
  interface/      人機介面（OLED、TFT、LCD、Keypad、旋轉編碼器等）
  networking/     無線通訊（WiFi、Web Server、MQTT、WebSocket、BLE、OTA）
  time/           即時時鐘（DS1302、DS3231）
  advanced/       整合範例（DHT11 Web Server、Keypad 門禁系統）
  lib/            依賴庫（LCD 驅動、ST7735 TFT 驅動）
```

---

### 核心技術 (`core-skills/`)

| 檔案 | 功能 | 難度 |
|------|------|------|
| `basics.py` | GPIO 基礎、LED、按鈕 | ⭐ |
| `adc.py` | ADC 類比輸入讀取 | ⭐ |
| `flash_storage.py` | Flash 掉電儲存設定值 | ⭐ |
| `interrupt.py` | GPIO 硬體中斷 | ⭐⭐ |
| `sleep_wdt.py` | 深度睡眠 + 看門狗計時器 | ⭐⭐ |
| `dual_core.py` | 雙核心分工（Core0 / Core1） | ⭐⭐⭐ |

---

### 感測器 (`sensors/`)

| 檔案 | 感測器 | 難度 |
|------|--------|------|
| `dht.py` | DHT11 溫濕度 | ⭐ |
| `analog_sensors.py` | 聲音 / 水位 / 雨水 / 火焰 / 光敏 | ⭐ |
| `pir_hall.py` | PIR 人體偵測 + 霍爾磁場感應 | ⭐ |
| `mq2.py` | MQ-2 煙霧 / 瓦斯偵測 | ⭐⭐ |
| `adxl335.py` | ADXL335 三軸加速度 | ⭐⭐ |
| `max471_hx711.py` | MAX471 電壓電流 + HX711 秤重 | ⭐⭐ |
| `max30100.py` | MAX30100 心率血氧 | ⭐⭐⭐ |

---

### 輸出控制 (`control/`)

| 檔案 | 功能 | 難度 |
|------|------|------|
| `pwm.py` | PWM 輸出（亮度 / 蜂鳴器） | ⭐ |
| `relay.py` | 繼電器控制（序列埠指令） | ⭐ |
| `servo.py` | 伺服馬達 0~180° | ⭐ |
| `dc_motor.py` | 直流馬達正反轉（L298N） | ⭐⭐ |
| `stepper.py` | 步進馬達精確控制 | ⭐⭐ |
| `ws2812b.py` | WS2812B 全彩 RGB 燈帶 | ⭐⭐ |
| `matrix_led_max7219.py` | 8x8 矩陣 LED（MAX7219） | ⭐⭐ |

---

### 人機介面 (`interface/`)

| 檔案 | 模組 | 難度 |
|------|------|------|
| `touch_sensor.py` | 電容式觸控 | ⭐ |
| `vibration.py` | 震動開關 | ⭐ |
| `dip_switch.py` | DIP 撥碼開關 | ⭐ |
| `i2c_lcd.py` | I2C LCD 16x2 | ⭐ |
| `seven_segment.py` | 七段顯示器 TM1637 | ⭐ |
| `keypad.py` | 4x4 矩陣鍵盤 | ⭐ |
| `ir_remote.py` | 紅外線遙控接收 | ⭐⭐ |
| `rotary_encoder.py` | 旋轉編碼器 | ⭐⭐ |
| `oled_ssd1306.py` | OLED SSD1306 128x64（I2C） | ⭐⭐ |
| `tft_st7735.py` | TFT 彩色螢幕 ST7735（SPI） | ⭐⭐ |

> `i2c_lcd.py` 需要 `lib/lcd_api.py` 和 `lib/machine_i2c_lcd.py`  
> `tft_st7735.py` 需要 `lib/st7735/` 目錄

---

### 無線通訊 (`networking/`)

| 檔案 | 功能 | 難度 |
|------|------|------|
| `wifi.py` | WiFi 連線 + 靜態 IP + NTP 對時 | ⭐ |
| `web_server.py` | HTTP Web Server（LED 控制、URL 參數） | ⭐⭐ |
| `async_web_server.py` | 非同步 Web Server（microdot）+ 靜態文件 | ⭐⭐ |
| `websocket.py` | WebSocket 雙向即時通訊 | ⭐⭐⭐ |
| `mqtt_publish.py` | MQTT 發布感測資料 + 自動重連 | ⭐⭐ |
| `mqtt_control.py` | MQTT 訂閱指令控制硬體 | ⭐⭐⭐ |
| `esp_now.py` | ESP-NOW 點對點無線通訊 | ⭐⭐⭐ |
| `bluetooth.py` | BLE + 傳統藍牙 SPP | ⭐⭐⭐ |
| `esp01.py` | ESP-01 AT 指令控制 | ⭐⭐ |
| `nrf24l01.py` | nRF24L01 2.4GHz 無線收發 | ⭐⭐ |
| `ota.py` | OTA 無線燒錄（WebREPL / HTTP 上傳） | ⭐⭐⭐ |

> `async_web_server.py` 需要另外安裝 microdot：  
> `mpremote mip install github:miguelgrinberg/microdot/src/microdot.py`

---

### 即時時鐘 (`time/`)

| 檔案 | 模組 | 難度 |
|------|------|------|
| `ds1302.py` | DS1302 RTC（精度較低） | ⭐ |
| `ds3231.py` | DS3231 RTC（溫度補償，更準確） | ⭐ |

---

### 整合範例 (`advanced/`)

| 檔案 | 功能 | 難度 |
|------|------|------|
| `dht11_web_server.py` | DHT11 + Web Server，網頁顯示溫濕度 | ⭐⭐ |
| `keypad_lcd_locker.py` | Keypad + LCD 門禁管制機 | ⭐⭐ |

---

## 依賴庫 (`lib/`)

不需要修改，直接上傳到 ESP32 的 `/lib/` 目錄即可。

| 路徑 | 說明 | 被誰使用 |
|------|------|----------|
| `lib/lcd_api.py` | I2C LCD 底層 API | `interface/i2c_lcd.py` |
| `lib/machine_i2c_lcd.py` | I2C LCD MicroPython 驅動 | `interface/i2c_lcd.py` |
| `lib/st7735/ST7735.py` | ST7735 TFT 驅動 | `interface/tft_st7735.py` |
| `lib/st7735/sysfont.py` | 系統字型 | `interface/tft_st7735.py` |
| `lib/st7735/seriffont.py` | Serif 字型 | `interface/tft_st7735.py` |
| `lib/st7735/terminalfont.py` | 終端機字型 | `interface/tft_st7735.py` |

---

## 難度說明

| 符號 | 程度 |
|------|------|
| ⭐ | 入門：照程式碼改 PIN 腳就能用 |
| ⭐⭐ | 中等：需要理解參數意義或搭配其他模組 |
| ⭐⭐⭐ | 進階：需要額外設定或對通訊協定有基本了解 |

---

