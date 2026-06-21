"""
nRF24L01+ 2.4GHz 無線收發
Networking - nrf24l01

原始課程: 36.nRF24L01無線收發
平台: ESP32 MicroPython

功能:
  範例 1: 發射端（每秒傳送一筆訊息）
  範例 2: 接收端（等待並印出收到的訊息）

nRF24L01 規格:
  2.4GHz ISM 頻段（ch 0~125，建議 83 以下）
  傳輸速率：250kbps / 1Mbps / 2Mbps
  最大 payload：32 bytes
  工作電壓：3.3V（IO 可承受 5V，但建議 3.3V 供電）
  通訊介面：SPI

依賴驅動:
  MicroPython nrf24l01 driver（drivers/nrf24l01.py）
  下載：https://github.com/micropython/micropython-lib/tree/master/micropython/drivers/radio/nrf24l01

通道位址說明:
  5 bytes 字串，收發兩端必須相同
  例："1Node" → b"1Node"

硬體接線:
  nRF24L01 VCC  → 3.3V
  nRF24L01 GND  → GND
  nRF24L01 SCK  → D18（SPI1 CLK）
  nRF24L01 MOSI → D23（SPI1 MOSI）
  nRF24L01 MISO → D19（SPI1 MISO）
  nRF24L01 CE   → D4（可自定）
  nRF24L01 CSN  → D5（可自定）
  （建議 nRF24L01 模組供電腳並聯 10µF 電容，避免電壓抖動）
"""

import time
from machine import SPI, Pin

SPI_CLK  = 18
SPI_MOSI = 23
SPI_MISO = 19
CE_PIN   = 4
CSN_PIN  = 5

CHANNEL   = 83        # 建議 <= 83，避免超出 ISM 頻段
PIPE_ADDR = b"1Node"  # 5 bytes 通道位址，收發一致
PIPE_NUM  = 1         # 接收通道編號（建議 1）


def _make_rf():
    from nrf24l01 import NRF24L01
    spi = SPI(1, sck=Pin(SPI_CLK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
    csn = Pin(CSN_PIN, Pin.OUT, value=1)
    ce  = Pin(CE_PIN,  Pin.OUT, value=0)
    rf  = NRF24L01(spi, csn, ce, channel=CHANNEL, payload_size=32)
    return rf


# ── 範例 1：發射端 ────────────────────────────────────────────
def sender_demo():
    """每秒傳送一次訊息"""
    rf = _make_rf()
    rf.open_tx_pipe(PIPE_ADDR)
    rf.stop_listening()

    count = 0
    print("nRF24L01 sender ready. Channel={}".format(CHANNEL))

    while True:
        msg = "Hello {:04d}!".format(count)
        payload = msg.encode().ljust(32, b'\x00')
        try:
            rf.send(payload)
            print("Sent:", msg)
        except OSError:
            print("Send failed (no ACK)")
        count += 1
        time.sleep_ms(1000)


# ── 範例 2：接收端 ────────────────────────────────────────────
def receiver_demo():
    """等待並印出收到的訊息"""
    rf = _make_rf()
    rf.open_rx_pipe(PIPE_NUM, PIPE_ADDR)
    rf.start_listening()

    print("nRF24L01 receiver ready. Waiting... Channel={}".format(CHANNEL))

    while True:
        if rf.any():
            payload = rf.recv()
            msg = payload.rstrip(b'\x00').decode("utf-8", "ignore")
            print("Received:", msg)
        time.sleep_ms(10)


# ── 主程式（選擇一種模式）────────────────────────────────────
# sender_demo()
receiver_demo()
