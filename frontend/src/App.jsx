import { Activity, AlertTriangle, Download, History, Plus, Send, Trash2, Upload } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

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
  routine: { label: "Reassuring / Normal", className: "routine" },
  monitor: { label: "Monitor", className: "monitor" },
  prompt_review: { label: "Routine doctor follow-up", className: "prompt" },
  urgent_review: { label: "Prompt doctor follow-up", className: "urgent" }
};

const recommendationCopy = {
  routine: {
    title: "No immediate concern detected",
    explanation: "The submitted values did not cross the rule thresholds used by this prototype. Continue routine care and review questions with a clinician."
  },
  monitor: {
    title: "Keep monitoring these results",
    explanation: "One or more values or trends may be worth watching. This does not suggest an emergency, but it may be useful to review during routine care."
  },
  prompt_review: {
    title: "Doctor follow-up recommended",
    explanation: "Some values are outside expected ranges or show a meaningful trend. This is not a diagnosis, but it would be reasonable to discuss the results with a doctor."
  },
  urgent_review: {
    title: "Prompt doctor follow-up recommended",
    explanation: "Some values fall into ranges that should be reviewed promptly by a clinician. This prototype cannot diagnose a condition or decide treatment."
  }
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

function rowFromRecord(record) {
  return {
    id: crypto.randomUUID(),
    test_name: record.test_name,
    value: String(record.value),
    unit: record.unit,
    collected_at: record.collected_at
  };
}

function displayValue(value, fallback = "Not provided") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function displaySex(value) {
  if (value === "female") return "Female";
  if (value === "male") return "Male";
  if (value === "other_unknown") return "Other/unknown";
  return "Unknown";
}

function displayPregnant(value) {
  if (value === true) return "Yes";
  if (value === false) return "No";
  return "Unknown";
}

function UploadedPatientSummary({ uploadInfo }) {
  if (!uploadInfo?.patient) return null;
  const patient = uploadInfo.patient;
  return (
    <section className="patient-summary" aria-label="Uploaded patient summary">
      <div>
        <span>Patient</span>
        <strong>{displayValue(patient.patient_name ?? patient.patient_id)}</strong>
      </div>
      <div>
        <span>Age</span>
        <strong>{displayValue(patient.age, "Unknown")}</strong>
      </div>
      <div>
        <span>Sex</span>
        <strong>{displaySex(patient.sex)}</strong>
      </div>
      <div>
        <span>Date of birth</span>
        <strong>{displayValue(patient.date_of_birth)}</strong>
      </div>
      <div>
        <span>Latest lab date</span>
        <strong>{displayValue(patient.latest_collected_at)}</strong>
      </div>
      <div>
        <span>Pregnant</span>
        <strong>{displayPregnant(patient.pregnant)}</strong>
      </div>
    </section>
  );
}

function RecommendationSummary({ analysis }) {
  const meta = urgencyMeta[analysis.overall_urgency] ?? urgencyMeta.routine;
  const copy = recommendationCopy[analysis.overall_urgency] ?? recommendationCopy.routine;
  const triggeredPatterns = analysis.results
    .filter((result) => result.triggered)
    .map((result) => result.pattern)
    .join(", ");
  return (
    <section className={`recommendation-card ${meta.className}`}>
      <span className="eyebrow">Overall recommendation</span>
      <h2>{copy.title}</h2>
      <p>
        {copy.explanation}
        {triggeredPatterns ? ` The recommendation is based on ${triggeredPatterns} results.` : ""}
      </p>
    </section>
  );
}

function UrgencyScale({ urgency }) {
  const levels = [
    ["routine", "Reassuring / Normal"],
    ["monitor", "Monitor"],
    ["prompt_review", "Routine follow-up"],
    ["urgent_review", "Prompt follow-up"]
  ];
  const activeIndex = Math.max(
    0,
    levels.findIndex(([value]) => value === urgency)
  );
  return (
    <div className="urgency-scale" aria-label="Urgency scale">
      {levels.map(([value, label], index) => (
        <div className={`scale-step ${index <= activeIndex ? "active" : ""} ${value}`} key={value}>
          <span />
          <strong>{label}</strong>
        </div>
      ))}
    </div>
  );
}

function formatNumber(value) {
  if (value === null || value === undefined) return "";
  return String(Math.round(value * 100) / 100);
}

function formatAxis(value) {
  if (value === null || value === undefined) return "";
  return String(Math.abs(value) >= 10 ? Math.round(value) : Math.round(value * 10) / 10);
}

const rangePositionText = {
  below: "Below the normal range",
  within: "Within the normal range",
  above: "Above the normal range"
};

function TrendMiniLine({ chart }) {
  const points = chart.trend ?? [];
  if (points.length < 2) return null;

  const width = 280;
  const height = 64;
  const padX = 10;
  const padTop = 10;
  const padBottom = 18;
  const values = points.map((point) => point.value);
  let low = Math.min(...values);
  let high = Math.max(...values);
  if (high === low) {
    high = low + 1;
    low = low - 1;
  }
  const span = high - low;
  low -= span * 0.18;
  high += span * 0.18;

  const xAt = (index) => padX + (index / (points.length - 1)) * (width - 2 * padX);
  const yAt = (value) => padTop + (1 - (value - low) / (high - low)) * (height - padTop - padBottom);
  const linePath = points
    .map((point, index) => `${index ? "L" : "M"}${xAt(index).toFixed(1)} ${yAt(point.value).toFixed(1)}`)
    .join(" ");
  const referenceLines = [chart.reference_low, chart.reference_high]
    .filter((value) => value !== null && value !== undefined && value > low && value < high)
    .map((value) => yAt(value));
  const first = points[0];
  const last = points[points.length - 1];

  return (
    <div className="trend-mini">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${chart.display_name} trend over time`}>
        {referenceLines.map((y, index) => (
          <line key={index} className="trend-ref" x1={padX} x2={width - padX} y1={y} y2={y} />
        ))}
        <path className="trend-line" d={linePath} fill="none" />
        {points.map((point, index) => (
          <circle
            key={point.collected_at}
            className={`trend-dot ${index === points.length - 1 ? "last" : ""}`}
            cx={xAt(index)}
            cy={yAt(point.value)}
            r={index === points.length - 1 ? 4 : 3}
          />
        ))}
        <text className="trend-axis-label" x={padX} y={height - 5}>
          {first.collected_at}
        </text>
        <text className="trend-axis-label" x={width - padX} y={height - 5} textAnchor="end">
          {last.collected_at}
        </text>
      </svg>
      <div className="trend-caption">
        <span>Trend over time</span>
        <span>
          {formatNumber(first.value)} → {formatNumber(last.value)} {chart.unit}
        </span>
      </div>
    </div>
  );
}

function MarkerRangeChart({ chart }) {
  const span = chart.axis_max - chart.axis_min || 1;
  const toPercent = (value) => Math.max(0, Math.min(100, ((value - chart.axis_min) / span) * 100));
  const positionText = rangePositionText[chart.range_position] ?? "";
  const valuePercent = toPercent(chart.value);

  const outsideRange = chart.range_position !== "within";
  const elevated = chart.severity === "high" || chart.severity === "critical";
  const borderline = chart.severity === "borderline";
  const showAdvisory = outsideRange && (elevated || borderline);
  const advisoryText = elevated
    ? "Outside the typical range — worth discussing with a clinician."
    : "Near the edge of the typical range — worth keeping an eye on.";

  return (
    <div className="marker-chart">
      <div className="marker-chart-head">
        <span className="marker-name">{chart.display_name}</span>
        <span className={`marker-value sev-${chart.severity}`}>
          {formatNumber(chart.value)} {chart.unit}
        </span>
      </div>
      <div className="marker-status">
        <span className={`status-chip sev-${chart.severity}`}>{chart.band_label}</span>
        <span className="status-text">
          {positionText} · reference {chart.reference_label}
        </span>
      </div>
      <div
        className="range-track"
        role="img"
        aria-label={`${chart.display_name} ${formatNumber(chart.value)} ${chart.unit}, ${positionText}, reference ${chart.reference_label}`}
      >
        {chart.bands.map((band, index) => {
          const left = toPercent(band.lower ?? chart.axis_min);
          const right = toPercent(band.upper ?? chart.axis_max);
          return (
            <div
              key={`${band.label}-${index}`}
              className={`range-band sev-${band.severity}`}
              style={{ left: `${left}%`, width: `${Math.max(0, right - left)}%` }}
              title={band.label}
            />
          );
        })}
        <div className="value-pointer" style={{ left: `${valuePercent}%` }}>
          <span className={`value-dot sev-${chart.severity}`} />
        </div>
      </div>
      <div className="range-axis">
        <span>{formatAxis(chart.axis_min)}</span>
        <span>{formatAxis(chart.axis_max)}</span>
      </div>
      {showAdvisory ? (
        <p className={`marker-advisory sev-${chart.severity}`}>
          <AlertTriangle size={14} />
          {advisoryText}
        </p>
      ) : null}
      <TrendMiniLine chart={chart} />
    </div>
  );
}

function ResultCard({ result }) {
  const meta = urgencyMeta[result.urgency_level] ?? urgencyMeta.routine;
  const charts = result.charts ?? [];
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
      {charts.length > 0 ? (
        <section className="marker-charts">
          <h4>Your values vs. typical ranges</h4>
          {charts.map((chart) => (
            <MarkerRangeChart key={chart.test_name} chart={chart} />
          ))}
        </section>
      ) : null}
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
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    setShowDetails(false);
  }, [analysis]);

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
      <RecommendationSummary analysis={analysis} />
      <UrgencyScale urgency={analysis.overall_urgency} />
      <div className="summary-band">
        <span className={`urgency-pill ${meta.className}`}>{meta.label}</span>
      </div>
      <p className="disclaimer">{analysis.disclaimer}</p>
      <button type="button" className="secondary-button detail-toggle" onClick={() => setShowDetails((current) => !current)}>
        {showDetails ? "Hide detailed explanation" : "Show detailed explanation"}
      </button>
      {showDetails ? (
        <div className="result-stack">
          {analysis.results.map((result) => (
            <ResultCard key={result.rule_id} result={result} />
          ))}
        </div>
      ) : null}
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

const HISTORY_PREFIX = "cdss_history_v1:";

function historyKeyFor(patientId) {
  const id = patientId && patientId.trim() ? patientId.trim() : "local-session";
  return `${HISTORY_PREFIX}${id}`;
}

function loadHistory(patientId) {
  try {
    const raw = localStorage.getItem(historyKeyFor(patientId));
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function persistHistory(patientId, entries) {
  try {
    localStorage.setItem(historyKeyFor(patientId), JSON.stringify(entries.slice(-50)));
  } catch {
    // Storage unavailable or full; local history is best-effort only.
  }
}

function summarizeAnalysis(analysis, labDate) {
  const markers = [];
  (analysis.results ?? []).forEach((result) => {
    (result.charts ?? []).forEach((chart) => {
      markers.push({
        test_name: chart.test_name,
        display_name: chart.display_name,
        value: chart.value,
        unit: chart.unit,
        severity: chart.severity
      });
    });
  });
  return {
    recorded_at: new Date().toISOString(),
    lab_date: labDate || today,
    overall_urgency: analysis.overall_urgency,
    flagged: (analysis.results ?? []).filter((result) => result.triggered).map((result) => result.pattern),
    markers
  };
}

function sameEntry(a, b) {
  if (!a || !b) return false;
  if (a.lab_date !== b.lab_date || a.overall_urgency !== b.overall_urgency) return false;
  if (a.markers.length !== b.markers.length) return false;
  return a.markers.every((marker, index) => {
    const other = b.markers[index];
    return other && other.test_name === marker.test_name && other.value === marker.value;
  });
}

function appendHistory(patientId, entry) {
  const entries = loadHistory(patientId);
  if (sameEntry(entries[entries.length - 1], entry)) return entries;
  const next = [...entries, entry];
  persistHistory(patientId, next);
  return next;
}

function latestRowDate(rows) {
  const dates = rows.map((row) => row.collected_at).filter(Boolean).sort();
  return dates.length ? dates[dates.length - 1] : today;
}

function trendArrow(values) {
  if (values.length < 2) return { symbol: "", label: "single result" };
  const first = values[0];
  const last = values[values.length - 1];
  const diff = last - first;
  const epsilon = Math.abs(first) * 0.02;
  if (diff > epsilon) return { symbol: "▲", label: "rising" };
  if (diff < -epsilon) return { symbol: "▼", label: "falling" };
  return { symbol: "→", label: "stable" };
}

function Sparkline({ values, severity }) {
  if (values.length < 2) {
    return <div className="sparkline-single">single reading</div>;
  }
  const width = 200;
  const height = 40;
  const padX = 4;
  const padY = 6;
  let low = Math.min(...values);
  let high = Math.max(...values);
  if (high === low) {
    high = low + 1;
    low = low - 1;
  }
  const xAt = (index) => padX + (index / (values.length - 1)) * (width - 2 * padX);
  const yAt = (value) => padY + (1 - (value - low) / (high - low)) * (height - 2 * padY);
  const path = values.map((value, index) => `${index ? "L" : "M"}${xAt(index).toFixed(1)} ${yAt(value).toFixed(1)}`).join(" ");
  return (
    <svg className={`sparkline sev-${severity}`} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" role="img" aria-label="Values over time">
      <path className="sparkline-line" d={path} fill="none" />
    </svg>
  );
}

function HistoryDashboard({ entries, patientLabel, onClear }) {
  if (!entries.length) {
    return (
      <section className="panel history-panel">
        <div className="panel-title">
          <History size={18} />
          <h2>Your history</h2>
        </div>
        <p className="history-empty">
          No past evaluations are saved on this device yet. Each analysis you run is saved only in this browser — never sent to a
          server — so you can see how your results change over time.
        </p>
      </section>
    );
  }

  const timeline = [...entries].reverse();
  const markerOrder = [];
  const seriesByMarker = {};
  entries.forEach((entry) => {
    entry.markers.forEach((marker) => {
      if (!seriesByMarker[marker.test_name]) {
        seriesByMarker[marker.test_name] = { display_name: marker.display_name, unit: marker.unit, points: [] };
        markerOrder.push(marker.test_name);
      }
      seriesByMarker[marker.test_name].points.push({ value: marker.value, severity: marker.severity });
    });
  });

  return (
    <section className="panel history-panel">
      <div className="history-head">
        <div className="panel-title">
          <History size={18} />
          <h2>Your history</h2>
        </div>
        <div className="history-meta">
          <span>
            {patientLabel} · {entries.length} evaluation{entries.length > 1 ? "s" : ""}
          </span>
          <button type="button" className="icon-button danger" title="Clear saved history" onClick={onClear}>
            <Trash2 size={16} />
          </button>
        </div>
      </div>
      <p className="history-note">Saved only in this browser. Not sent to any server.</p>

      <div className="history-grid">
        <div className="history-timeline">
          <h4>Past evaluations</h4>
          {timeline.map((entry) => {
            const meta = urgencyMeta[entry.overall_urgency] ?? urgencyMeta.routine;
            return (
              <div className="history-row" key={entry.recorded_at}>
                <span className="history-date">{entry.lab_date}</span>
                <span className={`urgency-pill ${meta.className}`}>{meta.label}</span>
                <span className="history-flagged">{entry.flagged.length ? entry.flagged.join(", ") : "no flags"}</span>
              </div>
            );
          })}
        </div>

        <div className="history-markers">
          <h4>Markers over time</h4>
          {markerOrder.map((name) => {
            const series = seriesByMarker[name];
            const values = series.points.map((point) => point.value);
            const latest = series.points[series.points.length - 1];
            const direction = trendArrow(values);
            return (
              <div className="history-marker" key={name}>
                <div className="history-marker-head">
                  <span className="marker-name">{series.display_name}</span>
                  <span className={`marker-value sev-${latest.severity}`}>
                    {formatNumber(latest.value)} {series.unit} {direction.symbol}
                  </span>
                </div>
                <Sparkline values={values} severity={latest.severity} />
                <span className="history-marker-meta">
                  {values.length} result{values.length > 1 ? "s" : ""} · {direction.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default function App() {
  const [patient, setPatient] = useState({ patient_id: "", age: "", sex: "other_unknown", pregnant: "" });
  const [currentRows, setCurrentRows] = useState([emptyRow("hemoglobin"), emptyRow("mcv")]);
  const [historyRows, setHistoryRows] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory(loadHistory(patient.patient_id));
  }, [patient.patient_id]);

  const sampleCsv = useMemo(
    () =>
      [
        "patient_id,patient_name,date_of_birth,age,sex,test_name,value,unit,collected_at,pregnant,source_label",
        "demo-001,Alex Demo,1981-04-18,45,female,fasting_glucose,82,mg/dL,2026-04-26,false,Fasting glucose",
        "demo-001,Alex Demo,1981-04-18,45,female,fasting_glucose,90,mg/dL,2026-05-26,false,Fasting glucose",
        "demo-001,Alex Demo,1981-04-18,45,female,fasting_glucose,98,mg/dL,2026-06-26,false,Fasting glucose",
        "demo-001,Alex Demo,1981-04-18,45,female,hemoglobin,11.4,g/dL,2026-06-26,false,Hemoglobin",
        "demo-001,Alex Demo,1981-04-18,45,female,mcv,78,fL,2026-06-26,false,MCV",
        "demo-001,Alex Demo,1981-04-18,45,female,ldl,145,mg/dL,2026-06-26,false,LDL",
        "demo-001,Alex Demo,1981-04-18,45,female,crp,2.4,mg/dL,2026-06-26,false,CRP"
      ].join("\n"),
    []
  );

  function updatePatient(field, value) {
    setPatient((current) => ({ ...current, [field]: value }));
  }

  function applyUploadedData(upload) {
    if (!upload) return;
    const uploadedPatient = upload.patient ?? {};
    setUploadInfo(upload);
    setPatient({
      patient_id: uploadedPatient.patient_id ?? "",
      age: uploadedPatient.age === null || uploadedPatient.age === undefined ? "" : String(uploadedPatient.age),
      sex: uploadedPatient.sex ?? "other_unknown",
      pregnant:
        uploadedPatient.pregnant === null || uploadedPatient.pregnant === undefined
          ? ""
          : String(uploadedPatient.pregnant)
    });

    const uploadedCurrent = (upload.current_results ?? []).map(rowFromRecord);
    const uploadedHistory = (upload.historical_results ?? []).map(rowFromRecord);
    setCurrentRows(uploadedCurrent.length ? uploadedCurrent : [emptyRow("hemoglobin")]);
    setHistoryRows(uploadedHistory);
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
      const body = await parseResponse(response);
      setAnalysis(body);
      setUploadInfo(null);
      setHistory(appendHistory(patient.patient_id, summarizeAnalysis(body, latestRowDate(currentRows))));
    } catch (err) {
      setError(err.message);
      setAnalysis(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function submitUpload(event) {
    event.preventDefault();
    if (!uploadFile) return;
    setIsLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", uploadFile);
      const response = await fetch(`${API_BASE}/api/analyze/upload`, {
        method: "POST",
        body: formData
      });
      const body = await parseResponse(response);
      setAnalysis(body);
      applyUploadedData(body.upload);
      const uploadPatientId = body.upload?.patient?.patient_id ?? "";
      const labDate = body.upload?.patient?.latest_collected_at;
      setHistory(appendHistory(uploadPatientId, summarizeAnalysis(body, labDate)));
    } catch (err) {
      setError(err.message);
      setAnalysis(null);
    } finally {
      setIsLoading(false);
    }
  }

  function clearHistory() {
    try {
      localStorage.removeItem(historyKeyFor(patient.patient_id));
    } catch {
      // best-effort
    }
    setHistory([]);
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
            <UploadedPatientSummary uploadInfo={uploadInfo} />

            <RecordRows title="Current results" rows={currentRows} setRows={setCurrentRows} />
            <RecordRows title="Historical results" rows={historyRows} setRows={setHistoryRows} compact />

            <button className="primary-button" type="submit" disabled={isLoading} title="Submit manual analysis">
              <Send size={17} />
              Analyze record
            </button>
          </form>

          <form onSubmit={submitUpload} className="csv-panel">
            <div className="subhead">
              <h3>Upload lab file</h3>
              <button type="button" className="icon-button" title="Download CSV sample" onClick={downloadSampleCsv}>
                <Download size={16} />
              </button>
            </div>
            <input type="file" accept=".csv,.pdf,text/csv,application/pdf" onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)} />
            <button className="secondary-button" type="submit" disabled={isLoading || !uploadFile} title="Upload file for analysis">
              <Upload size={17} />
              Analyze upload
            </button>
          </form>
        </section>

        <ResultPanel analysis={analysis} error={error} />
      </div>

      <HistoryDashboard
        entries={history}
        patientLabel={patient.patient_id && patient.patient_id.trim() ? patient.patient_id.trim() : "This device"}
        onClear={clearHistory}
      />
    </main>
  );
}
