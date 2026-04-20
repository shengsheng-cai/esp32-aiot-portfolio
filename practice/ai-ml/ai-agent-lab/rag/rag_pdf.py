import os
import sys
from pathlib import Path
from google import genai
from dotenv import load_dotenv
import chromadb

sys.path.insert(0, str(Path(__file__).parent.parent))
from common.embedding import embed, rerank

load_dotenv()
_llm = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DEFAULT_DB = str(Path(__file__).parent / "chroma_db")


def get_collection(db_path: str = DEFAULT_DB):
    client = chromadb.PersistentClient(path=db_path)
    return client.get_collection(name="law_collection")


def search(collection, query: str, top_k: int = 20) -> list[str]:
    q_emb = embed([query]).tolist()
    results = collection.query(query_embeddings=q_emb, n_results=top_k)
    return results["documents"][0]


def ask(query: str, context_docs: list[str]) -> str:
    context = "\n\n".join(context_docs)
    prompt = f"""請根據以下法規內容回答問題，使用繁體中文，並指出相關條文。

法規內容：
{context}

問題：{query}"""
    response = _llm.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )
    return response.text


def main():
    collection = get_collection()
    print("Chroma DB 載入完成\n")

    while True:
        print("─" * 40)
        query = input("問題（Ctrl+C 離開）：")
        candidates = search(collection, query, top_k=10)
        top_docs = rerank(query, candidates)

        print("\n[Rerank 後 Top 5]")
        for i, doc in enumerate(top_docs, 1):
            print(f"  {i}. {doc[:80]}...")

        print("\n[Gemini 回答]")
        print(ask(query, top_docs))


if __name__ == "__main__":
    main()
