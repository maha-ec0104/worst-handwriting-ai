export default function Upload({ file, preview, loading, onPick, onRun }) {
  return (
    <div className="card mb-3">
      <div className="card-header">1. Upload document</div>
      <div className="card-body">
        <div className="drop">
          <input className="form-control mb-3" type="file" accept="image/*"
                 onChange={(e) => onPick(e.target.files[0] || null)} />
          {preview ? <img src={preview} alt="Your handwriting" className="handwriting-img" />
                   : <div className="text-muted">Choose a photo of handwriting (JPG or PNG, up to 10 MB).</div>}
        </div>
        <button className="btn btn-dark btn-lg mt-3" disabled={!file || loading} onClick={onRun}>
          {loading ? (<><span className="spinner-border spinner-border-sm me-2" />Analysing…</>) : "Digitize handwriting"}
        </button>
      </div>
    </div>
  );
}
