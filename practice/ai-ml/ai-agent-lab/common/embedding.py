import os
import time
import numpy as np
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def embed(texts: list[str]) -> np.ndarray:
    batch_size = 100
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        if i > 0:
            time.sleep(62)
        result = _client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts[i:i + batch_size],
        )
        all_embeddings.extend(e.values for e in result.embeddings)
    return np.array(all_embeddings, dtype="float32")


def rerank(query: str, docs: list[str], top_k: int = 5) -> list[str]:
    numbered = "\n".join(f"{i+1}. {doc[:800]}" for i, doc in enumerate(docs))
    prompt = f"""以下是搜尋問題和候選文件。請選出最相關的 {top_k} 筆，只回傳編號（逗號分隔，如：3,1,5,2,4），不要其他文字。

問題：{query}

候選文件：
{numbered}

最相關的 {top_k} 筆編號："""

    response = _client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )
    try:
        indices = [int(x.strip()) - 1 for x in response.text.strip().split(",")]
        return [docs[i] for i in indices if 0 <= i < len(docs)]
    except Exception as e:
        print(f"[rerank fallback] {e}")
        return docs[:top_k]


class GeminiEmbeddingFn:
    def name(self) -> str:
        return "gemini-embedding-fn"

    def __call__(self, input: list[str]) -> list[list[float]]:
        return embed(input).tolist()
