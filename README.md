# Vocational Training Notes

泰山職訓局 2025~2026 課程學習紀錄。

---

## 職訓涵蓋範圍

| 領域 | 主要技術 |
|------|---------|
| **AI 應用** | PyTorch · CNN/RNN/VAE · ViT · OpenCV · RAG · MCP · AI Agent |
| **嵌入式 · IoT** | ESP32 · MicroPython · I2C/PWM/DHT · MQTT · OpenCV · MongoDB |

---

## 技術方向

**主要方向 · 軟體工程（Python / FastAPI / React）**
職訓打下 Python 基礎，以此延伸至 FastAPI + React 技術棧，目標全端軟體工程職位。

**延伸方向 · AIoT（ESP32 + AI + 感測器）**
結合 9 年可靠度工程背景（硬體除錯 · 環境測試 · 法規標準），
以 ESP32 + MicroPython 為硬體核心，整合職訓的 AI 應用（PyTorch · RAG · MCP）與 MQTT 通訊，
切入市面少見的「硬體出身 × AI 應用」定位。

---

## 練習成果

課程內容重寫為可執行學習專案，各採適合技術棧。

**AI / ML**

| 子專案 | 說明 | 技術 |
|--------|------|------|
| [mnist-dl](practice/ai-ml/mnist-dl/) | 手寫數字辨識 WebUI，最多 7 個深度學習模型同步推論，支援 Docker 部署 | FastAPI · PyTorch · React · Docker |
| [ai-agent-lab](practice/ai-ml/ai-agent-lab/) | RAG · MCP · ReAct Agent · Vision 完整學習路徑，7 個漸進式模組，全走 Gemini API | Gemini API · FAISS · Chroma · FastMCP |
| [cv-lab](practice/ai-ml/cv-lab/) | Transfer Learning · VAE · Style Transfer · Deep Dream · Cartoonize 學習實驗室，支援 MPS | PyTorch · ResNet50 · EfficientNet · VGG19 · InceptionV3 · AnimeGANv2 |

**Computer Vision**

| 子專案 | 說明 | 技術 |
|--------|------|------|
| [img-process-lab](practice/cv/img-process-lab/) | OpenCV 傳統影像處理學習實驗室：濾波 · 直方圖 · 人臉偵測 · QR · 攝影機 | OpenCV · Python |

**Embedded · IoT**

| 子專案 | 說明 | 技術 |
|--------|------|------|
| [esp32-sensor-lab](practice/iot/esp32-sensor-lab/) | ESP32 MicroPython 感測器模組庫：DHT11 · I2C LCD · SG90 舵機 · 繼電器 · 蜂鳴器，搭配 MQTT pipeline 與即時溫度儀表板 | MicroPython · MQTT · Flask · MongoDB |
| [esp32-vision-mqtt](practice/iot/esp32-vision-mqtt/) | PC 端 OpenCV 即時影像辨識 + ESP32 伺服馬達追蹤：Haar/SSD/MobileNetSSD 人臉與物件追蹤、face_recognition 陌生人偵測、MQTT/Serial 雙傳輸層 | OpenCV · MobileNetSSD · face_recognition · paho-mqtt |
| [esp32-module-lib](practice/iot/esp32-module-lib/) | 職訓課程期間完整實作的 68 種 ESP32 MicroPython 模組範例：感測器 · 通訊 · 控制 · 介面 · 進階整合，含難度分級 | MicroPython · MQTT · BLE · OTA · I2C · SPI |

**Backend**

| 子專案 | 說明 | 技術 |
|--------|------|------|
| [taiwan-reservoir](practice/web/taiwan-reservoir/) | 台灣水庫即時水情爬取 API，Selenium 爬取 → SQLite 存庫 → FastAPI 查詢 | FastAPI · Selenium · SQLite |
