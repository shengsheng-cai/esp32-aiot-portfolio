# ESP32 / AIoT Projects

ESP32 / MicroPython 嵌入式與 AIoT 實作專案。

> **Validation note**：進階整合腳本（`advanced/`）已實機驗證；其餘範例為課程學習整理，邏輯與結構已核對，未全數實機驗證。

---

| 專案 | 說明 | 驗證狀態 |
|------|------|----------|
| [esp32-module-lib](esp32-module-lib/) | 37 種 ESP32 MicroPython 模組範例：感測器 · 通訊 · 控制 · 介面 · 進階整合；`keypad_dht11`（Keypad + DHT11 + Web）、`motor_console`（Relay + Servo + LED + Stepper）、`night_light`（光敏 + PIR + 雙核心 + deep sleep）已實機驗證 | ✅ 部分實機驗證 |
| [esp32-sensor-lab](esp32-sensor-lab/) | ESP32 感測器節點：DHT11 → I2C LCD → MQTT 資料流，含 Flask + MongoDB 即時溫度儀表板（模板檔需自行補齊） | 程式層級 |
| [esp32-vision-mqtt](esp32-vision-mqtt/) | PC OpenCV 影像辨識 → MQTT/Serial → ESP32 伺服馬達追蹤 | 程式層級 |
