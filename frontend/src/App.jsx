import { useState } from "react";
import Upload from "./components/Upload.jsx";
import Result from "./components/Result.jsx";
import Confidence from "./components/Confidence.jsx";
import Analysis from "./components/Analysis.jsx";
import Pipeline from "./components/Pipeline.jsx";
import { digitize } from "./api.js";

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function pick(f) {
    setFile(f); setResult(null); setError("");
    setPreview(f ? URL.createObjectURL(f) : null);
  }

  async function run() {
    if (!file) return;
    setLoading(true); setError(""); setResult(null);
    try { setResult(await digitize(file)); }
    catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }

  return (
    <>
      <header className="hero">
        <div className="container">
          <h1 className="mb-1">AI Handwriting Intelligence</h1>
          <p>Understand • Recognize • Verify • Preserve</p>
        </div>
      </header>
      <main className="container py-4">
        <Upload file={file} preview={preview} loading={loading} onPick={pick} onRun={run} />
        {error && <div className="alert alert-danger">{error}</div>}
        <Pipeline loading={loading} result={result} />
        {result && (
          <>
            {result.warnings?.length > 0 && (
              <div className="alert alert-warning">{result.warnings.map((w, i) => <div key={i}>{w}</div>)}</div>
            )}
            <Result result={result} preview={preview} />
            <div className="row g-3 mt-1">
              <div className="col-lg-4"><Confidence result={result} /></div>
              <div className="col-lg-8"><Analysis result={result} /></div>
            </div>
          </>
        )}
      </main>
    </>
  );
}
