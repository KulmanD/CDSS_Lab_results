from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from cdss_core.models import LabRecord
from cdss_core.normalization import normalize_test_name


SIGNIFICANT_PERCENT_CHANGE: dict[str, float] = {
    "hemoglobin": 10.0,
    "egfr": 20.0,
    "creatinine": 20.0,
}


@dataclass(frozen=True)
class TrendResult:
    test_name: str
    previous_value: float | None
    current_value: float
    percent_change: float | None
    significant: bool
    message: str


def _date_key(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.min


def most_recent_previous(
    test_name: str,
    current_record: LabRecord,
    historical_records: Iterable[LabRecord],
) -> LabRecord | None:
    normalized = normalize_test_name(test_name)
    candidates = [
        record
        for record in historical_records
        if normalize_test_name(record.test_name) == normalized
        and _date_key(record.collected_at) < _date_key(current_record.collected_at)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda record: _date_key(record.collected_at))


def calculate_trend(
    test_name: str,
    current_record: LabRecord,
    historical_records: Iterable[LabRecord],
) -> TrendResult:
    normalized = normalize_test_name(test_name)
    previous = most_recent_previous(normalized, current_record, historical_records)
    if previous is None:
        return TrendResult(
            test_name=normalized,
            previous_value=None,
            current_value=current_record.value,
            percent_change=None,
            significant=False,
            message="Trend analysis skipped because no previous value was provided.",
        )
    if previous.value == 0:
        return TrendResult(
            test_name=normalized,
            previous_value=previous.value,
            current_value=current_record.value,
            percent_change=None,
            significant=False,
            message="Trend analysis skipped because the previous value is zero.",
        )

    percent_change = ((current_record.value - previous.value) / previous.value) * 100.0
    threshold = SIGNIFICANT_PERCENT_CHANGE.get(normalized)
    significant = threshold is not None and abs(percent_change) >= threshold
    if threshold is None:
        message = "No MVP trend threshold is defined for this marker."
    elif significant:
        message = f"Change of {percent_change:.1f}% meets the {threshold:.1f}% trend threshold."
    else:
        message = f"Change of {percent_change:.1f}% does not meet the {threshold:.1f}% trend threshold."

    return TrendResult(
        test_name=normalized,
        previous_value=previous.value,
        current_value=current_record.value,
        percent_change=percent_change,
        significant=significant,
        message=message,
    )
