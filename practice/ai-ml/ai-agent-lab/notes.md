# AI Agent 技術筆記

實作 `ai-agent-lab` 各模組後整理的概念筆記。

---

## 1. RAG（Retrieval-Augmented Generation）

LLM 本身不知道私有資料或最新資訊。RAG 的解法：**先從知識庫撈相關片段，再一起送進 prompt**。

```
問題 → embedding → 向量搜尋 → 取出相關片段 → 組成 prompt → LLM 生成答案
```

### Embedding

把文字轉成高維向量，語意相近的文字在向量空間中距離較近。
本專案用 Gemini `gemini-embedding-001`。

### 向量搜尋

**FAISS**（Meta 開源）：存在記憶體，速度快，適合快速實驗。重啟後需要重建索引。

**ChromaDB**：PersistentClient 把索引存到硬碟，下次直接載入，適合正式應用。

### Reranking（二階段搜尋）

向量搜尋是「模糊比對」，精準度有限。二階段做法：

```
向量搜尋取 top-10（快）→ Reranker 精排取 top-5（準）→ 送進 LLM
```

第一階段靠 embedding 相似度，第二階段靠 Reranker 直接比對 (query, doc) 對的相關性。
本專案用 Gemini 做 rerank（讓 Gemini 從候選清單中選出最相關的 N 筆）。

---

## 2. Chunking 策略

PDF 等長文件要切成小片段才能 embed。

### 固定大小切塊（`chunk_fixed`）

```python
while start < len(text):
    chunks.append(text[start:start + size])
    start += size - overlap  # overlap 避免語意被切斷
```

通用但可能切斷句子語意。`overlap` 讓相鄰 chunk 有重疊，降低語意遺失的機率。

### 語意切塊（`chunk_by_article`）

```python
re.split(r'(?=第\s*\d+(?:-\d+)?\s*條\n?)', text)
```

用 lookahead regex 在每條法條前切開，每個 chunk 包含完整法條。適合結構清楚的文件（法規、SOP），品質比固定切塊高但需要針對文件格式設計。

| 方式 | 優點 | 缺點 |
|------|------|------|
| 固定 size + overlap | 通用 | 可能切斷語意 |
| 語意切塊 | 每個 chunk 完整 | 需針對格式設計 |

---

## 3. MCP（Model Context Protocol）

Anthropic 提出的開放協定，讓 LLM 能用**標準化方式**呼叫外部工具，不需要為每個工具寫客製化整合。

```
LLM → JSON-RPC 2.0 請求 → MCP Server → 工具執行 → 結果回傳
```

### FastMCP 最小範例

```python
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def get_data(keyword: str) -> list[dict]:
    """根據關鍵字查詢資料"""
    # ...

mcp.run(transport="http", host="127.0.0.1", port=8802)
```

`@mcp.tool()` 的 docstring 就是工具說明，LLM 靠這個決定要不要呼叫這個工具。

### MCP 包裝 RAG

把 RAG 的檢索流程包成 MCP 工具，任何 MCP Client（Claude Desktop、自己寫的 Agent）都能呼叫，不需要知道 RAG 內部實作。

---

## 4. ReAct Agent

ReAct = **Re**asoning + **Act**ing。Agent 的最小運作迴圈：

```
輸入目標
  ↓
LLM 思考（Thought）→ 決定動作（Action）→ 執行工具 → 得到結果（Observation）
  ↓ 把結果加進 history，再讓 LLM 繼續思考
直到 action = "finish"
```

不靠任何框架，理解這個迴圈後，LangGraph / AutoGen 的架構就不陌生了。

### System Prompt 設計

工具清單要清楚定義在 system prompt，LLM 才知道有哪些動作可以選：

```
TOOLS:
1. bash(command)
2. read(file)
3. write(file,content)
4. finish(answer)

Respond with JSON only: {"thought": "...", "action": "...", "input": "..."}
```

強制 JSON 輸出讓程式容易解析，但 LLM 偶爾會輸出雜訊，需要 fallback regex 擷取。

---

## 5. Multi-MCP Agent

同時連接多個 MCP Server，讓 LLM 能呼叫來自不同來源的工具。

### 核心架構

```python
async with AsyncExitStack() as stack:
    tool_registry = {}   # tool_name → MCP Client
    openai_tools = []    # 工具清單（送給 LLM）

    for url in MCP_SERVERS:
        client = Client(url)
        await stack.enter_async_context(client)
        for tool in await client.list_tools():
            tool_registry[tool.name] = client   # 記錄工具屬於哪個 server
            openai_tools.append(...)
```

`tool_registry` 是關鍵：LLM 回傳 `tool_call` 後，從 registry 找到對應的 MCP Client 執行。

### Gemini + OpenAI 相容 API

Gemini 支援 OpenAI 相容端點，只需換 `base_url` 和 `api_key`，function calling 格式完全一樣：

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=GEMINI_API_KEY,
)
```

---

## 6. Vision API

把圖片和文字一起送給多模態 LLM，讓它「看圖回答」。

```python
from google.genai import types

image_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=[image_part, "這張圖裡有什麼？"],
)
```

Gemini SDK 直接傳 bytes，不需要手動 base64 編碼。

---

## 技術選型總結

| 元件 | 本專案 | 原課程 | 換掉的原因 |
|------|--------|--------|-----------|
| LLM | Gemini API | llama.cpp 本地 | 免安裝、別人 clone 直接跑 |
| Embedding | Gemini gemini-embedding-001 | SentenceTransformer 本地 | 同上 |
| Reranker | Gemini（prompt 排序） | CrossEncoder 本地模型 | 同上 |
| 向量 DB | FAISS + ChromaDB | 相同 | 無需更換 |
| MCP | FastMCP | 相同 | 無需更換 |
