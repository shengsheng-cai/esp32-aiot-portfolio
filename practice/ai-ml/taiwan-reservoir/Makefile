.PHONY: install dev scrape start

install:
	python3 -m venv .venv
	.venv/bin/pip install -r backend/requirements.txt

dev:
	cd backend && ../.venv/bin/uvicorn app:app --reload --port 8001

scrape:
	curl -s -X POST http://localhost:8001/scrape | python3 -m json.tool

start:
	cd backend && ../.venv/bin/uvicorn app:app --port 8001 &
	sleep 2
	curl -s -X POST http://localhost:8001/scrape | python3 -m json.tool
