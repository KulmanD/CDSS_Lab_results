import { Activity, AlertTriangle, Download, Plus, Send, Trash2, Upload } from "lucide-react";
import { useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

const markerDefaults = {
  hemoglobin: { unit: "g/dL", value: "11.4" },
  mcv: { unit: "fL", value: "78" },
  fasting_glucose: { unit: "mg/dL", value: "112" },
  hba1c: { unit: "%", value: "5.8" },
  creatinine: { unit: "mg/dL", value: "1.1" },
  egfr: { unit: "mL/min/1.73m2", value: "68" },
  total_cholesterol: { unit: "mg/dL", value: "210" },
  ldl: { unit: "mg/dL", value: "145" },
  hdl: { unit: "mg/dL", value: "38" },
  triglycerides: { unit: "mg/dL", value: "180" },
  vldl: { unit: "mg/dL", value: "32" },
  crp: { unit: "mg/dL", value: "2.4" }
};

const markerOptions = [
  ["hemoglobin", "Hemoglobin"],
  ["mcv", "MCV"],
  ["fasting_glucose", "Fasting glucose"],
  ["hba1c", "HbA1c"],
  ["creatinine", "Creatinine"],
  ["egfr", "eGFR"],
  ["total_cholesterol", "Total cholesterol"],
  ["ldl", "LDL"],
  ["hdl", "HDL"],
  ["triglycerides", "Triglycerides"],
  ["vldl", "VLDL"],
  ["crp", "CRP"]
];

const urgencyMeta = {
  routine: { label: "Routine", className: "routine" },
  monitor: { label: "Monitor", className: "monitor" },
  prompt_review: { label: "Prompt review", className: "prompt" },
  urgent_review: { label: "Urgent review", className: "urgent" }
};

const today = new Date().toISOString().slice(0, 10);

function emptyRow(testName = "hemoglobin", date = today) {
  const defaults = markerDefaults[testName] ?? { unit: "", value: "" };
  return {
    id: crypto.randomUUID(),
    test_name: testName,
    value: defaults.value,
    unit: defaults.unit,
    collected_at: date
  };
}

function serializeRow(row) {
  return {
    test_name: row.test_name,
    value: Number(row.value),
    unit: row.unit,
    collected_at: row.collected_at
  };
}

function ResultCard({ result }) {
  const meta = urgencyMeta[result.urgency_level] ?? urgencyMeta.routine;
  return (
    <article className={`result-card ${meta.className}`}>
      <div className="result-header">
        <div>
          <h3>{result.pattern}</h3>
          <p>{result.message}</p>
        </div>
        <span className={`urgency-pill ${meta.className}`}>{meta.label}</span>
      </div>
      <p className="plain-language">{result.plain_language_explanation}</p>
      <div className="detail-grid">
        <section>
          <h4>Evidence</h4>
          <ul>
            {result.evidence.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
        <section>
          <h4>Limitations</h4>
          <ul>
            {result.limitations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      </div>
    </article>
  );
}

function ResultPanel({ analysis, error }) {
  if (error) {
    return (
      <section className="panel result-panel">
        <div className="panel-title error-title">
          <AlertTriangle size={18} />
          <h2>Validation</h2>
        </div>
        <pre className="error-box">{error}</pre>
      </section>
    );
  }

  if (!analysis) {
    return (
      <section className="panel result-panel empty-state">
        <Activity size={28} />
        <h2>Results</h2>
        <p>No analysis submitted.</p>
      </section>
    );
  }

  const meta = urgencyMeta[analysis.overall_urgency] ?? urgencyMeta.routine;
  return (
    <section className="panel result-panel">
      <div className="summary-band">
        <div>
          <span className="eyebrow">Overall urgency</span>
          <h2>{meta.label}</h2>
        </div>
        <span className={`urgency-pill ${meta.className}`}>{analysis.overall_urgency}</span>
      </div>
      <p className="disclaimer">{analysis.disclaimer}</p>
      <div className="result-stack">
        {analysis.results.map((result) => (
          <ResultCard key={result.rule_id} result={result} />
        ))}
      </div>
    </section>
  );
}

function RecordRows({ title, rows, setRows, compact = false }) {
  function updateRow(id, field, value) {
    setRows((current) =>
      current.map((row) => {
        if (row.id !== id) return row;
        if (field === "test_name") {
          const defaults = markerDefaults[value] ?? { unit: row.unit, value: row.value };
          return { ...row, test_name: value, unit: defaults.unit, value: defaults.value };
        }
        return { ...row, [field]: value };
      })
    );
  }

  function removeRow(id) {
    setRows((current) => current.filter((row) => row.id !== id));
  }

  return (
    <section className="rows-block">
      <div className="subhead">
        <h3>{title}</h3>
        <button type="button" className="icon-button" title={`Add ${title.toLowerCase()} row`} onClick={() => setRows((current) => [...current, emptyRow("hemoglobin")])}>
          <Plus size={16} />
        </button>
      </div>
      <div className="table-like">
        <div className="table-row table-head">
          <span>Marker</span>
          <span>Value</span>
          <span>Unit</span>
          <span>Date</span>
          <span />
        </div>
        {rows.map((row) => (
          <div className={`table-row ${compact ? "compact" : ""}`} key={row.id}>
            <select value={row.test_name} onChange={(event) => updateRow(row.id, "test_name", event.target.value)}>
              {markerOptions.map(([value, label]) => (
                <option value={value} key={value}>
                  {label}
                </option>
              ))}
            </select>
            <input value={row.value} type="number" step="0.1" onChange={(event) => updateRow(row.id, "value", event.target.value)} />
            <input value={row.unit} onChange={(event) => updateRow(row.id, "unit", event.target.value)} />
            <input value={row.collected_at} type="date" onChange={(event) => updateRow(row.id, "collected_at", event.target.value)} />
            <button type="button" className="icon-button danger" title="Remove row" onClick={() => removeRow(row.id)} disabled={rows.length === 1 && !compact}>
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function App() {
  const [patient, setPatient] = useState({ patient_id: "demo-001", age: "45", sex: "female", pregnant: "false" });
  const [currentRows, setCurrentRows] = useState([emptyRow("hemoglobin"), emptyRow("mcv")]);
  const [historyRows, setHistoryRows] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [pdfFile, setPdfFile] = useState(null);

  const sampleCsv = useMemo(
    () =>
      [
        "patient_id,age,sex,test_name,value,unit,collected_at,pregnant,source_label",
        "demo-001,45,female,hemoglobin,11.4,g/dL,2026-06-26,false,Hemoglobin",
        "demo-001,45,female,mcv,78,fL,2026-06-26,false,MCV",
        "demo-001,45,female,ldl,145,mg/dL,2026-06-26,false,LDL",
        "demo-001,45,female,crp,2.4,mg/dL,2026-06-26,false,CRP"
      ].join("\n"),
    []
  );

  function updatePatient(field, value) {
    setPatient((current) => ({ ...current, [field]: value }));
  }

  async function parseResponse(response) {
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(JSON.stringify(body.detail ?? body, null, 2));
    }
    return body;
  }

  async function submitManual(event) {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    try {
      const payload = {
        patient: {
          patient_id: patient.patient_id || null,
          age: Number(patient.age),
          sex: patient.sex,
          pregnant: patient.pregnant === "" ? null : patient.pregnant === "true"
        },
        current_results: currentRows.map(serializeRow),
        historical_results: historyRows.map(serializeRow)
      };
      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      setAnalysis(await parseResponse(response));
    } catch (err) {
      setError(err.message);
      setAnalysis(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function submitCsv(event) {
    event.preventDefault();
    if (!csvFile) return;
    setIsLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", csvFile);
      const response = await fetch(`${API_BASE}/api/analyze/csv`, {
        method: "POST",
        body: formData
      });
      setAnalysis(await parseResponse(response));
    } catch (err) {
      setError(err.message);
      setAnalysis(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function submitPdf(event) {
    event.preventDefault();
    if (!pdfFile) return;
    setIsLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", pdfFile);
      const response = await fetch(`${API_BASE}/api/analyze/pdf`, {
        method: "POST",
        body: formData
      });
      setAnalysis(await parseResponse(response));
    } catch (err) {
      setError(err.message);
      setAnalysis(null);
    } finally {
      setIsLoading(false);
    }
  }

  function downloadSampleCsv() {
    const blob = new Blob([sampleCsv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "cdss_sample_labs.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">Rule-based CDSS</span>
          <h1>Lab Results Review</h1>
        </div>
        <span className="system-badge">No AI runtime</span>
      </header>

      <div className="workspace">
        <section className="panel input-panel">
          <div className="panel-title">
            <Activity size={18} />
            <h2>Patient record</h2>
          </div>
          <form onSubmit={submitManual} className="form-stack">
            <div className="patient-grid">
              <label>
                Patient ID
                <input value={patient.patient_id} onChange={(event) => updatePatient("patient_id", event.target.value)} />
              </label>
              <label>
                Age
                <input value={patient.age} type="number" min="0" onChange={(event) => updatePatient("age", event.target.value)} />
              </label>
              <label>
                Sex
                <select value={patient.sex} onChange={(event) => updatePatient("sex", event.target.value)}>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="other_unknown">Other/unknown</option>
                </select>
              </label>
              <label>
                Pregnant
                <select value={patient.pregnant} onChange={(event) => updatePatient("pregnant", event.target.value)}>
                  <option value="">Unknown</option>
                  <option value="false">No</option>
                  <option value="true">Yes</option>
                </select>
              </label>
            </div>

            <RecordRows title="Current results" rows={currentRows} setRows={setCurrentRows} />
            <RecordRows title="Historical results" rows={historyRows} setRows={setHistoryRows} compact />

            <button className="primary-button" type="submit" disabled={isLoading} title="Submit manual analysis">
              <Send size={17} />
              Analyze record
            </button>
          </form>

          <form onSubmit={submitCsv} className="csv-panel">
            <div className="subhead">
              <h3>CSV upload</h3>
              <button type="button" className="icon-button" title="Download CSV sample" onClick={downloadSampleCsv}>
                <Download size={16} />
              </button>
            </div>
            <input type="file" accept=".csv,text/csv" onChange={(event) => setCsvFile(event.target.files?.[0] ?? null)} />
            <button className="secondary-button" type="submit" disabled={isLoading || !csvFile} title="Upload CSV for analysis">
              <Upload size={17} />
              Analyze CSV
            </button>
          </form>

          <form onSubmit={submitPdf} className="csv-panel">
            <div className="subhead">
              <h3>PDF upload</h3>
            </div>
            <input type="file" accept=".pdf,application/pdf" onChange={(event) => setPdfFile(event.target.files?.[0] ?? null)} />
            <button className="secondary-button" type="submit" disabled={isLoading || !pdfFile} title="Upload text PDF for analysis">
              <Upload size={17} />
              Analyze PDF
            </button>
          </form>
        </section>

        <ResultPanel analysis={analysis} error={error} />
      </div>
    </main>
  );
}
