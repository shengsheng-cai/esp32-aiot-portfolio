PORT     := $(shell ls /dev/cu.usbserial-* /dev/cu.wchusbserial* /dev/cu.SLAB_USBtoUART* 2>/dev/null | head -1)
MPREMOTE := $(HOME)/.venvs/mpremote/bin/mpremote
ESPTOOL  := esptool
FIRMWARE := /tmp/micropython_esp32.bin
FW_ROOT  := practice/iot/esp32-module-lib/firmware
TARGET   := $(notdir $(basename $(shell find $(FW_ROOT) -name "*.py" | xargs ls -t 2>/dev/null | head -1)))

.PHONY: run repl erase flash help

run:
	$(MPREMOTE) connect $(PORT) run --no-follow $(shell find $(FW_ROOT) -name "$(TARGET).py" | head -1) + repl

## 開啟互動式 REPL（不跑腳本）
repl:
	$(MPREMOTE) connect $(PORT)

## 清空 Flash
erase:
	$(ESPTOOL) --port $(PORT) erase-flash

## 重刷 MicroPython 韌體
flash:
	$(ESPTOOL) --port $(PORT) --baud 460800 write-flash -z 0x1000 $(FIRMWARE)

help:
	@echo ""
	@echo "ESP32 MicroPython 控制指令"
	@echo "---------------------------"
	@echo "  make run                   執行 TARGET 設定的腳本（預設：最近修改的 .py）"
	@echo "  make repl                  開啟互動式 REPL"
	@echo "  make erase                 清空 Flash"
	@echo "  make flash                 重刷 MicroPython 韌體"
	@echo ""
