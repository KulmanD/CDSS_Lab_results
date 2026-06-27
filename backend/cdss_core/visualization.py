"""Deterministic chart data for rule results.

This module turns the same threshold constants the rules use (see
``cdss_core/thresholds.py`` / ``docs/thresholds.md``) into structured,
numeric data the frontend can render as a value-vs-reference-range chart
and an optional trend line. No medical classification happens here beyond
locating a value inside its already-documented reference bands, so the
frontend never has to embed thresholds or classify values itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from cdss_core.models import LabRecord, PatientDemographics
from cdss_core.normalization import normalize_test_name
from cdss_core.thresholds import (
    CRP_MARKED_MIN,
    CRP_MODERATE_MIN,
    CRP_NORMAL_MAX,
    CRP_SEVERE_MIN,
    FASTING_GLUCOSE_DIABETES_MIN,
    FASTING_GLUCOSE_LOW,
    FASTING_GLUCOSE_NORMAL_MAX,
    HBA1C_DIABETES_MIN,
    HBA1C_NORMAL_MAX,
    LDL_BORDERLINE_HIGH_MIN,
    LDL_HIGH_MIN,
    LDL_OPTIMAL_MAX,
    LDL_VERY_HIGH_MIN,
    MCV_MACROCYTIC_MIN,
    MCV_MICROCYTIC_MAX,
    TOTAL_CHOLESTEROL_DESIRABLE_MAX,
    TOTAL_CHOLESTEROL_HIGH_MIN,
    TRIGLYCERIDES_HIGH_MIN,
    TRIGLYCERIDES_NORMAL_MAX,
    TRIGLYCERIDES_SEVERE_MIN,
    VLDL_HIGH_MIN,
    creatinine_range,
    hemoglobin_high_threshold,
    hemoglobin_threshold,
)

# eGFR Stage I lower bound is applied as a literal in the kidney rule
# (`value < 90`); there is no named constant, so it is mirrored here.
EGFR_NORMAL_MIN = 90.0
EGFR_STAGE_2_MIN = 60.0
EGFR_STAGE_3_MIN = 30.0
EGFR_STAGE_4_MIN = 15.0


DISPLAY_NAMES: dict[str, str] = {
    "hemoglobin": "Hemoglobin",
    "mcv": "MCV",
    "fasting_glucose": "Fasting glucose",
    "hba1c": "HbA1c",
    "creatinine": "Creatinine",
    "egfr": "eGFR",
    "total_cholesterol": "Total cholesterol",
    "ldl": "LDL",
    "hdl": "HDL",
    "triglycerides": "Triglycerides",
    "vldl": "VLDL",
    "crp": "CRP",
}

# Comfortable default axis ranges per marker so the normal band stays
# readable. The axis is widened at build time if the patient's value falls
# outside these bounds.
NOMINAL_AXIS: dict[str, tuple[float, float]] = {
    "hemoglobin": (7.0, 18.0),
    "mcv": (60.0, 120.0),
    "fasting_glucose": (50.0, 180.0),
    "hba1c": (4.0, 10.0),
    "creatinine": (0.2, 2.0),
    "egfr": (0.0, 120.0),
    "total_cholesterol": (120.0, 300.0),
    "ldl": (40.0, 220.0),
    "hdl": (20.0, 90.0),
    "triglycerides": (50.0, 300.0),
    "vldl": (0.0, 60.0),
    "crp": (0.0, 12.0),
}

# Which markers each rule visualises.
RULE_MARKERS: dict[str, list[str]] = {
    "anemia_hgb_mcv": ["hemoglobin", "mcv"],
    "glucose_fpg_hba1c": ["fasting_glucose", "hba1c"],
    "kidney_egfr_creatinine": ["egfr", "creatinine"],
    "lipid_panel": ["total_cholesterol", "ldl", "hdl", "triglycerides", "vldl"],
    "inflammation_crp": ["crp"],
}


@dataclass(frozen=True)
class TrendPoint:
    collected_at: str
    value: float


@dataclass(frozen=True)
class MarkerBand:
    label: str
    lower: float | None  # inclusive lower edge; None means open-ended below
    upper: float | None  # exclusive upper edge; None means open-ended above
    severity: str  # normal | borderline | high | critical


@dataclass(frozen=True)
class MarkerChart:
    test_name: str
    display_name: str
    value: float
    unit: str
    axis_min: float
    axis_max: float
    reference_low: float | None
    reference_high: float | None
    reference_label: str
    band_label: str
    range_position: str  # below | within | above
    severity: str
    bands: list[MarkerBand]
    trend: list[TrendPoint]


def _band(label: str, lower: float | None, upper: float | None, severity: str) -> MarkerBand:
    return MarkerBand(label=label, lower=lower, upper=upper, severity=severity)


def _bands_for(normalized: str, patient: PatientDemographics) -> tuple[list[MarkerBand], float | None, float | None]:
    """Return (bands_low_to_high, reference_low, reference_high) for a marker.

    ``reference_low``/``reference_high`` describe the normal/desirable band
    used for the simple range bracket; either may be ``None`` for a
    one-sided marker (e.g. "desirable when below X", "normal when at or
    above X").
    """
    if normalized == "hemoglobin":
        threshold = hemoglobin_threshold(patient)[0].value
        high = hemoglobin_high_threshold(patient)[0].value
        return (
            [
                _band("Low", None, threshold, "high"),
                _band("Normal", threshold, high, "normal"),
                _band("High", high, None, "high"),
            ],
            threshold,
            high,
        )
    if normalized == "mcv":
        low = MCV_MICROCYTIC_MAX.value
        high = MCV_MACROCYTIC_MIN.value
        return (
            [
                _band("Low (microcytic)", None, low, "borderline"),
                _band("Normal", low, high, "normal"),
                _band("High (macrocytic)", high, None, "borderline"),
            ],
            low,
            high,
        )
    if normalized == "fasting_glucose":
        return (
            [
                _band("Low", None, FASTING_GLUCOSE_LOW.value, "high"),
                _band("Normal", FASTING_GLUCOSE_LOW.value, FASTING_GLUCOSE_NORMAL_MAX.value, "normal"),
                _band("Prediabetes range", FASTING_GLUCOSE_NORMAL_MAX.value, FASTING_GLUCOSE_DIABETES_MIN.value, "borderline"),
                _band("Diabetes range", FASTING_GLUCOSE_DIABETES_MIN.value, None, "high"),
            ],
            FASTING_GLUCOSE_LOW.value,
            FASTING_GLUCOSE_NORMAL_MAX.value,
        )
    if normalized == "hba1c":
        return (
            [
                _band("Normal", None, HBA1C_NORMAL_MAX.value, "normal"),
                _band("Prediabetes range", HBA1C_NORMAL_MAX.value, HBA1C_DIABETES_MIN.value, "borderline"),
                _band("Diabetes range", HBA1C_DIABETES_MIN.value, None, "high"),
            ],
            None,
            HBA1C_NORMAL_MAX.value,
        )
    if normalized == "creatinine":
        lower, upper, _ = creatinine_range(patient)
        return (
            [
                _band("Low", None, lower.value, "borderline"),
                _band("Normal", lower.value, upper.value, "normal"),
                _band("High", upper.value, None, "high"),
            ],
            lower.value,
            upper.value,
        )
    if normalized == "egfr":
        return (
            [
                _band("Kidney failure (Stage V)", None, EGFR_STAGE_4_MIN, "critical"),
                _band("Severely reduced (Stage IV)", EGFR_STAGE_4_MIN, EGFR_STAGE_3_MIN, "critical"),
                _band("Moderately reduced (Stage III)", EGFR_STAGE_3_MIN, EGFR_STAGE_2_MIN, "high"),
                _band("Mildly reduced (Stage II)", EGFR_STAGE_2_MIN, EGFR_NORMAL_MIN, "borderline"),
                _band("Normal (Stage I)", EGFR_NORMAL_MIN, None, "normal"),
            ],
            EGFR_NORMAL_MIN,
            None,
        )
    if normalized == "total_cholesterol":
        return (
            [
                _band("Desirable", None, TOTAL_CHOLESTEROL_DESIRABLE_MAX.value, "normal"),
                _band("Borderline high", TOTAL_CHOLESTEROL_DESIRABLE_MAX.value, TOTAL_CHOLESTEROL_HIGH_MIN.value, "borderline"),
                _band("High", TOTAL_CHOLESTEROL_HIGH_MIN.value, None, "high"),
            ],
            None,
            TOTAL_CHOLESTEROL_DESIRABLE_MAX.value,
        )
    if normalized == "ldl":
        return (
            [
                _band("Optimal", None, LDL_OPTIMAL_MAX.value, "normal"),
                _band("Near optimal", LDL_OPTIMAL_MAX.value, LDL_BORDERLINE_HIGH_MIN.value, "normal"),
                _band("Borderline high", LDL_BORDERLINE_HIGH_MIN.value, LDL_HIGH_MIN.value, "borderline"),
                _band("High", LDL_HIGH_MIN.value, LDL_VERY_HIGH_MIN.value, "high"),
                _band("Very high", LDL_VERY_HIGH_MIN.value, None, "critical"),
            ],
            None,
            LDL_OPTIMAL_MAX.value,
        )
    if normalized == "hdl":
        # Mirror the rule's actual threshold selection (see lipids.py).
        if patient.sex == "female":
            from cdss_core.thresholds import HDL_LOW_FEMALE

            threshold = HDL_LOW_FEMALE.value
        else:
            from cdss_core.thresholds import HDL_LOW_MALE

            threshold = HDL_LOW_MALE.value
        return (
            [_band("Low", None, threshold, "high"), _band("Healthy", threshold, None, "normal")],
            threshold,
            None,
        )
    if normalized == "triglycerides":
        return (
            [
                _band("Normal", None, TRIGLYCERIDES_NORMAL_MAX.value, "normal"),
                _band("Borderline high", TRIGLYCERIDES_NORMAL_MAX.value, TRIGLYCERIDES_HIGH_MIN.value, "borderline"),
                _band("High", TRIGLYCERIDES_HIGH_MIN.value, TRIGLYCERIDES_SEVERE_MIN.value, "high"),
                _band("Very high", TRIGLYCERIDES_SEVERE_MIN.value, None, "critical"),
            ],
            None,
            TRIGLYCERIDES_NORMAL_MAX.value,
        )
    if normalized == "vldl":
        return (
            [
                _band("Usual range", None, VLDL_HIGH_MIN.value, "normal"),
                _band("Above usual range", VLDL_HIGH_MIN.value, None, "borderline"),
            ],
            None,
            VLDL_HIGH_MIN.value,
        )
    if normalized == "crp":
        return (
            [
                _band("Normal", None, CRP_NORMAL_MAX.value, "normal"),
                _band("Near upper reference", CRP_NORMAL_MAX.value, CRP_MODERATE_MIN.value, "borderline"),
                _band("Moderate elevation", CRP_MODERATE_MIN.value, CRP_MARKED_MIN.value, "high"),
                _band("Marked elevation", CRP_MARKED_MIN.value, CRP_SEVERE_MIN.value, "high"),
                _band("Severe elevation", CRP_SEVERE_MIN.value, None, "critical"),
            ],
            None,
            CRP_NORMAL_MAX.value,
        )
    return ([], None, None)


def _format_number(value: float) -> str:
    return f"{value:g}"


def _reference_label(reference_low: float | None, reference_high: float | None, unit: str) -> str:
    unit_suffix = f" {unit}".rstrip()
    if reference_low is not None and reference_high is not None:
        return f"{_format_number(reference_low)}–{_format_number(reference_high)}{unit_suffix}"
    if reference_high is not None:
        return f"< {_format_number(reference_high)}{unit_suffix}"
    if reference_low is not None:
        return f"≥ {_format_number(reference_low)}{unit_suffix}"
    return "No reference range"


def _band_for_value(bands: list[MarkerBand], value: float) -> MarkerBand | None:
    for band in bands:
        lower_ok = band.lower is None or value >= band.lower
        upper_ok = band.upper is None or value < band.upper
        if lower_ok and upper_ok:
            return band
    return None


def _range_position(value: float, reference_low: float | None, reference_high: float | None) -> str:
    if reference_low is not None and value < reference_low:
        return "below"
    if reference_high is not None and value >= reference_high:
        return "above"
    return "within"


def _axis_bounds(normalized: str, value: float, bands: list[MarkerBand]) -> tuple[float, float]:
    nominal_min, nominal_max = NOMINAL_AXIS.get(normalized, (0.0, max(value, 1.0)))
    low = min(nominal_min, value)
    high = max(nominal_max, value)
    if high <= low:
        high = low + 1.0
    padding = (high - low) * 0.06
    low = max(0.0, low - padding)
    high = high + padding
    return low, high


def _date_key(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.min


def _trend_points(normalized: str, record: LabRecord, history: list[LabRecord]) -> list[TrendPoint]:
    candidates = [record, *[item for item in history if normalize_test_name(item.test_name) == normalized]]
    by_date: dict[str, float] = {}
    for item in candidates:
        if _date_key(item.collected_at) == date.min:
            continue  # skip unparseable dates so the line stays meaningful
        by_date[item.collected_at] = item.value
    if len(by_date) < 2:
        return []
    ordered = sorted(by_date.items(), key=lambda pair: _date_key(pair[0]))
    return [TrendPoint(collected_at=collected_at, value=value) for collected_at, value in ordered]


def build_marker_chart(
    normalized: str,
    record: LabRecord,
    patient: PatientDemographics,
    history: list[LabRecord],
) -> MarkerChart | None:
    bands, reference_low, reference_high = _bands_for(normalized, patient)
    if not bands:
        return None

    value = record.value
    unit = record.unit
    axis_min, axis_max = _axis_bounds(normalized, value, bands)
    band = _band_for_value(bands, value)

    return MarkerChart(
        test_name=normalized,
        display_name=DISPLAY_NAMES.get(normalized, normalized),
        value=value,
        unit=unit,
        axis_min=axis_min,
        axis_max=axis_max,
        reference_low=reference_low,
        reference_high=reference_high,
        reference_label=_reference_label(reference_low, reference_high, unit),
        band_label=band.label if band else "Unknown",
        range_position=_range_position(value, reference_low, reference_high),
        severity=band.severity if band else "normal",
        bands=bands,
        trend=_trend_points(normalized, record, history),
    )


def build_charts_for_rule(
    rule_id: str,
    patient: PatientDemographics,
    current: dict[str, LabRecord],
    history: list[LabRecord],
) -> list[MarkerChart]:
    charts: list[MarkerChart] = []
    for marker in RULE_MARKERS.get(rule_id, []):
        record = current.get(marker)
        if record is None:
            continue
        chart = build_marker_chart(marker, record, patient, history)
        if chart is not None:
            charts.append(chart)
    return charts
