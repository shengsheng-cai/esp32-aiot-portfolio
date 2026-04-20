VENV_BIN  := .venv/bin
PIP       := $(VENV_BIN)/pip
UVICORN   := $(VENV_BIN)/uvicorn

# .pth 放在 models/，透過環境變數傳給後端
MODEL_DIR ?= ../models

PYTHON    := $(VENV_BIN)/python

.PHONY: install dev backend frontend train-simple train-vit train-hf docker-build docker-up docker-down

install:
	$(PIP) install -r backend/requirements.txt
	npm --prefix client install

backend:
	cd backend && MODEL_DIR=$(MODEL_DIR) ../$(UVICORN) app:app --reload

frontend:
	npm --prefix client run dev

dev:
	cd backend && MODEL_DIR=$(MODEL_DIR) ../$(UVICORN) app:app --reload & \
	npm --prefix client run dev

train-simple:
	cd training && ../$(PYTHON) train_simple.py

train-vit:
	cd training && ../$(PYTHON) train_vit_custom.py

train-hf:
	cd training && ../$(PYTHON) train_vit_hf.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down
