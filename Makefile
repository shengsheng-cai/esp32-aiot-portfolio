PORT     := /dev/cu.usbserial-0001
MPREMOTE := $(HOME)/.venvs/mpremote/bin/mpremote
ESPTOOL  := esptool
FIRMWARE := /tmp/micropython_esp32.bin
FW_ROOT  := practice/iot/esp32-module-lib/firmware
TARGET   := keypad_dht11

.PHONY: run repl erase flash help

run:
	$(MPREMOTE) connect $(PORT) run $(shell find $(FW_ROOT) -name "$(TARGET).py" | head -1)

## 開啟互動式 REPL
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
	@echo "  make run                   執行 TARGET 設定的腳本（預設 keypad_dht11）"
	@echo "  make repl                  開啟互動式 REPL"
	@echo "  make erase                 清空 Flash"
	@echo "  make flash                 重刷 MicroPython 韌體"
	@echo ""
