import os
import asyncio
import json
from contextlib import AsyncExitStack
from openai import AsyncOpenAI
from fastmcp import Client
from dotenv import load_dotenv

load_dotenv()

MODEL = "gemini-2.5-flash-lite"

MCP_SERVERS = [
    "http://127.0.0.1:8802/mcp",  # mcp-server（課表）
    "http://127.0.0.1:8803/mcp",  # mcp-rag（法規 RAG）
]

SYSTEM = """你是一個嚴謹的 AI 助手。
- 課表相關問題：必須呼叫查課表工具，日期格式轉為 YYYY-MM-DD。
- 法規查詢：必須呼叫 search_law 工具。
- 工具回傳空資料時，誠實告知，禁止編造。"""


async def main():
    client = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    async with AsyncExitStack() as stack:
        tool_registry: dict[str, Client] = {}
        openai_tools: list[dict] = []

        print("連線 MCP Server...")
        for url in MCP_SERVERS:
            try:
                mcp = Client(url)
                await stack.enter_async_context(mcp)
                print(f"  OK: {url}")
                for tool in await mcp.list_tools():
                    tool_registry[tool.name] = mcp
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description or "",
                            "parameters": tool.inputSchema,
                        },
                    })
            except Exception as e:
                print(f"  FAIL: {url} — {e}")

        if not openai_tools:
            print("沒有載入任何工具，結束。")
            return

        print(f"\n載入 {len(openai_tools)} 個工具，開始對話（quit 離開）\n")

        messages = [{"role": "system", "content": SYSTEM}]

        while True:
            user_input = input("你：")
            if user_input.lower() in ("quit", "exit", "q"):
                break

            messages.append({"role": "user", "content": user_input})

            for _ in range(5):
                response = await client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=openai_tools,
                    temperature=0.1,
                )
                msg = response.choices[0].message

                if msg.tool_calls:
                    messages.append(msg)

                    async def call_one(call):
                        name = call.function.name
                        args = json.loads(call.function.arguments)
                        print(f"\n  -> {name}({args})")
                        if name not in tool_registry:
                            return f"找不到工具: {name}"
                        try:
                            result = await tool_registry[name].call_tool(name, arguments=args)
                            if hasattr(result, "content"):
                                return "\n".join(
                                    item.text if hasattr(item, "text") else str(item)
                                    for item in result.content
                                )
                            return str(result)
                        except Exception as e:
                            return f"錯誤: {e}"

                    texts = await asyncio.gather(*[call_one(c) for c in msg.tool_calls])
                    tool_results = "\n".join(
                        f"{c.function.name} 結果:\n{t}" for c, t in zip(msg.tool_calls, texts)
                    )
                    messages.append({"role": "user", "content": tool_results})
                else:
                    answer = msg.content
                    messages.append({"role": "assistant", "content": answer})
                    print(f"\nAgent：{answer}\n")
                    break


if __name__ == "__main__":
    asyncio.run(main())
