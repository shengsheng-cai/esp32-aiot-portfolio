import os
import sys
import numpy as np
import faiss
from pathlib import Path
from google import genai
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from common.embedding import embed

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DOCUMENTS = [
    "RAG 是 Retrieval-Augmented Generation 的縮寫，結合檢索與生成兩個階段。",
    "FAISS 是 Meta AI Research 開發的高效向量搜尋函式庫。",
    "Embedding 是將文字轉換為高維度向量的技術，語意相近的文字向量距離較近。",
    "向量資料庫透過計算向量距離，找出語意相似的文件片段。",
    "LLM 生成答案前，先從知識庫取出相關片段作為 context 注入 prompt。",
    "FastAPI 是 Python 高效能 Web 框架，支援自動產生 OpenAPI 文件。",
    "Python 是目前最廣泛使用的 AI 開發語言，生態系完整。",
    "Docker 讓應用程式在容器中以一致的環境執行，簡化部署流程。",
    "SQLite 是輕量級的嵌入式關聯式資料庫，不需要獨立伺服器。",
    "Gemini 是 Google DeepMind 開發的大型語言模型，支援文字與多模態輸入。",
    "CrossEncoder 對每個（query, doc）對重新計算相關分數，提升檢索精準度。",
    "IndexFlatL2 是 FAISS 最基本的索引，對所有向量做暴力 L2 距離搜尋。",
    "Chroma 是開源的向量資料庫，支援 PersistentClient 將索引存到硬碟。",
    "MCP 是 Model Context Protocol，標準化 LLM 呼叫外部工具的介面。",
    "ReAct 是 Reasoning + Acting 的 Agent 設計模式，讓模型交替推理與執行。",
    "gemini-embedding-001 是 Gemini 的文字 embedding 模型，可將文字轉為高維向量。",
]


def build_index(vectors: np.ndarray) -> faiss.Index:
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    return index


def search(index: faiss.Index, query: str, top_k: int = 5) -> list[str]:
    q_vec = embed([query])
    _, indices = index.search(q_vec, top_k)
    return [DOCUMENTS[i] for i in indices[0]]


def ask(query: str, context_docs: list[str]) -> str:
    context = "\n".join(context_docs)
    prompt = f"""請根據以下資料回答問題，使用繁體中文回答。

資料：
{context}

問題：{query}"""

    response = _client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )
    return response.text


def main():
    print("建立向量索引...")
    vectors = embed(DOCUMENTS)
    index = build_index(vectors)
    print(f"索引建立完成，共 {len(DOCUMENTS)} 筆文件\n")

    while True:
        print("─" * 40)
        query = input("問題（Ctrl+C 離開）：")
        context_docs = search(index, query)
        print("\n[檢索到的相關片段]")
        for i, doc in enumerate(context_docs, 1):
            print(f"  {i}. {doc}")
        print("\n[Gemini 回答]")
        print(ask(query, context_docs))


if __name__ == "__main__":
    main()
