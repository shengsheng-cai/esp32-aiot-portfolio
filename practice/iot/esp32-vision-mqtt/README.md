# esp32-vision-mqtt

ESP32 MicroPython + PC 端 OpenCV 即時影像辨識與 MQTT/Serial 控制學習實驗室。

課程來源（泰山職訓局 2025~2026）將 Raspberry Pi + Arduino I2C 架構移植至 ESP32 + UART，
PC 端保留 Python 3 / OpenCV，傳輸層可在 MQTT 與 Serial 間切換（改 import 即可）。

---

## 架構

```
PC（Python 3）                        ESP32（MicroPython）
┌─────────────────────┐  MQTT/Serial  ┌──────────────────────┐
│  search_*.py        │ ────────────> │  servo_uart.py       │
│  stranger*.py       │  角度/指令    │    SG90 伺服馬達      │
│  (OpenCV 偵測)      │ <──────────── │    HW-482 繼電器      │
│                     │               │    LCD 1602           │
│  http://localhost   │               └──────────────────────┘
│  :9090/a.mjpg       │
└─────────────────────┘
```

**傳輸層切換**：所有偵測腳本皆 `from mySerial import ...`，改成 `from myMQTT import ...` 即可切換為 MQTT 模式（API 完全相同）。

---

## 功能模組

### PC 端偵測腳本（擇一執行）

| 腳本 | 偵測方式 | 額外功能 |
|------|----------|----------|
| `search_face_hc_v4.py` | Haar Cascade 人臉 + 眼睛 | 縮圖加速，掃描補償 |
| `search_face_v.py` | ResNet-SSD 人臉 | 信心度過濾 |
| `search_object.py` | MobileNetSSD 任意物件（-o 1~20） | 指定類別追蹤 |
| `search_object_rec.py` | MobileNetSSD + 錄影 | 偵測到物件時錄 output.mp4 |
| `stranger.py` | MobileNetSSD 人物 + face_recognition | 辨識已知臉孔，陌生人錄影 |
| `stranger_lcd.py` | 同上 + LCD/Relay | 辨識結果顯示於 LCD，繼電器連動 |

所有腳本共用追蹤邏輯：偵測到目標 → 伺服馬達跟隨；無目標 → 左右掃描。

### PC 端工具

| 檔案 | 說明 |
|------|------|
| `mySerial.py` | UART 傳輸層（r_h/lcd_show/dev_On/dev_Off） |
| `myMQTT.py` | MQTT 傳輸層（API 與 mySerial 完全相同） |
| `myCam1.py` | 多執行緒攝影機讀取類別 |
| `mjpg_server.py` | MJPEG HTTP 串流伺服器（共用模組） |
| `vplay.py` | 影片/攝影機 MJPEG 播放，支援速度控制 |
| `config.json` | MQTT broker 與 topic 設定 |
| `test_get_conf.py` | 驗證 config.json 設定是否正確 |

### ESP32 端

| 檔案 | 說明 |
|------|------|
| `esp32/servo_uart.py` | UART 接收角度/LCD/Relay 指令，統一入口 |

（ESP32 端放在 `../esp32-sensor-lab/esp32/servo_uart.py`，含 SG90 + HW-482 + LCD 完整控制）

---

## 接線

```
ESP32 GPIO  9 → SG90 Signal（橘線）
ESP32 GPIO 17 → HW-482 Relay S
ESP32 GPIO  1 → UART TX（接 PC USB-Serial RX）
ESP32 GPIO  3 → UART RX（接 PC USB-Serial TX）

SG90  紅=5V  棕=GND  橘=GPIO 9
HW-482 += 5V  -= GND
LCD   SDA=GPIO 21  SCL=GPIO 22
```

---

## 快速開始

**1. 安裝依賴**

```bash
pip install opencv-python paho-mqtt pyserial face_recognition requests
```

**2. 設定 config.json（MQTT 模式）**

```bash
cp config.json.example config.json   # 或直接編輯 config.json
python test_get_conf.py              # 驗證設定
```

**3. 燒錄 ESP32**

將 `esp32-sensor-lab/esp32/servo_uart.py` 以 Thonny 或 mpremote 上傳至 ESP32：

```bash
mpremote connect /dev/ttyUSB0 cp ../esp32-sensor-lab/esp32/servo_uart.py :main.py
```

**4. 執行偵測腳本（Serial 模式，預設）**

```bash
cd host/
python search_object.py -o 15        # 追蹤人（class 15）
python search_face_hc_v4.py          # Haar Cascade 人臉追蹤
python stranger_lcd.py               # 陌生人偵測 + LCD + 繼電器
```

瀏覽器開啟 `http://localhost:9090/a.mjpg` 即時觀看串流。

**5. 切換為 MQTT 模式**

將偵測腳本第一行的 import 改為：

```python
from myMQTT import mm_close, r_h, lcd_show, dev_On, dev_Off
```

確認 config.json 的 MQTT broker 設定後重新執行。

---

## 模型檔下載

| 模型 | 用途 | 下載 |
|------|------|------|
| `MobileNetSSD_deploy.caffemodel` | 物件偵測（search_object*.py, stranger*.py） | [chuanqi305/MobileNet-SSD](https://github.com/chuanqi305/MobileNet-SSD) |
| `res10_300x300_ssd_iter_140000.caffemodel` | 人臉偵測（search_face_v.py） | OpenCV GitHub extra modules |

prototxt 已包含於 `host/models/`，caffemodel 需另行下載並放至 `host/` 根目錄。

---

## MobileNetSSD 類別對照

```
1:aeroplane  2:bicycle   3:bird      4:boat      5:bottle
6:bus        7:car       8:cat       9:chair    10:cow
11:diningtable 12:dog   13:horse   14:motorbike 15:person
16:pottedplant 17:sheep 18:sofa    19:train    20:tvmonitor
```

用法：`python search_object.py -o 7`（追蹤汽車）

---

## 技術棧

- **語言**：Python 3 / OpenCV · MicroPython（ESP32）
- **AI 推論**：OpenCV DNN（MobileNetSSD / ResNet-SSD）· face_recognition（dlib）
- **通訊**：UART Serial 或 paho-mqtt（切換 import）
- **串流**：MJPEG over HTTP（標準瀏覽器可直接觀看）
