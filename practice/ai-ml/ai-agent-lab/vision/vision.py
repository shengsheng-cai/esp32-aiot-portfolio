import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def load_image(path: str) -> types.Part:
    p = Path(path)
    mime = MIME.get(p.suffix.lower(), "image/jpeg")
    return types.Part.from_bytes(data=p.read_bytes(), mime_type=mime)


def ask(image_part: types.Part, question: str) -> str:
    response = _client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[image_part, question],
    )
    return response.text


def main():
    if len(sys.argv) >= 2:
        image_path = sys.argv[1].strip("'\"")
    else:
        image_path = input("圖片路徑：").strip().strip("'\"")

    image_part = load_image(image_path)
    print(f"圖片載入：{image_path}\n")

    if len(sys.argv) >= 3:
        question = " ".join(sys.argv[2:])
        print(ask(image_part, question))
    else:
        while True:
            question = input("問題（Ctrl+C 離開）：")
            print(ask(image_part, question))
            print()


if __name__ == "__main__":
    main()
