import { useRef, useEffect } from "react";

const CANVAS_SIZE = 280;
const LINE_WIDTH = 18;
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function DrawingCanvas({ onResult, onLoading }) {
  const canvasRef = useRef(null);
  const ctxRef = useRef(null);
  const isDrawing = useRef(false);

  useEffect(() => {
    const ctx = canvasRef.current.getContext("2d");
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = LINE_WIDTH;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctxRef.current = ctx;
    fillBlack();
  }, []);

  function fillBlack() {
    const ctx = ctxRef.current;
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
  }

  function getPos(e) {
    const rect = canvasRef.current.getBoundingClientRect();
    // 支援滑鼠和觸控
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
      x: clientX - rect.left,
      y: clientY - rect.top,
    };
  }

  function startDraw(e) {
    e.preventDefault();
    isDrawing.current = true;
    const { x, y } = getPos(e);
    ctxRef.current.beginPath();
    ctxRef.current.moveTo(x, y);
  }

  function draw(e) {
    e.preventDefault();
    if (!isDrawing.current) return;
    const { x, y } = getPos(e);
    ctxRef.current.lineTo(x, y);
    ctxRef.current.stroke();
  }

  function stopDraw() {
    isDrawing.current = false;
  }

  function clearCanvas() {
    fillBlack();
    onResult(null);
  }

  async function submit() {
    canvasRef.current.toBlob(async (blob) => {
      const form = new FormData();
      form.append("file", blob, "digit.png");

      onLoading(true);
      try {
        const res = await fetch(`${API_URL}/predict`, { method: "POST", body: form });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        onResult(await res.json());
      } catch (err) {
        alert(`送出失敗：${err.message}`);
      } finally {
        onLoading(false);
      }
    }, "image/png");
  }

  return (
    <div className="canvas-wrapper">
      <canvas
        ref={canvasRef}
        width={CANVAS_SIZE}
        height={CANVAS_SIZE}
        onMouseDown={startDraw}
        onMouseMove={draw}
        onMouseUp={stopDraw}
        onMouseLeave={stopDraw}
        onTouchStart={startDraw}
        onTouchMove={draw}
        onTouchEnd={stopDraw}
        style={{ cursor: "crosshair", touchAction: "none" }}
      />
      <div className="canvas-buttons">
        <button onClick={clearCanvas}>清除</button>
        <button onClick={submit} className="primary">送出辨識</button>
      </div>
    </div>
  );
}
