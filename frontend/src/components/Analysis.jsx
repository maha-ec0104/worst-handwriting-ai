export default function Analysis({ result }) {
  const { uncertain_parts: unc, crossed_out: crossed, margin_notes: margin, document_structure: st } = result;
  const tables = st?.tables || [];
  return (
    <div className="card h-100">
      <div className="card-header">AI analysis</div>
      <div className="card-body">
        <p className="mb-2"><strong>Detected language:</strong>{" "}
          <span className="badge text-bg-primary">{result.detected_language}</span></p>
        {result.title && <p className="mb-2"><strong>Title:</strong> {result.title}</p>}
        <p className="mb-3 small text-muted">
          OCR engine: {result.ocr_engine || "none (Vision AI only)"} · Lines: {result.lines.length}
          {st?.has_signature ? " · Signature found" : ""}
        </p>

        <h6>Uncertain content</h6>
        {unc.length === 0 ? <p className="text-muted small">Nothing flagged.</p> : unc.map((u, i) => (
          <div key={i} className="alert alert-warning py-2 mb-2">
            ⚠ <mark className="unc">{u.text}</mark> {u.reason && <span className="small">— {u.reason}</span>}
            <div className="small">AI is not confident about this word.</div>
          </div>
        ))}

        <h6 className="mt-3">Crossed-out content</h6>
        {crossed.length === 0 ? <p className="text-muted small">None detected.</p> : crossed.map((c, i) => (
          <div key={i} className="mb-1"><span className="crossed">{c.text}</span>
            {c.replaced_by && <> → <strong>{c.replaced_by}</strong></>}</div>
        ))}

        <h6 className="mt-3">Margin notes</h6>
        {margin.length === 0 ? <p className="text-muted small">None detected.</p> : margin.map((m, i) => (
          <div key={i} className="mb-1">📝 {m.text}</div>
        ))}

        {tables.length > 0 && (<>
          <h6 className="mt-3">Table (prototype)</h6>
          {tables.map((t, ti) => (
            <table key={ti} className="table table-sm table-bordered"><tbody>
              {t.map((row, ri) => <tr key={ri}>{row.map((c, ci) => <td key={ci}>{c}</td>)}</tr>)}
            </tbody></table>
          ))}
        </>)}

        <h6 className="mt-3">Document structure</h6>
        <div className="small">
          {["title", "heading", "paragraph", "bullet", "numbered", "table", "signature"].map((t) => {
            const n = result.lines.filter((l) => l.type === t).length;
            return n ? <span key={t} className="badge text-bg-light border me-1">{t} × {n}</span> : null;
          })}
        </div>
      </div>
    </div>
  );
}
