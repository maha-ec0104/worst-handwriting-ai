const ALL = ["Image preprocessing", "Layout analysis", "Language detection", "Handwriting recognition",
  "Context understanding", "Vision verification", "Confidence analysis"];

export default function Pipeline({ loading, result }) {
  if (!loading && !result) return null;
  const done = result ? result.processing_steps.join("|") : "";
  return (
    <div className="card mb-3">
      <div className="card-header">Processing pipeline</div>
      <div className="card-body d-flex flex-wrap gap-3">
        {ALL.map((s) => {
          const ok = result && done.includes(s.split(" ")[0]) && done.includes(s);
          return (
            <span key={s} className={ok ? "step-done" : "text-muted"}>
              {loading ? "… " : ok ? "✓ " : "– "}{s}
            </span>
          );
        })}
      </div>
    </div>
  );
}
