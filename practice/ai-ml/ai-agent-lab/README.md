# AI Agent Lab

職訓課程重寫 — RAG · MCP · Agent · Vision 學習實驗室。

技術棧：Python · Gemini API · FAISS / Chroma · FastMCP · OpenAI SDK

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
| [rag/](rag/) | 向量檢索（FAISS）+ PDF RAG（Chroma） | FAISS · Chroma · Gemini Embedding |
| [mcp/](mcp/) | MCP 工具伺服器（SQLite）+ RAG MCP Server | FastMCP · SQLite |
| [agent/](agent/) | ReAct 推理迴圈 + 多 MCP 協調 | ReAct · AsyncExitStack |
| [vision/](vision/) | 多模態圖片問答 | Gemini Vision |

---

## 環境

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入 GEMINI_API_KEY
```

---

## 授權

資料集採用公開授權來源（政府 OpenData / 公開文件）
