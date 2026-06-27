from __future__ import annotations

from fastapi import HTTPException

from api.schemas import AnalyzeRequest, LabRecordPayload, PatientPayload
from cdss_core import LabRecord, PatientDemographics, analyze_lab_results
from cdss_core.normalization import normalize_test_name


SUPPORTED_TESTS = {
    "hemoglobin",
    "mcv",
    "fasting_glucose",
    "hba1c",
    "creatinine",
    "egfr",
    "total_cholesterol",
    "ldl",
    "hdl",
    "triglycerides",
    "vldl",
    "crp",
}


def validate_supported_tests(records: list[LabRecordPayload], field_prefix: str) -> None:
    errors = []
    for index, record in enumerate(records):
        normalized = normalize_test_name(record.test_name)
        if normalized not in SUPPORTED_TESTS:
            errors.append(
                {
                    "field": f"{field_prefix}[{index}].test_name",
                    "message": f"Unsupported test_name '{record.test_name}'. Supported tests: {', '.join(sorted(SUPPORTED_TESTS))}.",
                }
            )
    if errors:
        raise HTTPException(status_code=422, detail={"errors": errors})


def to_core_patient(patient: PatientPayload) -> PatientDemographics:
    return PatientDemographics(
        patient_id=patient.patient_id,
        age=patient.age,
        sex=patient.sex,
        pregnant=patient.pregnant,
    )


def to_core_record(record: LabRecordPayload) -> LabRecord:
    return LabRecord(
        test_name=record.test_name,
        value=record.value,
        unit=record.unit,
        collected_at=record.collected_at,
        source_label=record.source_label,
        reference_min=record.reference_min,
        reference_max=record.reference_max,
    )


def run_analysis(payload: AnalyzeRequest, additional_historical_results: list[LabRecordPayload] | None = None) -> dict:
    validate_supported_tests(payload.current_results, "current_results")
    historical_results = [*payload.historical_results, *(additional_historical_results or [])]
    validate_supported_tests(historical_results, "historical_results")

    response = analyze_lab_results(
        patient=to_core_patient(payload.patient),
        current_results=[to_core_record(record) for record in payload.current_results],
        historical_results=[to_core_record(record) for record in historical_results],
    )
    return response.to_dict()
