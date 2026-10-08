import { useState } from "react";
import { query, exportFile } from "../api.js";

const MARK = /(\[(?:UNCERTAIN|ILLEGIBLE)[^\]]*\])/gi;

function Highlight({ text }) {
  return text.split(MARK).map((p, i) =>
    /^\[(UNCERTAIN|ILLEGIBLE)/i.test(p) ? <mark key={i} className="unc">⚠ {p}</mark> : <span key={i}>{p}</span>);
}

const QUICK = ["What is written here?", "Show only the important points.", "Find dates.",
  "Find names.", "Find phone numbers.", "Summarize this note."];

export default function Result({ result, preview }) {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  async function ask(question) {
    setQ(question); setBusy(true); setAnswer("");
    try { setAnswer((await query(question, result.corrected_text)).answer); }
    catch (e) { setAnswer("Could not get an answer: " + e.message); }
    finally { setBusy(false); }
  }

  function download(name, content, type) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content], { type }));
    a.download = name; a.click(); URL.revokeObjectURL(a.href);
  }

  async function copy() {
    await navigator.clipboard.writeText(result.corrected_text);
    setCopied(true); setTimeout(() => setCopied(false), 1500);
  }

  return (
    <>
      <div className="row g-3">
        <div className="col-lg-6">
          <div className="card h-100">
            <div className="card-header">Original handwriting</div>
            <div className="card-body text-center">
              <img src={preview} alt="Original" className="handwriting-img" />
            </div>
          </div>
        </div>
        <div className="col-lg-6">
          <div className="card h-100">
            <div className="card-header d-flex justify-content-between">
              <span>AI understood text</span>
              <span className="badge text-bg-primary">{result.detected_language}</span>
            </div>
            <div className="card-body">
              <div className="text-pane">
                {result.lines.length === 0 ? <span className="text-muted">No readable text found.</span> :
                  result.lines.map((l, i) => (
                    <div key={i} className={`line ${l.level}`} title={`${l.level} · ${Math.round(l.confidence * 100)}%`}>
                      <Highlight text={l.text} />
                    </div>
                  ))}
              </div>
              <div className="mt-3 d-flex flex-wrap gap-2">
                <button className="btn btn-sm btn-outline-dark" onClick={copy}>{copied ? "Copied" : "Copy text"}</button>
                <button className="btn btn-sm btn-outline-dark" onClick={() => download("handwriting.txt", result.corrected_text, "text/plain")}>Download TXT</button>
                <button className="btn btn-sm btn-outline-dark" onClick={() => download("handwriting.json", JSON.stringify(result, null, 2), "application/json")}>Download JSON</button>
                <button className="btn btn-sm btn-outline-dark" onClick={() => exportFile("docx", result).catch((e) => alert(e.message))}>Download DOCX</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-3 mt-1">
        <div className="col-lg-6">
          <div className="card h-100">
            <div className="card-header">Raw recognition (before AI verification)</div>
            <div className="card-body text-pane">{result.raw_text || <span className="text-muted">OCR returned nothing.</span>}</div>
          </div>
        </div>
        <div className="col-lg-6">
          <div className="card h-100">
            <div className="card-header">Why did AI choose this text?</div>
            <div className="card-body">
              <p>{result.explanation}</p>
              {result.corrections?.length > 0 && result.corrections.map((c, i) => (
                <div key={i} className="small">
                  <span className="crossed">{c.from}</span> → <strong>{c.to}</strong> ({Math.round((c.confidence || 0) * 100)}%)
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="card mt-3">
        <div className="card-header">Ask about this document</div>
        <div className="card-body">
          <div className="d-flex flex-wrap gap-2 mb-3">
            {QUICK.map((s) => <button key={s} className="btn btn-sm btn-outline-secondary" disabled={busy} onClick={() => ask(s)}>{s}</button>)}
          </div>
          <div className="input-group">
            <input className="form-control" value={q} placeholder="Ask anything about the extracted text"
                   onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && q && ask(q)} />
            <button className="btn btn-dark" disabled={busy || !q} onClick={() => ask(q)}>Ask</button>
          </div>
          {busy && <div className="mt-3 text-muted">Thinking…</div>}
          {answer && <div className="alert alert-light border mt-3 mb-0 text-pane">{answer}</div>}
        </div>
      </div>
    </>
  );
}
