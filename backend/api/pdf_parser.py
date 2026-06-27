from __future__ import annotations

from io import BytesIO

from fastapi import HTTPException
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from api.csv_parser import ParsedUpload, parse_csv_upload, parse_csv_upload_with_metadata
from api.schemas import AnalyzeRequest


def extract_pdf_text(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
    except PdfReadError as exc:
        raise HTTPException(status_code=422, detail={"errors": [{"message": "PDF could not be read."}]}) from exc

    if reader.is_encrypted:
        raise HTTPException(
            status_code=422,
            detail={"errors": [{"message": "Encrypted PDFs are not supported."}]},
        )

    page_text: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            page_text.append(text)

    extracted = "\n".join(page_text).strip()
    if not extracted:
        raise HTTPException(
            status_code=422,
            detail={
                "errors": [
                    {
                        "message": "No readable text was found. Scanned/image PDFs require OCR and are not supported."
                    }
                ]
            },
        )
    return extracted


def parse_pdf_upload(file_bytes: bytes) -> AnalyzeRequest:
    text = extract_pdf_text(file_bytes)
    return parse_csv_upload(text.encode("utf-8"))


def parse_pdf_upload_with_metadata(file_bytes: bytes) -> ParsedUpload:
    text = extract_pdf_text(file_bytes)
    return parse_csv_upload_with_metadata(text.encode("utf-8"))
