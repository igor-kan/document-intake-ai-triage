import React, { useState } from "react";
import { createRoot } from "react-dom/client";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("Select a file first.");
      return;
    }

    const form = new FormData();
    form.append("file", file);

    try {
      const response = await fetch("http://localhost:8020/api/intake/triage", {
        method: "POST",
        body: form
      });
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      setResult(await response.json());
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <main style={{ maxWidth: 760, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>Document Intake + AI Triage</h1>
      <form onSubmit={submit}>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button style={{ marginLeft: 8 }} type="submit">Analyze</button>
      </form>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      {result ? <pre>{JSON.stringify(result, null, 2)}</pre> : null}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
