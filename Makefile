PORT     := $(shell ls /dev/cu.usbserial-* /dev/cu.wchusbserial* /dev/cu.SLAB_USBtoUART* 2>/dev/null | head -1)
MPREMOTE := $(HOME)/.venvs/mpremote/bin/mpremote
PYSERIAL := $(HOME)/.venvs/mpremote/bin/python3
ESPTOOL  := esptool
FIRMWARE := /tmp/micropython_esp32.bin
FW_ROOT  := practice/iot/esp32-module-lib/firmware
TARGET   := $(notdir $(basename $(shell find $(FW_ROOT) -name "*.py" | xargs ls -t 2>/dev/null | head -1)))

.PHONY: run repl erase flash help

## 跑腳本（預設跑最近存檔的 .py；要換檔就先 Cmd+S 那支再 make run）
run:
	$(PYSERIAL) -c "import serial,time; s=serial.Serial('$(PORT)'); s.dtr=False; time.sleep(0.1); s.dtr=True; s.close()"
	sleep 1
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
	@echo "  make run                   跑最近存檔的 .py（要換檔先 Cmd+S 該檔）"
	@echo "  make repl                  開啟互動式 REPL"
	@echo "  make erase                 清空 Flash"
	@echo "  make flash                 重刷 MicroPython 韌體"
	@echo ""
