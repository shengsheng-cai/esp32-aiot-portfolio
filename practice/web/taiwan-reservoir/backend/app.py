from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db import init_db, insert_snapshots, get_latest, get_history
from scraper import scrape


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Taiwan Reservoir API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/scrape", summary="觸發爬取並存入 DB")
def trigger_scrape():
    records = scrape()
    if not records:
        raise HTTPException(status_code=502, detail="爬取失敗，未取得任何資料")
    scraped_at = datetime.now()
    insert_snapshots(records, scraped_at)
    return {
        "scraped_at": scraped_at.isoformat(),
        "count": len(records),
    }


@app.get("/latest", summary="取最新一次爬取的所有水庫")
def latest():
    rows = get_latest()
    if not rows:
        raise HTTPException(status_code=404, detail="尚無資料，請先執行 POST /scrape")
    return rows


@app.get("/stats", summary="全台蓄水率統計（最新一筆）")
def stats():
    rows = get_latest()
    if not rows:
        raise HTTPException(status_code=404, detail="尚無資料，請先執行 POST /scrape")
    valid = [r for r in rows if r["percent"] is not None]
    if not valid:
        raise HTTPException(status_code=422, detail="無有效百分比資料")
    values = [r["percent"] for r in valid]
    return {
        "scraped_at": rows[0]["scraped_at"],
        "total": len(rows),
        "avg_percent": round(sum(values) / len(values), 2),
        "highest": {"name": valid[0]["name"], "percent": valid[0]["percent"]},
        "lowest": {"name": valid[-1]["name"], "percent": valid[-1]["percent"]},
    }


@app.get("/history/{name}", summary="單一水庫歷史蓄水率")
def history(name: str):
    rows = get_history(name)
    if not rows:
        raise HTTPException(status_code=404, detail=f"找不到水庫：{name}")
    return rows
