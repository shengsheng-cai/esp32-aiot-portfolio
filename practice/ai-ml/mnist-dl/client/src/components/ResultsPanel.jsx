export default function ResultsPanel({ data }) {
  if (!data) {
    return <div className="results-empty">畫一個數字，按「送出辨識」</div>;
  }

  const entries = Object.entries(data.results).sort(
    ([, a], [, b]) => b.confidence - a.confidence
  );

  return (
    <div className="results-panel">
      <div className="results-best">
        最佳預測：<span className="best-digit">{data.best_prediction}</span>
        <span className="best-model">（{data.best_model}）</span>
      </div>

      <div className="results-list">
        {entries.map(([name, result]) => {
          const isBest = name === data.best_model;
          const pct = (result.confidence * 100).toFixed(1);
          return (
            <div key={name} className={`result-row${isBest ? " best" : ""}`}>
              <span className="result-name">{name}</span>
              <span className="result-digit">{result.prediction}</span>
              <div className="result-bar-wrap">
                <div className="result-bar" style={{ width: `${pct}%` }} />
              </div>
              <span className="result-pct">{pct}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
