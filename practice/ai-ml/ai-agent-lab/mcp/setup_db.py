import sqlite3

SCHEDULE = [
    ("2026-01-05", "AM", "Python 基礎語法", "後端講師"),
    ("2026-01-05", "PM", "Python 資料結構", "後端講師"),
    ("2026-01-06", "AM", "FastAPI 入門", "後端講師"),
    ("2026-01-06", "PM", "REST API 設計實作", "後端講師"),
    ("2026-01-07", "AM", "SQLite 資料庫設計", "資料庫講師"),
    ("2026-01-07", "PM", "SQLAlchemy ORM", "資料庫講師"),
    ("2026-01-08", "AM", "React 前端基礎", "前端講師"),
    ("2026-01-08", "PM", "React Hooks 實戰", "前端講師"),
    ("2026-01-09", "AM", "前後端串接實作", "後端講師"),
    ("2026-01-09", "PM", "專題製作", "業師"),
    ("2026-01-12", "AM", "Docker 容器化部署", "DevOps 講師"),
    ("2026-01-12", "PM", "Docker Compose 多服務", "DevOps 講師"),
    ("2026-01-13", "AM", "Nginx 反向代理設定", "DevOps 講師"),
    ("2026-01-13", "PM", "CI/CD 觀念與實作", "DevOps 講師"),
    ("2026-01-14", "AM", "Gemini API 應用", "AI 講師"),
    ("2026-01-14", "PM", "RAG 系統建構", "AI 講師"),
    ("2026-01-15", "AM", "MCP Server 開發", "AI 講師"),
    ("2026-01-15", "PM", "AI Agent 實作", "AI 講師"),
    ("2026-01-16", "AM", "專題製作", "業師"),
    ("2026-01-16", "PM", "專題成果發表", "業師"),
]

DB = "course.db"

conn = sqlite3.connect(DB)
conn.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        date       TEXT,
        period     TEXT,
        course     TEXT,
        instructor TEXT
    )
""")
conn.execute("DELETE FROM courses")
conn.executemany("INSERT INTO courses VALUES (?, ?, ?, ?)", SCHEDULE)
conn.commit()
conn.close()

print(f"course.db 建立完成，共 {len(SCHEDULE)} 筆")
