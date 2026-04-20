.PHONY: rag-basic rag-pdf-setup rag-pdf mcp-setup mcp-server mcp-client mcp-rag dev agent-react agent-multi vision clean

rag-basic:
	python rag/rag_basic.py

rag-pdf-setup:
	python rag/build_db.py $(PDF)

rag-pdf:
	python rag/rag_pdf.py

mcp-setup:
	python mcp/setup_db.py

mcp-server:
	python mcp/course_server.py

mcp-client:
	python mcp/client.py $(ARGS)

mcp-rag:
	python mcp/law_server.py

dev:
	@test -f mcp/courses.db || python mcp/setup_db.py
	@bash dev_start.sh

agent-react:
	python agent/react.py $(GOAL)

agent-multi:
	python agent/multi_mcp.py

vision:
	python vision/vision.py $(IMG) $(Q)

clean:
	-@pkill -9 -f "course_server" 2>/dev/null
	-@pkill -9 -f "law_server" 2>/dev/null
	@echo "服務已停止"
