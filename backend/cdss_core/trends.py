"""Deterministic trend analysis.

A single least-squares engine evaluates whether a patient's repeated
results for one marker are moving in a clinically adverse direction. It
replaces the earlier per-marker logic with one approach that is:

- direction-aware: only a move in the marker's adverse direction can flag,
  so an *improving* value never raises an alert;
- tolerant of noise: a straight line is fit through all dated points, so a
  single dip no longer hides a real trend, and an R^2 gate keeps scattered
  results from triggering;
- multi-point: any number of dated results at or above the per-marker
  minimum is supported.

All thresholds live in ``TREND_CONFIG`` and are intended to be documented in
``docs/thresholds.md`` and reviewed before any clinical use.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from cdss_core.models import LabRecord
from cdss_core.normalization import normalize_test_name


@dataclass(frozen=True)
class TrendConfig:
    adverse: str  # "rising" | "falling": the direction that is clinically concerning
    min_points: int
    min_span_days: int
    pct_threshold: float
    abs_threshold: float | None
    r2_min: float


# Per-marker trend configuration. Percentage thresholds match the values the
# MVP used previously (hemoglobin 10%, eGFR/creatinine 20%, fasting glucose
# 10% or a 10 mg/dL absolute rise); the regression, direction-awareness, and
# R^2 gate are the additions.
TREND_CONFIG: dict[str, TrendConfig] = {
    "hemoglobin": TrendConfig("falling", min_points=2, min_span_days=21, pct_threshold=10.0, abs_threshold=None, r2_min=0.5),
    "egfr": TrendConfig("falling", min_points=2, min_span_days=30, pct_threshold=20.0, abs_threshold=None, r2_min=0.5),
    "creatinine": TrendConfig("rising", min_points=2, min_span_days=30, pct_threshold=20.0, abs_threshold=None, r2_min=0.5),
    "fasting_glucose": TrendConfig("rising", min_points=3, min_span_days=21, pct_threshold=10.0, abs_threshold=10.0, r2_min=0.5),
}

DISPLAY_NAMES: dict[str, str] = {
    "hemoglobin": "Hemoglobin",
    "egfr": "eGFR",
    "creatinine": "Creatinine",
    "fasting_glucose": "Fasting glucose",
}


@dataclass(frozen=True)
class TrendResult:
    test_name: str
    previous_value: float | None  # first value in the window
    current_value: float  # latest value
    percent_change: float | None  # modelled change across the window, % of the first value
    direction: str  # rising | falling | flat | none
    slope_per_30d: float | None  # modelled change per 30 days
    projected_change: float | None  # modelled change across the full window
    r_squared: float | None
    n_points: int
    span_days: int
    confidence: str  # clear | possible | noisy | insufficient
    significant: bool
    message: str


def _date_key(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.min


def _series(normalized: str, current_record: LabRecord, history: list[LabRecord]) -> list[tuple[str, float]]:
    """Dated points for the marker (history + current), de-duped by date,
    oldest first. Records without a parseable date are dropped."""
    records = [record for record in history if normalize_test_name(record.test_name) == normalized]
    records.append(current_record)
    by_date: dict[str, float] = {}
    for record in records:
        if _date_key(record.collected_at) == date.min:
            continue
        by_date[record.collected_at] = record.value  # later insert (current) wins on a tie
    return sorted(by_date.items(), key=lambda pair: _date_key(pair[0]))


def calculate_trend(
    test_name: str,
    current_record: LabRecord,
    historical_records: Iterable[LabRecord],
) -> TrendResult:
    normalized = normalize_test_name(test_name)
    config = TREND_CONFIG.get(normalized)
    label = DISPLAY_NAMES.get(normalized, normalized)
    points = _series(normalized, current_record, list(historical_records))
    current_value = current_record.value

    def insufficient(message: str) -> TrendResult:
        return TrendResult(
            test_name=normalized,
            previous_value=None,
            current_value=current_value,
            percent_change=None,
            direction="none",
            slope_per_30d=None,
            projected_change=None,
            r_squared=None,
            n_points=len(points),
            span_days=0,
            confidence="insufficient",
            significant=False,
            message=message,
        )

    if config is None:
        return insufficient("No MVP trend threshold is defined for this marker.")
    if len(points) < config.min_points:
        if len(points) < 2:
            return insufficient("Trend analysis skipped because no previous value was provided.")
        return insufficient(f"Trend analysis needs at least {config.min_points} dated {label} results for this patient.")

    dates = [_date_key(day) for day, _ in points]
    values = [value for _, value in points]
    span_days = (dates[-1] - dates[0]).days
    if span_days < config.min_span_days:
        return insufficient(f"Trend analysis needs {label} results spanning at least {config.min_span_days} days.")

    offsets = [(day - dates[0]).days for day in dates]
    n = len(points)
    mean_t = sum(offsets) / n
    mean_v = sum(values) / n
    sum_tt = sum((t - mean_t) ** 2 for t in offsets)
    if sum_tt == 0:
        return insufficient("Trend analysis skipped because all results share one date.")

    slope = sum((t - mean_t) * (v - mean_v) for t, v in zip(offsets, values)) / sum_tt
    intercept = mean_v - slope * mean_t
    ss_tot = sum((v - mean_v) ** 2 for v in values)
    ss_res = sum((v - (slope * t + intercept)) ** 2 for t, v in zip(offsets, values))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0

    projected = slope * span_days
    first = values[0]
    percent = (projected / first * 100) if first else 0.0
    direction = "rising" if slope > 0 else "falling" if slope < 0 else "flat"
    adverse = direction == config.adverse
    strong = abs(percent) >= config.pct_threshold or (
        config.abs_threshold is not None and abs(projected) >= config.abs_threshold
    )
    consistent = r_squared >= config.r2_min
    significant = adverse and strong and consistent
    confidence = "clear" if r_squared >= 0.8 else "possible" if consistent else "noisy"

    if significant:
        message = f"{label} is {direction} and meets the MVP trend threshold ({percent:+.1f}% over {span_days} days, {confidence} fit)."
    elif adverse and strong and not consistent:
        message = f"{label} appears to be {direction} ({percent:+.1f}% over {span_days} days) but the results are too scattered to confirm a trend."
    elif adverse and not strong:
        message = f"{label} change of {percent:+.1f}% over {span_days} days does not meet the MVP trend threshold."
    else:
        message = f"{label} is not on an adverse trend ({percent:+.1f}% over {span_days} days)."

    return TrendResult(
        test_name=normalized,
        previous_value=first,
        current_value=current_value,
        percent_change=percent,
        direction=direction,
        slope_per_30d=slope * 30,
        projected_change=projected,
        r_squared=r_squared,
        n_points=n,
        span_days=span_days,
        confidence=confidence,
        significant=significant,
        message=message,
    )
