from __future__ import annotations

from collections.abc import Iterable

from cdss_core.models import LabRecord


TEST_NAME_ALIASES: dict[str, str] = {
    "hb": "hemoglobin",
    "hgb": "hemoglobin",
    "haemoglobin": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "mcv": "mcv",
    "mean corpuscular volume": "mcv",
    "fasting glucose": "fasting_glucose",
    "fasting blood glucose": "fasting_glucose",
    "fasting plasma glucose": "fasting_glucose",
    "fpg": "fasting_glucose",
    "glucose": "fasting_glucose",
    "hba1c": "hba1c",
    "hb a1c": "hba1c",
    "glycated hemoglobin": "hba1c",
    "glycated haemoglobin": "hba1c",
    "creatinine": "creatinine",
    "serum creatinine": "creatinine",
    "egfr": "egfr",
    "e gfr": "egfr",
    "estimated glomerular filtration rate": "egfr",
}


def clean_test_name(test_name: str) -> str:
    return " ".join(test_name.strip().lower().replace("_", " ").split())


def normalize_test_name(test_name: str) -> str:
    cleaned = clean_test_name(test_name)
    return TEST_NAME_ALIASES.get(cleaned, cleaned.replace(" ", "_"))


def records_by_test_name(records: Iterable[LabRecord]) -> dict[str, LabRecord]:
    mapped: dict[str, LabRecord] = {}
    for record in records:
        mapped[normalize_test_name(record.test_name)] = record
    return mapped
