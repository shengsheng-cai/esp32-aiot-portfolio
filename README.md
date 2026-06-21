# ESP32 / AIoT Learning Portfolio

泰山職訓局 2025~2026 課程的重寫實作集，涵蓋 ESP32 / MicroPython 嵌入式、AIoT 通訊、AI/ML 應用與 CV。`ai-ml/ai-agent-lab`（RAG · MCP · ReAct Agent）為最貼近 AI 應用工作的子專案；`practice/iot/` 的 ESP32 實作為嵌入式學習紀錄。

各子專案為職訓期間學習實作整理，程式邏輯已核對；`esp32-module-lib/advanced/` 的 `keypad_dht11.py`（Keypad + DHT11 + Web）與 `motor_console.py`（Relay + Servo + LED + Stepper）已在 ESP32-D0WD-V3 rev3.1 實機驗證通過，其餘 IoT 韌體驗證狀態詳見各自 README。

---

## 技術範圍

| 領域 | 主要技術 |
|------|---------|
| **嵌入式 · IoT**（主軸） | ESP32 · MicroPython · GPIO/PWM/ADC · I2C/SPI/UART · MQTT · BLE · OTA |
| AI 應用 | PyTorch · CNN/ViT · OpenCV · RAG · MCP · Agent |
| 後端 | FastAPI · SQLite · Selenium |

---

## 主要作品 · ESP32 / AIoT

| 專案 | 說明 | 技術 |
|------|------|------|
| [esp32-module-lib](practice/iot/esp32-module-lib/) | 39 種 ESP32 MicroPython 模組範例：感測器 · 通訊 · 控制 · 介面 · 進階整合，含難度分級；`keypad_dht11`、`motor_console`、`night_light` 已實機驗證 ✅ | MicroPython · MQTT · BLE · OTA · I2C · SPI |
| [esp32-sensor-lab](practice/iot/esp32-sensor-lab/) | ESP32 感測器節點：DHT11 → I2C LCD → MQTT 資料流，含 Flask + MongoDB 即時溫度儀表板（dashboard 模板需補齊） | MicroPython · MQTT · Flask · MongoDB |
| [esp32-vision-mqtt](practice/iot/esp32-vision-mqtt/) | PC OpenCV 影像辨識 → MQTT/Serial → ESP32 伺服馬達追蹤 | OpenCV · MobileNetSSD · paho-mqtt |

---

## Additional Practice · AI / CV / Backend

| 專案 | 說明 | 技術 |
|------|------|------|
| [mnist-dl](practice/ai-ml/mnist-dl/) | 手寫數字辨識 WebUI，最多 7 個模型同步推論 + Docker 部署 | FastAPI · PyTorch · React · Docker |
| [ai-agent-lab](practice/ai-ml/ai-agent-lab/) | RAG · MCP · ReAct Agent · Vision，7 個漸進式模組 | Gemini API · FAISS · Chroma · FastMCP |
| [cv-lab](practice/ai-ml/cv-lab/) | Transfer Learning · VAE · Style Transfer · Cartoonize | PyTorch · ResNet50 · VGG19 |
| [img-process-lab](practice/cv/img-process-lab/) | OpenCV 傳統影像處理：濾波 · 直方圖 · 人臉 · QR | OpenCV · Python |
| [taiwan-reservoir](practice/web/taiwan-reservoir/) | 台灣水庫水情爬取 API：Selenium → SQLite → FastAPI | FastAPI · Selenium · SQLite |
