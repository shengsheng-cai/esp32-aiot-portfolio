import sys
from pathlib import Path
from fastmcp import FastMCP
import chromadb

sys.path.insert(0, str(Path(__file__).parent.parent))
from common.embedding import embed, rerank

DB_PATH = str(Path(__file__).parent.parent / "rag" / "chroma_db")

print("連線 ChromaDB...")
_chroma = chromadb.PersistentClient(path=DB_PATH)
_collection = _chroma.get_collection(name="law_collection")

mcp = FastMCP("LawRAGServer")


@mcp.tool()
def search_law(query: str, top_k: int = 3) -> str:
    """
    從法規資料庫檢索相關條文，並由 Gemini Rerank 重新排序。
    :param query: 查詢字串（如「未戴安全帽罰多少」）
    :param top_k: 回傳條文數量，預設 3
    """
    q_emb = embed([query]).tolist()
    candidates = _collection.query(query_embeddings=q_emb, n_results=20)["documents"][0]
    if not candidates:
        return "找不到相關條文。"

    top_docs = rerank(query, candidates, top_k=top_k)

    lines = [f"針對「{query}」的相關法規：\n"]
    for i, doc in enumerate(top_docs, 1):
        lines.append(f"【{i}】\n{doc}\n{'─' * 40}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("LawRAGServer 啟動，port 8803")
    mcp.run(transport="http", host="127.0.0.1", port=8803)
