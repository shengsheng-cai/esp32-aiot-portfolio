import asyncio
import argparse
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main(url: str, tool: str | None, params: str):
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            if tool is None:
                result = await session.list_tools()
                print("可用工具：")
                for t in result.tools:
                    print(f"  {t.name}: {t.description}")
            else:
                result = await session.call_tool(tool, json.loads(params))
                print(result.content[0].text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP Client CLI")
    parser.add_argument("-a", "--address", default="http://127.0.0.1:8802/mcp")
    parser.add_argument("-t", "--tool", default=None, help="工具名稱（省略則列出所有工具）")
    parser.add_argument("-p", "--params", default="{}", help='工具參數 JSON，如 \'{"date":"2026-01-05"}\'')
    args = parser.parse_args()

    asyncio.run(main(args.address, args.tool, args.params))
