import React, { useState } from "react";
import { createRoot } from "react-dom/client";

const API_BASE = "http://localhost:8020";

function App() {
  const [file, setFile] = useState(null);
  const [textHint, setTextHint] = useState("");
  const [result, setResult] = useState(null);
  const [batchResult, setBatchResult] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [queueStats, setQueueStats] = useState(null);
  const [error, setError] = useState("");

  async function submitSingle(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("Select a file first.");
      return;
    }

    const form = new FormData();
    form.append("file", file);
    form.append("text_hint", textHint);

    try {
      const response = await fetch(`${API_BASE}/api/intake/triage`, {
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

  async function submitBatch() {
    setError("");
    setBatchResult(null);

    const payload = {
      documents: [
        {
          filename: "urgent-appeal.pdf",
          content_type: "application/pdf",
          text_hint: "urgent deadline appeal"
        },
        {
          filename: "data-ingest.csv",
          content_type: "text/csv",
          text_hint: "tabular payload"
        }
      ]
    };

    try {
      const response = await fetch(`${API_BASE}/api/intake/batch/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        throw new Error(`Batch request failed: ${response.status}`);
      }
      const data = await response.json();
      setBatchResult(data);
      pollJob(data.job_id);
    } catch (e) {
      setError(String(e));
    }
  }

  async function pollJob(jobId) {
    for (let i = 0; i < 10; i += 1) {
      const response = await fetch(`${API_BASE}/api/intake/jobs/${jobId}`);
      if (!response.ok) {
        throw new Error(`Job status failed: ${response.status}`);
      }
      const data = await response.json();
      setJobStatus(data);
      if (data.status === "completed") {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 300));
    }

    const stats = await fetch(`${API_BASE}/api/intake/queue/stats`);
    if (stats.ok) {
      setQueueStats(await stats.json());
    }
  }

  return (
    <main style={{ maxWidth: 860, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>Document Intake + AI Triage</h1>

      <section>
        <h2>Single Document Triage</h2>
        <form onSubmit={submitSingle}>
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          <input
            placeholder="Optional text hint"
            value={textHint}
            onChange={(e) => setTextHint(e.target.value)}
            style={{ marginLeft: 8 }}
          />
          <button style={{ marginLeft: 8 }} type="submit">Analyze</button>
        </form>
      </section>

      <section style={{ marginTop: 20 }}>
        <h2>Batch Queue Demo</h2>
        <button type="button" onClick={submitBatch}>Submit Demo Batch</button>
        {batchResult ? <p>Batch Job: {batchResult.job_id}</p> : null}
      </section>

      {queueStats ? (
        <section style={{ marginTop: 20 }}>
          <h2>Queue Stats</h2>
          <pre>{JSON.stringify(queueStats, null, 2)}</pre>
        </section>
      ) : null}

      {jobStatus ? (
        <section style={{ marginTop: 20 }}>
          <h2>Latest Batch Job Status</h2>
          <pre>{JSON.stringify(jobStatus, null, 2)}</pre>
        </section>
      ) : null}

      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      {result ? <pre>{JSON.stringify(result, null, 2)}</pre> : null}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
