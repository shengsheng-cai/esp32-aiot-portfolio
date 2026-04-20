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

## 資料

| 資料 | 位置 | 建立方式 |
|------|------|---------|
| 課表（SQLite） | `mcp/courses.db` | `make dev`（自動建立） |
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
