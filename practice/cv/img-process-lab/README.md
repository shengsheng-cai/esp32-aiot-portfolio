# img-process-lab

OpenCV 傳統影像處理學習實驗室。從原始課程檔案重寫為可獨立執行的 CLI 模組，純 OpenCV + Python，無 PyTorch 依賴。

---

## 安裝

```bash
pip install -r requirements.txt
# 選用：pip install tensorflow   # teachable.py
# 選用：pip install pyserial     # gesture.py --serial
```

---

## 模組說明

### basics/

| 檔案 | 功能 | 範例指令 |
|------|------|---------|
| `basics.py` | Resize · Rotate · Canny · Contour | `python basics/basics.py --source sample/lena.jpg --mode all` |
| `threshold.py` | THRESH_BINARY / BINARY_INV，多閾值對比 | `python basics/threshold.py --source sample/lena.jpg --mode all --gray` |
| `interpolation.py` | 5 種插值方法放大 / 縮小對比 | `python basics/interpolation.py --source sample/lena.jpg --mode all` |
| `histogram.py` | 直方圖均衡化 · 正規化 · 彩色均衡化 · matplotlib 繪圖 | `python basics/histogram.py --source sample/dim.jpg --mode all` |

### filter/

| 檔案 | 功能 | 範例指令 |
|------|------|---------|
| `filter.py` | 模糊（blur/Gaussian/median/box/bilateral）· filter2D kernel · Sobel · Canny | `python filter/filter.py --source sample/lena.jpg --mode blur` |

### color/

| 檔案 | 功能 | 範例指令 |
|------|------|---------|
| `in_range.py` | HSV 色彩遮罩 · 背景替換 · 隱形斗篷（攝影機） | `python color/in_range.py --source sample/T04-A.jpg --mode mask` |
| `tracking.py` | HSV 顏色物件追蹤（拖尾軌跡） | `python color/tracking.py --color green` |

### detection/

| 檔案 | 功能 | 範例指令 |
|------|------|---------|
| `face_detect.py` | DNN 人臉偵測（SSD ResNet-10），支援圖片 / 影片 / 攝影機 | `python detection/face_detect.py --source sample/jp.png` |
| `landmarks.py` | MediaPipe 臉部特徵點（478 點）· 眨眼計數（EAR） | `python detection/landmarks.py --source 0 --mode blinks` |
| `gesture.py` | MediaPipe 手勢辨識（剪刀石頭布），選用序列埠傳送 | `python detection/gesture.py` |
| `qr.py` | QR Code 解碼，支援圖片 / 攝影機 | `python detection/qr.py --source sample/qr.png` |
| `teachable.py` | Teachable Machine Keras 模型推論（需自備 .h5） | `python detection/teachable.py --model keras_Model.h5 --labels labels.txt` |

### application/

| 檔案 | 功能 | 範例指令 |
|------|------|---------|
| `cam.py` | 攝影機預覽 · 錄影 | `python application/cam.py --mode preview` |
| `scan.py` | 文件掃描透視校正（+ 自適應二值化） | `python application/scan.py --source <doc-photo.jpg> --mode scan` |
| `measure.py` | 以已知寬度參考物估算畫面物件尺寸（英吋） | `python application/measure.py --source <photo.jpg> --width 0.955` |
| `grader.py` | OMR 泡泡卷自動閱卷 | `python application/grader.py --source sample/test.png` |

### web/

| 檔案 | 功能 | 範例指令 |
|------|------|---------|
| `i.html` | 純前端 MediaPipe JS 手勢辨識（剪刀石頭布） | 瀏覽器直接開啟 |

---

## 常用指令

```bash
make install                              # 安裝依賴
make demo                                 # 靜態圖全跑（不需攝影機）

# 圖片模組（IMG 預設 sample/lena.jpg）
make basics                               # Resize · Rotate · Canny · Contour
make face IMG=sample/jp.png              # DNN 人臉偵測（靜態圖）
make face-cam                             # DNN 人臉偵測（攝影機）
make filter IMG=sample/lena.jpg          # 所有濾波模式
make filter-blur  IMG=sample/lena.jpg    # 模糊對比
make filter-sobel IMG=sample/gear.png    # Sobel 邊緣
make filter-canny IMG=sample/lena.jpg    # Canny 邊緣
make histogram IMG=sample/dim.jpg        # 直方圖均衡化 / 正規化
make in-range IMG=sample/T04-A.jpg       # HSV 色彩遮罩
make interpolation                        # 插值方法對比
make scan   IMG=<doc-photo.jpg>          # 透視校正（需自備文件照）
make measure IMG=<photo.jpg> WIDTH=0.955 # 物件測量（需自備照片）
make grader IMG=<omr-sheet.png>          # OMR 閱卷（需自備答卷）
make landmarks                            # 臉部特徵點（靜態圖）
make threshold                            # 閾值多對比

# 攝影機 / 即時
make cam          # 預覽
make cam-record   # 錄影（輸出 output.mp4）
make tracking     # HSV 顏色物件追蹤
make qr           # QR Code 解碼（靜態圖）
make qr-cam       # QR Code 解碼（攝影機）
make blinks       # 眨眼偵測（攝影機）
make cloak        # 隱形斗篷（攝影機）
make gesture      # 剪刀石頭布手勢辨識

# 需自備模型
make teachable MODEL=keras_Model.h5 LABELS=labels.txt
```

---

## 樣本圖片

`sample/` 內含課程原始圖片，可直接用於各模組測試。

| 圖片 | 適用模組 |
|------|---------|
| `lena.jpg`, `airPineapple.jpg`, `lily.jpg` | filter, basics, interpolation |
| `jp.png`, `iron_chic.jpg` | face_detect, landmarks |
| `tetris_blocks.png`, `rooster.jpg` | basics, contour |
| `dim.jpg`, `river.jpg` | histogram |
| `T04-A.jpg`, `daisy_in_blue_510x340.jpg`, `brook_1020x680.jpg` | in_range |
| `qr.png` | qr |
| `gear.png` | filter (sobel) |
| `lena_s.png` | 小尺寸 lena，快速測試用 |
| `night.jpg` | 低光源場景，histogram 測試用 |
| `periwinkle.jpg` | 藍紫色花朵，in_range 測試用 |
| `a.jpg`, `b.png`, `c.png` | 通用備用素材（scan / basics） |
| `bear.jpg`, `bug.jpg` | 通用備用素材 |

---

## 注意事項

- `face_detect.py` 首次執行自動下載 caffemodel（約 10MB），需網路連線
- `teachable.py` 需自備從 [Teachable Machine](https://teachablemachine.withgoogle.com/) 訓練匯出的 `keras_Model.h5`
- `gesture.py --serial` 需額外安裝 `pyserial`
