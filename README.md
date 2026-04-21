# Vocational Training Notes

泰山職訓局 2025~2026 課程學習紀錄。

---

## 職訓涵蓋範圍

| 領域 | 主要技術 |
|------|---------|
| **Web 全端** | HTML/CSS/JS · PHP/SQL · Vue · Node/Express · NodeRED |
| **AI 應用** | PyTorch · CNN/RNN/VAE · ViT · OpenCV · RAG · MCP · AI Agent |
| **嵌入式 · IoT** | Raspberry Pi · I2C/PWM/DHT · MQTT · Docker · MongoDB |

---

## 技術方向

**主要方向 · 軟體工程（Python / FastAPI / React）**
職訓打下 Python 與 Web 全端基礎（Vue / Node / Express），
以此延伸至 FastAPI + React 技術棧，目標全端軟體工程職位。

**延伸方向 · AIoT（ESP32 + AI + 感測器）**
結合 9 年可靠度工程背景（硬體除錯 · 環境測試 · 法規標準），
以 ESP32 + MicroPython 為硬體核心，整合職訓的 AI 應用（PyTorch · RAG · MCP）與 MQTT 通訊，
切入市面少見的「硬體出身 × AI 應用」定位。

---

## 練習成果

課程內容以 FastAPI + React 重寫，每個子專案包含可執行程式碼與學習說明。

| 子專案 | 說明 | 技術 |
|--------|------|------|
| [mnist-dl](practice/ai-ml/mnist-dl/) | 手寫數字辨識 WebUI，最多 7 個深度學習模型同步推論，支援 Docker 部署 | FastAPI · PyTorch · React · Docker |
| [taiwan-reservoir](practice/ai-ml/taiwan-reservoir/) | 台灣水庫即時水情爬取 API，Selenium 爬取 → SQLite 存庫 → FastAPI 查詢 | FastAPI · Selenium · SQLite |
| [ai-agent-lab](practice/ai-ml/ai-agent-lab/) | RAG · MCP · ReAct Agent · Vision 完整學習路徑，7 個漸進式模組，全走 Gemini API | Gemini API · FAISS · Chroma · FastMCP |
| [cv-lab](practice/ai-ml/cv-lab/) | Transfer Learning · VAE · Style Transfer · Deep Dream · Cartoonize 學習實驗室，支援 MPS | PyTorch · ResNet50 · EfficientNet · VGG19 · InceptionV3 · AnimeGANv2 |
