# MNIST Multi-Model Inference WebUI

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.11-EE4C2C?logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)

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
| ViT_HF_BestTuned | google/vit-base-patch16-224 fine-tuned + augmentation | — | 自訓 × HF（`make train-hf`，可選） |

### 技術堆棧

| 層級 | 技術 |
|------|------|
| 後端 | FastAPI · PyTorch · OpenCV · Transformers |
| 前端 | React 19 · Vite · Canvas API |
| 訓練 | PyTorch · MNIST（公開資料集）· MPS / CUDA |

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

## 快速啟動

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

---

## 目錄結構

```
mnist-dl/
├── backend/
│   ├── app.py            # FastAPI 路由與模型載入
│   ├── models.py         # SimpleNN / SimpleCNN / ViT_MNIST class
│   ├── preprocessing.py  # OpenCV 前處理（手寫字置中）
│   └── requirements.txt
├── client/               # React（Vite）
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── DrawingCanvas.jsx
│           └── ResultsPanel.jsx
├── training/
│   ├── train_simple.py   # SimpleNN + SimpleCNN
│   ├── train_vit_custom.py
│   └── train_vit_hf.py
├── models/               # .pth 檔（gitignored）
├── .venv/                # Python 環境（gitignored）
└── Makefile
```