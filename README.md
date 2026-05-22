# Embedded / AIoT Learning Portfolio

泰山職訓局 2025~2026 課程的重寫實作集，聚焦 ESP32 / MicroPython 嵌入式與 AIoT 應用。結合 9 年可靠度工程背景（硬體除錯 · 環境測試 · 法規標準），切入「硬體出身 × 嵌入式 / AIoT」。

> **Validation note**：部分 ESP32 範例為程式層級練習與架構整理，尚未全數完成實機接線驗證；各子專案 README 標明驗證狀態。

---

## 技術範圍

| 領域 | 主要技術 |
|------|---------|
| **嵌入式 · IoT**（主軸） | ESP32 · MicroPython · GPIO/PWM/ADC · I2C/SPI/UART · MQTT · BLE · OTA |
| AI 應用 | PyTorch · CNN/ViT · OpenCV · RAG · MCP · Agent |
| 後端 | FastAPI · SQLite · Selenium |

---

## 主要作品 · Embedded / AIoT

| 專案 | 說明 | 技術 |
|------|------|------|
| [esp32-module-lib](practice/iot/esp32-module-lib/) | 68 種 ESP32 MicroPython 模組範例：感測器 · 通訊 · 控制 · 介面 · 進階整合，含難度分級 | MicroPython · MQTT · BLE · OTA · I2C · SPI |
| [esp32-sensor-lab](practice/iot/esp32-sensor-lab/) | ESP32 感測器節點：DHT11 → I2C LCD → MQTT 資料流，含 Flask + MongoDB 即時溫度儀表板 | MicroPython · MQTT · Flask · MongoDB |
| [esp32-vision-mqtt](practice/iot/esp32-vision-mqtt/) | PC OpenCV 影像辨識 → MQTT/Serial → ESP32 伺服馬達追蹤 | OpenCV · MobileNetSSD · paho-mqtt |

> IoT 專案總入口：[practice/iot/](practice/iot/)

---

## Additional Practice · AI / CV / Backend

| 專案 | 說明 | 技術 |
|------|------|------|
| [mnist-dl](practice/ai-ml/mnist-dl/) | 手寫數字辨識 WebUI，最多 7 個模型同步推論 + Docker 部署 | FastAPI · PyTorch · React · Docker |
| [ai-agent-lab](practice/ai-ml/ai-agent-lab/) | RAG · MCP · ReAct Agent · Vision，7 個漸進式模組 | Gemini API · FAISS · Chroma · FastMCP |
| [cv-lab](practice/ai-ml/cv-lab/) | Transfer Learning · VAE · Style Transfer · Cartoonize | PyTorch · ResNet50 · VGG19 |
| [img-process-lab](practice/cv/img-process-lab/) | OpenCV 傳統影像處理：濾波 · 直方圖 · 人臉 · QR | OpenCV · Python |
| [taiwan-reservoir](practice/web/taiwan-reservoir/) | 台灣水庫水情爬取 API：Selenium → SQLite → FastAPI | FastAPI · Selenium · SQLite |
