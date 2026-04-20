import sqlite3
from fastmcp import FastMCP

mcp = FastMCP("CourseServer")
DB = "course.db"


def query(sql: str, args: tuple = ()) -> list[dict]:
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql, args)
        return [dict(row) for row in cur.fetchall()]


@mcp.tool()
def get_all_courses() -> list[dict]:
    """取得完整課程表"""
    return query("SELECT * FROM courses ORDER BY date, period")


@mcp.tool()
def get_courses_by_date(date: str) -> list[dict]:
    """依日期查詢課程，date 格式 YYYY-MM-DD"""
    return query("SELECT * FROM courses WHERE date = ?", (date,))


@mcp.tool()
def get_courses_by_instructor(instructor: str) -> list[dict]:
    """依講師查詢負責課程"""
    return query("SELECT * FROM courses WHERE instructor LIKE ?", (f"%{instructor}%",))


@mcp.tool()
def get_courses_by_keyword(keyword: str) -> list[dict]:
    """依課程名稱關鍵字模糊搜尋"""
    return query("SELECT * FROM courses WHERE course LIKE ?", (f"%{keyword}%",))


if __name__ == "__main__":
    print("CourseServer 啟動，port 8802")
    mcp.run(transport="http", host="127.0.0.1", port=8802)
