const COLORS = { HIGH: "success", MEDIUM: "warning", LOW: "danger" };

export default function Confidence({ result }) {
  const pct = Math.round(result.confidence * 100);
  const color = COLORS[result.confidence_level];
  return (
    <div className="card h-100">
      <div className="card-header">Confidence score</div>
      <div className="card-body">
        <div className="d-flex justify-content-between mb-1">
          <strong>AI confidence</strong>
          <span className={`badge text-bg-${color}`}>{result.confidence_level} · {pct}%</span>
        </div>
        <div className="progress mb-3" style={{ height: 12 }}>
          <div className={`progress-bar bg-${color}`} style={{ width: `${pct}%` }} />
        </div>
        <div className="d-flex justify-content-between mb-1">
          <span>Language confidence</span><span>{Math.round(result.language_confidence * 100)}%</span>
        </div>
        <div className="d-flex justify-content-between mb-1">
          <span>Uncertain words</span><span>{result.uncertain_parts.length}</span>
        </div>
        <div className="d-flex justify-content-between mb-1">
          <span>OCR vs verified match</span><span>{Math.round(result.ocr_agreement * 100)}%</span>
        </div>
        <div className="small text-muted mt-2">High ≥ 85% · Medium 60–84% · Low &lt; 60%</div>
      </div>
    </div>
  );
}
