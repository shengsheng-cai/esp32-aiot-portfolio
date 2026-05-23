# CV Lab

職訓課程重寫 — Transfer Learning · VAE · Style Transfer · Cartoonize 學習實驗室。

技術棧：Python · PyTorch · torchvision · AnimeGANv2

---

## 學習路徑

```
transfer → vae → style → cartoonize
遷移學習    生成模型   風格轉換    GAN 推理
```

---

## 模組清單

| 資料夾 | 主題 | 核心技術 |
|--------|------|---------|
| [transfer/](transfer/) | 遷移學習：ImageNet 預訓練模型分類 CIFAR-10 | ResNet50 · EfficientNet · Feature Extraction · Fine-tuning |
| [vae/](vae/) | 變分自編碼器：生成 + 去噪 | VAE · Denoising AE · 潛在空間視覺化 |
| [style/](style/) | 神經風格轉換 + Deep Dream | VGG19 · Gram Matrix · InceptionV3 · LBFGS |
| [cartoonize/](cartoonize/) | 卡通化推理：動漫風格生成 | AnimeGANv2 · paprika · face_paint_v2 · celeba_distill |

---

## 環境

```bash
pip install -r requirements.txt
```

> cartoonize 使用 `torch.hub` 自動下載 AnimeGANv2 權重，首次執行需要網路，之後 cache 在 `~/.cache/torch/hub/`。

---

## 前置條件（Prerequisites）

- Python + `requirements.txt`（torch / torchvision / Pillow / matplotlib / numpy / tqdm）。AnimeGANv2 不在 requirements，靠 `torch.hub` 動態載入，不需另外 `pip install`。
- **資料集自動下載**：`transfer`（CIFAR-10，約 170MB）、`vae`（MNIST，約 11MB）首次執行會自動下載，需要網路。
- **模型權重 / 預訓練網路需網路**：
  - transfer 用 torchvision 的 ImageNet 預訓練 ResNet50 / EfficientNet（首次自動下載）。
  - style 用 VGG19、dream 用 InceptionV3（torchvision 預訓練，首次自動下載）。
  - cartoonize 用 `torch.hub` 從 `bryandlee/animegan2-pytorch` 下載 AnimeGANv2 generator 權重（paprika / face_paint_512_v2 / celeba_distill），首次自動下載並 cache 於 `~/.cache/torch/hub/`。
- **訓練 / 推論產物不在 git 內**：`*.pth`（`resnet50_cifar10.pth`、`vae.pth`、`denoise_ae.pth` 等）與結果 `*.png` 都未納入 git，clone 後不存在，需自行執行對應 `make` target 產生。
- **裝置限制**：
  - transfer / vae / cartoonize 自動選 `cuda > mps > cpu`，可在 Apple Silicon 用 MPS 加速。
  - **style transfer 例外**：LBFGS 不支援 MPS，MPS 上會跑出錯誤結果，務必加 `--device cpu`（`make smoke` 已內建此 flag）。
  - 純 CPU 可跑但慢（見「指令總覽」時間欄）。

## 驗證狀態（Validation Status）

- **程式層級**：Makefile target、各腳本的參數（`--model` / `--mode` / `--device` / `--styles` 等）、device 邏輯、cartoonize 的 `torch.hub` 載入方式與本 README 對照一致。
- **cartoonize 的 AnimeGANv2 API 描述屬實**：對照 `cartoonize/cartoonize.py`，確實使用 `torch.hub.load("bryandlee/animegan2-pytorch:main", "generator", pretrained=<key>, trust_repo=True)`，三種風格對應的權重 key 為 `paprika` / `face_paint_512_v2` / `celeba_distill`，與 README 風格表一致；README 的「torch.hub 自動下載、不需額外裝 TF」描述正確，未發現呼叫不存在的 API。
- **本機實跑（部分）**：擁有者本機已存在 `resnet50_cifar10.pth`、`vae.pth`、`denoise_ae.pth` 及 `result_style.png` / `result_dream.png` / `denoise_result.png` / `latent_space.png` / `label_clusters.png`，顯示 transfer / vae / style / dream 模組在擁有者環境實際產出過；但這些檔不入 git。
- **未由本品檢流程實跑**：本次未安裝套件、未下載任何權重、未實際執行（含 cartoonize 的 torch.hub 下載）。cartoonize 端到端推論結果以擁有者環境為準。

---

## 快速驗證

重頭開始（全新環境）：

```bash
make dev   # 安裝套件 + 跑所有模組，MPS ~10 分鐘 / CPU ~30 分鐘
```

只跑驗證（套件已裝）：

```bash
make smoke   # transfer-quick + vae-denoise + dream + style（style 強制 CPU，見下）
```

或只跑單一模組：

```bash
make transfer-quick   # MPS ~3 分鐘 / CPU ~10 分鐘，val_acc 應該 ~80%
make vae-denoise      # MPS ~3 分鐘 / CPU ~10 分鐘，產出 denoise_result.png
```

---

## 指令總覽

