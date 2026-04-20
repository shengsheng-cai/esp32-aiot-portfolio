import re
import sys
import argparse
import fitz
import chromadb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from common.embedding import embed

DEFAULT_DB = str(Path(__file__).parent / "chroma_db")


def load_file(path: str) -> str:
    if path.endswith(".txt"):
        return Path(path).read_text(encoding="utf-8")
    doc = fitz.open(path)
    return "".join(page.get_text() for page in doc)


def chunk_fixed(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


def chunk_by_article(text: str) -> list[str]:
    parts = re.split(r'(?=第\s*\d+(?:-\d+)?\s*條\n?)', text)
    return [p.strip() for p in parts if len(p.strip()) > 10]


def build(pdf_path: str, db_path: str = DEFAULT_DB, mode: str = "article"):
    print(f"讀取檔案：{pdf_path}")
    text = load_file(pdf_path)

    if mode == "article":
        chunks = chunk_by_article(text)
        print(f"依條文切分：{len(chunks)} 個區塊")
    else:
        chunks = chunk_fixed(text)
        print(f"固定大小切分：{len(chunks)} 個區塊")

    print("計算 embeddings（每分鐘限 100 筆，超過自動等待）...")
    embeddings = embed(chunks).tolist()

    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="law_collection")

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": Path(pdf_path).name, "index": i} for i in range(len(chunks))]

    print("寫入 ChromaDB...")
    collection.upsert(documents=chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)
    print(f"完成，DB 儲存於 {db_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將 PDF 建立為 Chroma 向量資料庫")
    parser.add_argument("pdf", help="PDF 或 TXT 檔案路徑")
    parser.add_argument("--mode", default="article", choices=["article", "fixed"],
                        help="切塊策略：article=依條文, fixed=固定大小")
    parser.add_argument("--db", default=DEFAULT_DB, help="Chroma DB 儲存路徑")
    args = parser.parse_args()
    build(args.pdf, args.db, args.mode)
