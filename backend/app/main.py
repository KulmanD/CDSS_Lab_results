from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from api.conversion import run_analysis, validate_supported_tests
from api.csv_parser import ParsedUpload, parse_csv_upload, parse_csv_upload_with_metadata
from api.history_store import delete_patient_history, get_patient_history, save_patient_history
from api.pdf_parser import parse_pdf_upload, parse_pdf_upload_with_metadata
from api.schemas import AnalyzeRequest, HistoryRecordsPayload


app = FastAPI(
    title="CDSS Lab Results API",
    version="0.1.0",
    description="Deterministic rule-based CDSS API for selected lab-result patterns.",
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


def _detect_upload_type(file: UploadFile) -> str:
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    content_type = (file.content_type or "").lower()

    if suffix == ".csv" or content_type in {"text/csv", "application/csv", "application/vnd.ms-excel"}:
        return "csv"
    if suffix == ".pdf" or content_type == "application/pdf":
        return "pdf"

    raise HTTPException(
        status_code=422,
        detail={"errors": [{"field": "file", "message": "Unsupported file type. Upload a CSV or text-based PDF."}]},
    )


def _upload_response(parsed: ParsedUpload, file_type: str) -> dict:
    response = run_analysis(parsed.payload)
    response["upload"] = {
        "file_type": file_type,
        "patient": parsed.patient_metadata,
        "current_results": [record.model_dump() for record in parsed.payload.current_results],
        "historical_results": [record.model_dump() for record in parsed.payload.historical_results],
    }
    return response


@app.post("/api/analyze")
def analyze(payload: AnalyzeRequest, use_saved_history: bool = False) -> dict:
    saved_history = []
    if use_saved_history:
        if not payload.patient.patient_id:
            raise HTTPException(
                status_code=422,
                detail={
                    "errors": [
                        {
                            "field": "patient.patient_id",
                            "message": "patient_id is required when use_saved_history is true.",
                        }
                    ]
                },
            )
        saved_history = get_patient_history(payload.patient.patient_id)
    return run_analysis(payload, additional_historical_results=saved_history)


@app.post("/api/analyze/csv")
async def analyze_csv(file: UploadFile = File(...)) -> dict:
    content = await file.read()
    payload = parse_csv_upload(content)
    return run_analysis(payload)


@app.post("/api/analyze/pdf")
async def analyze_pdf(file: UploadFile = File(...)) -> dict:
    content = await file.read()
    payload = parse_pdf_upload(content)
    return run_analysis(payload)


@app.post("/api/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)) -> dict:
    content = await file.read()
    file_type = _detect_upload_type(file)
    if file_type == "csv":
        return _upload_response(parse_csv_upload_with_metadata(content), file_type)
    return _upload_response(parse_pdf_upload_with_metadata(content), file_type)


@app.get("/api/history/{patient_id}")
def get_history(patient_id: str) -> dict:
    records = get_patient_history(patient_id)
    return {"patient_id": patient_id, "count": len(records), "records": [record.model_dump() for record in records]}


@app.post("/api/history/{patient_id}")
def save_history(patient_id: str, payload: HistoryRecordsPayload) -> dict:
    validate_supported_tests(payload.records, "records")
    records = save_patient_history(patient_id, payload.records)
    return {"patient_id": patient_id, "count": len(records), "records": [record.model_dump() for record in records]}


@app.delete("/api/history/{patient_id}")
def delete_history(patient_id: str) -> dict:
    deleted_count = delete_patient_history(patient_id)
    return {"patient_id": patient_id, "deleted_count": deleted_count}