| 指令 | 需求 | 時間（CPU） | 產出 |
|------|------|-------------|------|
| `make transfer` | 自動下載 CIFAR-10 | ~2 小時 | `resnet50_cifar10.pth` |
| `make transfer-efficientnet` | 同上 | ~1.5 小時 | `efficientnet_cifar10.pth` |
| `make transfer-quick` | 同上（只用 5000 張） | ~10 分鐘 | `resnet50_cifar10.pth` |
| `make vae` | 自動下載 MNIST | ~10 分鐘 | `vae.pth`, `latent_space.png`, `label_clusters.png` |
| `make vae-denoise` | 同上 | ~10 分鐘 | `denoise_ae.pth`, `denoise_result.png` |
| `make style CONTENT=<圖> STYLE_IMG=<圖>` | 自備 2 張圖 | 幾分鐘 | `result_style.png` |
| `make dream IMG=<圖>` | 自備 1 張圖 | 幾分鐘 | `result_dream.png` |
| `make cartoonize` | `cartoonize/input_images/`，首次自動下載權重 | 幾分鐘 | `cartoonize/output_images/paprika/*` |
| `make cartoonize-all` | 同上，跑全部 3 種風格 | 幾分鐘 | `cartoonize/output_images/<style>/*` |
| `make cartoonize-style STYLE=face_paint_v2` | 同上，指定風格（paprika / face_paint_v2 / celeba_distill） | 幾分鐘 | 單一風格輸出 |

輸出檔除了 cartoonize 以外都落在執行 `make` 的當前目錄（repo 根目錄）。

---

## 模組說明

### transfer — 遷移學習

兩階段訓練流程：

```
Phase 1: Feature Extraction  凍結 backbone，只訓練分類頭（快速收斂）
Phase 2: Fine-tuning         解凍全部層，低學習率繼續訓練（提升精度）
```

支援 `--model resnet50 / efficientnet`，訓練完自動儲存 `.pth` 權重。

CPU 訓練很慢，建議先跑 `make transfer-quick`（subset + 少 epoch）確認能動，再考慮跑全量。訓練過程會顯示 tqdm 進度條，沒動才是有問題。

---

### vae — 變分自編碼器

```
VAE 模式：
  Encoder（Conv）→ z_mean, z_log_var → reparameterize → Decoder（ConvTranspose）
  Loss = reconstruction loss（BCE）+ KL divergence
  輸出：latent_space.png（2D 流形格子圖）+ label_clusters.png（數字分布圖）

Denoise 模式：
  輸入加噪圖 → AutoEncoder → 還原原圖
  輸出：denoise_result.png（原圖 / 加噪 / 還原 三排對比）
```

---

### style — 風格轉換 + Deep Dream

需要自備圖片（不在 repo 裡）。

```bash
# 神經風格轉換：把 style 圖片的畫風套到 content 圖片
make style CONTENT=photo.jpg STYLE_IMG=painting.jpg

# Deep Dream：強化圖片中神經網路「看到」的特徵
make dream IMG=photo.jpg
```

風格轉換使用 VGG19，以 Gram Matrix 計算風格損失，PyTorch LBFGS 優化。
Deep Dream 使用 InceptionV3，多尺度 octave 梯度上升。

> ⚠️ **LBFGS 不支援 MPS**：style 模式在 MPS 上會跑出錯誤結果，務必加 `--device cpu`。
> `make smoke` 已內建此 flag；直接呼叫時記得手動加。

---

### cartoonize — 卡通化

將照片轉換為動漫風格，使用 AnimeGANv2（PyTorch），首次執行透過 `torch.hub` 自動下載權重。

| 風格 | 說明 |
|------|------|
| `paprika` | 今敏風格（顆粒感，飽和） |
| `face_paint_v2` | 動漫臉部繪畫風格 |
| `celeba_distill` | 輕量蒸餾模型，速度最快 |

輸入圖片放到 `cartoonize/input_images/`，結果存至 `cartoonize/output_images/<style>/`，自動產生原圖與卡通化對比圖。

---

## 技術選型

| 元件 | 本專案 | 原課程 | 換掉的原因 |
|------|--------|--------|-----------|
| 框架 | PyTorch | TensorFlow/Keras | 與 mnist-dl 一致，現代主流 |
| Transfer Learning | ResNet50 + EfficientNet | ResNet50 + Xception | EfficientNet 更輕量現代 |
| VAE | PyTorch 自實作 | Keras 官方範例 | 框架統一 |
| Style Transfer | torch.optim.LBFGS | scipy fmin_l_bfgs_b | 不需 TF1 相容層 |
| Deep Dream | InceptionV3 梯度上升 | 同，TF1 風格 | 移除 disable_eager_execution |
| Cartoonize | AnimeGANv2（PyTorch，torch.hub 自動下載） | CartoonGAN（TF-based） | 統一 PyTorch，不需額外裝 TF |

---

## 授權

模型權重採用各原始專案授權（AnimeGANv2、torchvision pretrained models）。
