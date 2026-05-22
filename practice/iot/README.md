# Embedded / AIoT Projects

ESP32 / MicroPython 嵌入式與 AIoT 實作專案。

> **Validation note**：部分範例為程式層級練習，尚未全數實機驗證；各專案 README 標明驗證狀態。

---

| 專案 | 說明 | 技術 |
|------|------|------|
| [esp32-module-lib](esp32-module-lib/) | 68 種 ESP32 MicroPython 模組範例：感測器 · 通訊 · 控制 · 介面 · 進階整合，含難度分級 | MicroPython · MQTT · BLE · OTA · I2C · SPI |
| [esp32-sensor-lab](esp32-sensor-lab/) | ESP32 感測器節點：DHT11 → I2C LCD → MQTT 資料流，含 Flask + MongoDB 即時溫度儀表板 | MicroPython · MQTT · Flask · MongoDB |
| [esp32-vision-mqtt](esp32-vision-mqtt/) | PC OpenCV 影像辨識 → MQTT/Serial → ESP32 伺服馬達追蹤 | OpenCV · MobileNetSSD · paho-mqtt |
