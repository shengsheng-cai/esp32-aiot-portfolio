# esp32-vision-mqtt

ESP32 MicroPython + PC 端 OpenCV 即時影像辨識與 MQTT/Serial 控制學習實驗室。課程來源（泰山職訓局 2025~2026）將 Raspberry Pi + Arduino I2C 架構移植至 ESP32 + UART。

## What I Built
PC 端用 OpenCV 做即時影像辨識（人臉 / 物件 / 陌生人偵測），透過 MQTT 或 Serial 把指令送到 ESP32，控制伺服馬達追蹤目標，並連動 LCD 與繼電器。傳輸層 MQTT/Serial 可切換（改 import 即可）。

## Skills Demonstrated
- OpenCV DNN：MobileNetSSD 物件偵測 · ResNet-SSD / Haar 人臉偵測
- face_recognition（dlib）陌生人辨識
- MJPEG over HTTP 即時串流
- UART Serial / MQTT 雙傳輸層（API 相同，可切換）
- ESP32 端：SG90 伺服追蹤 · HW-482 繼電器 · LCD 控制

## Hardware / Interface
ESP32 · SG90 舵機 · HW-482 繼電器 · LCD 1602
介面：UART · I2C · MQTT / Serial

```
D9 → SG90 Signal     D17 → HW-482 Relay
TX0/RX0 → UART TX/RX（接 PC USB-Serial）
D21/D22 → LCD SDA/SCL
```

## How to Run
1. `pip install opencv-python paho-mqtt pyserial face_recognition requests`
2. 下載 `MobileNetSSD_deploy.caffemodel` 放 `host/`
3. 燒錄本專案內的 `esp32/servo_uart.py` 至 ESP32
4. `cd host/ && python search_object.py -o 15`（追蹤人）
5. 瀏覽器開 `http://localhost:9090/a.mjpg` 看即時串流

## Validation Status
**程式層級練習，邏輯與結構已核對** — PC 端 OpenCV 偵測邏輯為核心；ESP32 端硬體控制待實機驗證。caffemodel 需另行下載。

## Next Step
接 ESP32 + SG90 做實機驗證，錄一段「影像辨識 → 馬達追蹤」的 demo 影片或 GIF。

---

## 架構

```
PC（Python 3 / OpenCV）  ──MQTT/Serial──>  ESP32（MicroPython）
  search_*.py / stranger*.py                servo_uart.py
  偵測 → 角度/指令                          SG90 / 繼電器 / LCD
```

傳輸層切換：偵測腳本第一行 `from mySerial import ...` 改成 `from myMQTT import ...` 即切 MQTT（API 相同）。

## PC 端偵測腳本

| 腳本 | 偵測方式 | 額外功能 |
|------|----------|----------|
| `search_face_hc_v4.py` | Haar Cascade 人臉 + 眼睛 | 縮圖加速 |
| `search_face_v.py` | ResNet-SSD 人臉 | 信心度過濾 |
| `search_object.py` | MobileNetSSD 物件（-o 1~20） | 指定類別追蹤 |
| `search_object_rec.py` | MobileNetSSD + 錄影 | 偵測到即錄影 |
| `stranger.py` | MobileNetSSD + face_recognition | 陌生人錄影 |
| `stranger_lcd.py` | 同上 + LCD/Relay | LCD 顯示 + 繼電器連動 |

## 模型檔

| 模型 | 用途 | 下載 |
|------|------|------|
| `MobileNetSSD_deploy.caffemodel` | 物件偵測 | [chuanqi305/MobileNet-SSD](https://github.com/chuanqi305/MobileNet-SSD) |
| `res10_300x300_ssd_iter_140000.caffemodel` | 人臉偵測 | OpenCV GitHub extra modules |

## 技術棧
- 語言：Python 3 / OpenCV · MicroPython（ESP32）
- AI 推論：OpenCV DNN（MobileNetSSD / ResNet-SSD）· face_recognition（dlib）
- 通訊：UART Serial 或 paho-mqtt（切換 import）
- 串流：MJPEG over HTTP
