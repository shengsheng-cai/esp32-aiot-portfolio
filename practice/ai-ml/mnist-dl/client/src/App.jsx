import { useState } from "react";
import DrawingCanvas from "./components/DrawingCanvas";
import ResultsPanel from "./components/ResultsPanel";
import "./App.css";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="app">
      <header className="app-header">
        <h1>MNIST 多模型辨識</h1>
        <p>手寫數字 → 7 個模型同時推論</p>
      </header>

      <main className="app-main">
        <DrawingCanvas onResult={setResult} onLoading={setLoading} />
        <div className="divider" />
        {loading ? (
          <div className="loading">辨識中…</div>
        ) : (
          <ResultsPanel data={result} />
        )}
      </main>
    </div>
  );
}
