#!/bin/bash

cleanup() {
    echo -e "\n停止所有服務..."
    kill $COURSE_PID $LAW_PID 2>/dev/null
    exit
}
trap cleanup SIGINT SIGTERM EXIT

echo "啟動 CourseServer (port 8802)..."
lsof -ti:8802 | xargs kill -9 2>/dev/null || true
python mcp/course_server.py &
COURSE_PID=$!

echo "啟動 LawRAGServer (port 8803)..."
lsof -ti:8803 | xargs kill -9 2>/dev/null || true
python mcp/law_server.py &
LAW_PID=$!

echo "等待 server 就緒..."
sleep 2

echo "----------------------------------------"
echo "CourseServer: http://127.0.0.1:8802/mcp"
echo "LawRAGServer: http://127.0.0.1:8803/mcp"
echo "按 Ctrl+C 停止所有服務"
echo "----------------------------------------"

wait $COURSE_PID $LAW_PID
