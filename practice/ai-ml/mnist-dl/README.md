# MNIST Multi-Model Inference WebUI

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.11-EE4C2C?logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

**Hand-drawn digit recognition with up to 7 deep learning models via FastAPI + React.**  
Draw a digit on the canvas — SimpleNN, SimpleCNN, custom ViT, and HuggingFace models inference simultaneously and rank results by confidence.

[中文說明如下](#專案說明)

在瀏覽器畫板手寫數字，由最多 7 個深度學習模型同步推論並依信心度排序。從泰山職訓局 AI/ML 課程改寫，以 FastAPI + React 重構原版 vanilla HTML，並修正原始碼中的 typo 與 Normalize 參數 bug。

---

## 專案說明

### 模型列表

| 模型 | 架構 | Val Acc | 來源 |
|------|------|---------|------|
| SimpleNN | Linear × 3 | 96.1% | 自訓（MNIST） |
| SimpleCNN | Conv2d × 2 + Linear × 2 | 99.0% | 自訓（MNIST） |
| ViT_Custom | Patch Embedding + Transformer × 6 | 98.2% | 自訓（MNIST） |
| ViT_ImageNet | google/vit-base-patch16-224 | — | HuggingFace（ImageNet pretrained，對照用） |
| ViT_3rd_MNIST | farleyknight-org-username/vit-base-mnist | ~99% | HuggingFace |
| ViT_HF_4060 | google/vit-base-patch16-224 fine-tuned 3 epochs | — | 自訓 × HF（`make train-hf`，可選） |
| ViT_HF_BestTuned | google/vit-base-patch16-224 fine-tuned + augmentation | 99.26% | 自訓 × HF（`make train-hf`，可選） |

### 技術堆棧

| 層級 | 技術 |
|------|------|
| 後端 | FastAPI · PyTorch · OpenCV · Transformers |
| 前端 | React 19 · Vite · Canvas API |
| 訓練 | PyTorch · MNIST（公開資料集）· MPS / CUDA |
| 部署 | Docker · Docker Compose · Nginx |

---

## 系統架構

```
瀏覽器 Canvas（手寫數字）
    │
    │ POST /predict（PNG blob）
    ▼
FastAPI  ─── preprocessing.py（OpenCV）
    │            GaussianBlur → Otsu → 置中 → 28×28
    │
    ├── SimpleNN        → probabilities[10]
    ├── SimpleCNN       → probabilities[10]
    ├── ViT_Custom      → probabilities[10]
    ├── ViT_ImageNet    → probabilities[10]
    ├── ViT_3rd_MNIST   → probabilities[10]
    ├── ViT_HF_4060     → probabilities[10]  # 可選
    └── ViT_HF_BestTuned → probabilities[10] # 可選
    │
    │ JSON { results, best_model, best_prediction }
    ▼
React 前端（信心度色條排序顯示）
```

---

## 前置條件（Prerequisites）

- Python 3.13、Node.js（前端 Vite）、（選用）Docker / Docker Compose。
- **模型權重不在 git 內**（`models/*.pth` 已被 `.gitignore` 排除）。clone 後 `models/` 是空的，**必須先自行訓練**至少 SimpleNN / SimpleCNN / ViT_Custom，後端才會載入對應模型（見下方「快速啟動 → 訓練模型」）。後端啟動時只載入 `models/` 裡實際存在的 `.pth`，缺檔的模型會自動跳過。
- `ViT_ImageNet` 與 `ViT_3rd_MNIST` 由 HuggingFace 線上抓取（`google/vit-base-patch16-224`、`farleyknight-org-username/vit-base-mnist`），**首次啟動需要網路**下載權重，之後 cache 在 `~/.cache/huggingface`。無網路時這兩個模型會載入失敗並跳過，其餘模型仍可運作。
- **推論裝置**：後端（`backend/app.py`）只判斷 CUDA，否則用 CPU（**不使用 MPS**）；Docker 版以 `CUDA_VISIBLE_DEVICES=""` 強制 CPU。訓練腳本則支援 MPS / CUDA / CPU。
- HuggingFace fine-tune 的兩個模型（`ViT_HF_4060`、`ViT_HF_BestTuned`）為選用，需 `make train-hf` 自行訓練後才會出現。

## 驗證狀態（Validation Status）

- **程式層級**：Makefile target、後端路由、模型載入邏輯與本 README 指令對照一致。
- **本機實跑**：擁有者本機 `models/` 內已存在 5 個自訓 `.pth`（SimpleNN / SimpleCNN / ViT_Custom / ViT_HF_4060 / ViT_HF_BestTuned），表 README 列出的模型確實訓練並載入過；但這些 `.pth` 不入 git，他人 clone 後需自行重訓。
- **未由本品檢流程實跑**：本次未實際安裝套件、未重新訓練、未啟動服務或 Docker，故端到端流程（含 HF 線上下載）以擁有者環境為準。

---

## 快速啟動

### 本地開發

```bash
# 1. 建立 Python 虛擬環境並安裝套件
python3 -m venv .venv
make install

# 2. 訓練模型（首次使用）
make train-simple   # SimpleNN + SimpleCNN（~5 分鐘）
make train-vit      # ViT_Custom（~20 分鐘）
make train-hf       # HF fine-tune × 2（選用，支援斷點續跑）

# 3. 啟動服務
make dev            # 後端 :8000 + 前端 :5173
```

| 服務 | URL |
|------|-----|
| 前端 | http://localhost:5173 |
| 後端 API | http://localhost:8000 |
| API 文件 | http://localhost:8000/docs |

### Docker

```bash
# 1. 訓練模型（首次使用，同上）

# 2. 打包並啟動
make docker-build
make docker-up
```

| 服務 | URL |
|------|-----|
| 前端 | http://localhost |
| API 文件 | http://localhost/docs |

---

## 目錄結構

```
mnist-dl/
├── backend/
│   ├── app.py            # FastAPI 路由與模型載入
│   ├── models.py         # SimpleNN / SimpleCNN / ViT_MNIST class
│   ├── preprocessing.py  # OpenCV 前處理（手寫字置中）
│   ├── requirements.txt
│   └── Dockerfile
├── client/               # React（Vite）
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── DrawingCanvas.jsx
│   │       └── ResultsPanel.jsx
│   ├── Dockerfile
│   └── nginx.conf
├── training/
│   ├── train_simple.py   # SimpleNN + SimpleCNN
│   ├── train_vit_custom.py
│   └── train_vit_hf.py
├── models/               # .pth 檔（gitignored）
├── .venv/                # Python 環境（gitignored）
├── docker-compose.yml
└── Makefile
```