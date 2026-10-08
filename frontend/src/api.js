const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function handle(res) {
  let data = null;
  try { data = await res.json(); } catch { /* not json */ }
  if (!res.ok || (data && data.success === false)) {
    throw new Error((data && data.error) || `Server error (${res.status})`);
  }
  return data;
}

export async function digitize(file) {
  const form = new FormData();
  form.append("file", file);
  try {
    return await handle(await fetch(`${API}/digitize`, { method: "POST", body: form }));
  } catch (e) {
    if (e instanceof TypeError) throw new Error("Cannot reach the backend. Is it running? Check VITE_API_URL.");
    throw e;
  }
}

export async function query(question, document) {
  return handle(await fetch(`${API}/query`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, document }),
  }));
}

export async function exportFile(format, data) {
  const res = await fetch(`${API}/export`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ format, data }),
  });
  if (!res.ok) throw new Error("Export failed");
  const blob = await res.blob();
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `handwriting.${format}`;
  a.click();
  URL.revokeObjectURL(a.href);
}
