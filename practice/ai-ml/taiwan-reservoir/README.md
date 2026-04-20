# Taiwan Reservoir API

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.20-43B02A?logo=selenium&logoColor=white)

爬取台灣水庫即時水情（[water.taiwanstat.com](https://water.taiwanstat.com/)），存入 SQLite，透過 FastAPI 提供查詢 API。

從泰山職訓局 AI/ML 課程改寫，修正原始碼中的 typo 與邏輯 bug，並重構為「爬取 → 清洗 → 存庫 → 查詢」四段流程。

---

## 系統架構

```
POST /scrape
    │
    ▼
scraper.py（Selenium headless Chrome）
    │ list[dict]
    ▼
db.py（SQLite → reservoir_snapshots）
    │
    ├── GET /latest          最新一次爬取的所有水庫（蓄水率排序）
    ├── GET /stats           全台平均 / 最高 / 最低蓄水率
    └── GET /history/{name}  單一水庫歷史趨勢
```

---

## 快速啟動

```bash
# 1. 建立虛擬環境並安裝套件
make install

# 2. 啟動 server 並自動觸發一次爬取
make start
```

> 預設使用 Brave Browser。若使用 Chrome 或其他路徑，設定環境變數：
> ```bash
> BRAVE_BIN=/path/to/your/browser make start
> ```

開發模式（支援 hot reload）：
```bash
make dev   # 啟動 server
make scrape  # 另開 terminal 手動觸發爬取
```

| 服務 | URL |
|------|-----|
| API 文件 | http://localhost:8001/docs |
| 最新水情 | http://localhost:8001/latest |
| 全台統計 | http://localhost:8001/stats |

---

## 目錄結構

```
taiwan-reservoir/
├── backend/
│   ├── app.py           # FastAPI 路由
│   ├── scraper.py       # Selenium 爬取
│   ├── db.py            # SQLite CRUD
│   └── requirements.txt
├── reservoir.db         # SQLite 資料庫（gitignored）
└── Makefile
```

---

## DB Schema

```sql
CREATE TABLE reservoir_snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scraped_at  TEXT NOT NULL,      -- ISO 8601
    name        TEXT NOT NULL,
    percent     REAL,               -- 蓄水百分比（數字）
    volume      TEXT,               -- 有效蓄水量（原始字串）
    status      TEXT,               -- 昨日變化，例如 +0.5% / -1.2%
    update_time TEXT                -- 水利署更新時間
);
```

---

## 原始碼 Bug 對照（課堂版 app.py）

| 行號 | 問題 | 修正 |
|------|------|------|
| 118 | `element.text.strp()` | 改為 `.strip()` |
| 126 | `percent = "資料擷取失敗"` 在 try/except 外，直接覆蓋抓到的值 | 移除，改用 `if not percent` 判斷 |
| 129+ | `volumn` 拼錯 | 改為 `volume` |
| 240 | `encoding='utf8-sig'` | 改為 `'utf-8-sig'` |
| 259 | 使用 `percent_clean` 但未建立該欄 | 補上數字清洗步驟 |
| 263 | `plt_df.empty()` | 改為 `plt_df.empty`（屬性，非方法）|
