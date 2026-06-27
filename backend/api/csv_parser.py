from __future__ import annotations

import csv
from io import StringIO
from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError

from api.conversion import SUPPORTED_TESTS
from api.schemas import AnalyzeRequest, LabRecordPayload, PatientPayload
from cdss_core.normalization import normalize_test_name


REQUIRED_COLUMNS = {
    "patient_id",
    "age",
    "sex",
    "test_name",
    "value",
    "unit",
    "collected_at",
}

OPTIONAL_COLUMNS = {
    "pregnant",
    "reference_min",
    "reference_max",
    "source_label",
}


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _parse_optional_float(value: str | None, row_number: int, field: str, errors: list[dict[str, Any]]) -> float | None:
    value = _blank_to_none(value)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        errors.append({"row": row_number, "field": field, "message": f"{field} must be numeric."})
        return None


def _parse_bool(value: str | None, row_number: int, errors: list[dict[str, Any]]) -> bool | None:
    value = _blank_to_none(value)
    if value is None:
        return None
    lowered = value.lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    errors.append({"row": row_number, "field": "pregnant", "message": "pregnant must be true, false, or blank."})
    return None


def _validation_errors_to_rows(row_number: int, exc: ValidationError) -> list[dict[str, Any]]:
    errors = []
    for err in exc.errors():
        field = ".".join(str(part) for part in err.get("loc", []))
        errors.append({"row": row_number, "field": field, "message": err.get("msg", "Invalid value.")})
    return errors


def parse_csv_upload(file_bytes: bytes) -> AnalyzeRequest:
    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=422, detail={"errors": [{"message": "CSV must be UTF-8 encoded."}]}) from exc

    reader = csv.DictReader(StringIO(text))
    fieldnames = set(reader.fieldnames or [])
    missing = sorted(REQUIRED_COLUMNS - fieldnames)
    if missing:
        raise HTTPException(
            status_code=422,
            detail={"errors": [{"field": "header", "message": f"Missing required columns: {', '.join(missing)}."}]},
        )

    records: list[LabRecordPayload] = []
    errors: list[dict[str, Any]] = []
    patient_data: dict[str, Any] | None = None
    patient_identity: tuple[str | None, str, str, bool | None] | None = None

    for row_index, row in enumerate(reader, start=2):
        for column in REQUIRED_COLUMNS:
            if _blank_to_none(row.get(column)) is None:
                errors.append({"row": row_index, "field": column, "message": f"{column} is required."})

        pregnant = _parse_bool(row.get("pregnant"), row_index, errors)
        row_patient_identity = (
            _blank_to_none(row.get("patient_id")),
            _blank_to_none(row.get("age")) or "",
            (_blank_to_none(row.get("sex")) or "").lower(),
            pregnant,
        )
        if patient_identity is None:
            patient_identity = row_patient_identity
            try:
                patient_data = PatientPayload(
                    patient_id=row_patient_identity[0],
                    age=int(row_patient_identity[1]),
                    sex=row_patient_identity[2],
                    pregnant=pregnant,
                ).model_dump()
            except (ValueError, ValidationError) as exc:
                if isinstance(exc, ValidationError):
                    errors.extend(_validation_errors_to_rows(row_index, exc))
                else:
                    errors.append({"row": row_index, "field": "age", "message": "age must be an integer."})
        elif row_patient_identity != patient_identity:
            errors.append(
                {
                    "row": row_index,
                    "field": "patient",
                    "message": "All rows in one upload must describe the same patient demographics.",
                }
            )

        value_text = _blank_to_none(row.get("value"))
        try:
            value = float(value_text) if value_text is not None else 0.0
        except ValueError:
            errors.append({"row": row_index, "field": "value", "message": "value must be numeric."})
            value = 0.0

        test_name = _blank_to_none(row.get("test_name")) or ""
        normalized = normalize_test_name(test_name)
        if test_name and normalized not in SUPPORTED_TESTS:
            errors.append(
                {
                    "row": row_index,
                    "field": "test_name",
                    "message": f"Unsupported test_name '{test_name}'. Supported tests: {', '.join(sorted(SUPPORTED_TESTS))}.",
                }
            )

        try:
            records.append(
                LabRecordPayload(
                    test_name=test_name,
                    value=value,
                    unit=_blank_to_none(row.get("unit")) or "",
                    collected_at=_blank_to_none(row.get("collected_at")) or "",
                    source_label=_blank_to_none(row.get("source_label")) or test_name,
                    reference_min=_parse_optional_float(row.get("reference_min"), row_index, "reference_min", errors),
                    reference_max=_parse_optional_float(row.get("reference_max"), row_index, "reference_max", errors),
                )
            )
        except ValidationError as exc:
            errors.extend(_validation_errors_to_rows(row_index, exc))

    if not records and not errors:
        errors.append({"field": "body", "message": "CSV contains no data rows."})

    if errors or patient_data is None:
        raise HTTPException(status_code=422, detail={"errors": errors})

    return AnalyzeRequest(patient=PatientPayload(**patient_data), current_results=records, historical_results=[])
