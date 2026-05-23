# AI Agent Lab

職訓課程重寫 — RAG · MCP · Agent · Vision 學習實驗室。

技術棧：Python · Gemini API（gemini-embedding-001 · gemini-2.5-flash-lite）· FAISS · Chroma · FastMCP · Gemini OpenAI 相容 API

---

## 學習路徑

```
rag/rag_basic → rag/rag_pdf → mcp/course_server → mcp/law_server → agent/react → agent/multi_mcp → vision/vision
   基礎 RAG       PDF RAG       MCP 工具伺服器      MCP 包 RAG       推理迴圈      多工具協調       多模態
```

---

## 模組清單

| 資料夾 | 主題 | 核心技術 |
|--------|------|---------|
| [common/](common/) | 共用模組：Gemini Embedding · Rerank | gemini-embedding-001 · gemini-2.5-flash-lite |
| [rag/](rag/) | 向量檢索（FAISS）+ PDF RAG（Chroma） | FAISS · Chroma · Gemini Embedding |
| [mcp/](mcp/) | MCP 工具伺服器（SQLite 課表）+ RAG MCP Server（法規） | FastMCP · SQLite |
| [agent/](agent/) | ReAct 推理迴圈 + 多 MCP 協調 | ReAct · AsyncExitStack · Gemini OpenAI 相容 API |
| [vision/](vision/) | 多模態圖片問答 | Gemini Vision |

---

## 環境

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入 GEMINI_API_KEY
```

---

## 前置條件（Prerequisites）

- **Gemini API key（必要）**：所有模組都會 `load_dotenv()` 並讀取 `GEMINI_API_KEY`（embedding、RAG、Agent、Vision 皆然）。沒設 key 無法執行任何需要呼叫模型的指令。請 `cp .env.example .env` 後填入。
- **資料庫需自行建立**：課表 DB（`course.db`）與法規向量庫（`rag/chroma_db/`）**都不在 git 內**，clone 後不存在，需依下方「資料」段建立：
  - 課表 DB：`make mcp-setup`（或第一次 `make dev` 會自動建）。
  - 法規向量庫：`make rag-pdf-setup PDF=rag/data/traffic_law.txt`（會呼叫 Gemini Embedding，需網路與 API key）。
- **MCP server 為背景服務**：`make agent-multi` 需先 `make dev` 啟動雙 MCP server（CourseServer :8802、LawRAGServer :8803）。`make dev` 會 foreground 阻塞，請另開終端機跑 agent。
- **網路 / 額度**：embedding 與 LLM 呼叫走 Google Gemini 線上 API；`common/embedding.py` 內建每分鐘限 100 筆的節流（超過自動 sleep 62 秒），大量文件建庫會明顯變慢。

## 安全注意（ReAct Agent）

`make agent-react` 的 ReAct 迴圈含 `bash` / `write` 工具（`agent/react.py`），會**直接執行或寫入模型產生的命令與檔案**，無沙箱限制。
- **僅限本地學習 / 受控環境**使用。
- **請勿**對不可信的 prompt、或在生產環境執行。

## 驗證狀態（Validation Status）

- **程式層級**：Makefile target、各入口腳本的環境變數（`GEMINI_API_KEY`）、模型名稱（`gemini-embedding-001`、`gemini-2.5-flash-lite`）、FAISS / Chroma / FastMCP 用法與本 README 對照一致。
- **尚未端到端實跑驗證**：README 與程式對照一致，但未實際安裝套件、設定 API key、建 DB、啟動 server 跑過；端到端行為（含 Gemini 線上呼叫）以實機為準。

---

## 資料

| 資料 | 位置 | 建立方式 |
|------|------|---------|
| 課表（SQLite） | `course.db`（repo 根目錄） | `make dev` 或 `make mcp-setup`（自動建立） |
| 法規向量庫（Chroma） | `rag/chroma_db/` | `make rag-pdf-setup PDF=rag/data/traffic_law.txt` |
| 法規原文 | `rag/data/traffic_law.txt` | 道路交通管理處罰條例（政府 OpenData） |

兩個 DB 不在 git 裡，clone 後需要手動建立。

---

## 常用指令

```bash
make rag-basic                              # FAISS 基礎 RAG
make rag-pdf-setup PDF=rag/data/traffic_law.txt  # 建立法規向量庫
make rag-pdf                                # Chroma PDF RAG
make dev                                    # 啟動雙 MCP Server（課表 + 法規）
make agent-multi                            # 多 MCP Agent（需先 make dev）
make agent-react GOAL="你的目標"            # ReAct Agent
make vision                                 # 圖片問答
```

---

## 授權

資料集採用公開授權來源（政府 OpenData / 公開文件）
