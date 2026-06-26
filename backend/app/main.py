from __future__ import annotations

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from api.conversion import run_analysis
from api.csv_parser import parse_csv_upload
from api.schemas import AnalyzeRequest


app = FastAPI(
    title="CDSS Lab Results API",
    version="0.1.0",
    description="Deterministic rule-based CDSS API for the lab-results MVP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "cdss-lab-results"}


@app.post("/api/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    return run_analysis(payload)


@app.post("/api/analyze/csv")
async def analyze_csv(file: UploadFile = File(...)) -> dict:
    content = await file.read()
    payload = parse_csv_upload(content)
    return run_analysis(payload)
