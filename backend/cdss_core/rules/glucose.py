from __future__ import annotations

from cdss_core.models import LabRecord, RuleResult
from cdss_core.thresholds import (
    FASTING_GLUCOSE_CRITICAL_HIGH,
    FASTING_GLUCOSE_CRITICAL_LOW,
    FASTING_GLUCOSE_DIABETES_MIN,
    FASTING_GLUCOSE_LOW,
    FASTING_GLUCOSE_NORMAL_MAX,
    HBA1C_DIABETES_MIN,
    HBA1C_NORMAL_MAX,
)
from cdss_core.trends import calculate_trend


def _fasting_glucose_status(record: LabRecord) -> tuple[str, str]:
    value = record.value
    if value < FASTING_GLUCOSE_CRITICAL_LOW.value:
        return "critical_low", f"fasting glucose {value:g} {record.unit} is below the critical level {FASTING_GLUCOSE_CRITICAL_LOW.value:g} {FASTING_GLUCOSE_CRITICAL_LOW.unit}"
    if value < FASTING_GLUCOSE_LOW.value:
        return "low", f"fasting glucose {value:g} {record.unit} is below {FASTING_GLUCOSE_LOW.value:g} {FASTING_GLUCOSE_LOW.unit}"
    if value < FASTING_GLUCOSE_NORMAL_MAX.value:
        return "normal", f"fasting glucose {value:g} {record.unit} is below {FASTING_GLUCOSE_NORMAL_MAX.value:g} {FASTING_GLUCOSE_NORMAL_MAX.unit}"
    if value < FASTING_GLUCOSE_DIABETES_MIN.value:
        return "prediabetes_risk", f"fasting glucose {value:g} {record.unit} is between 100 and 125 mg/dL"
    if value < FASTING_GLUCOSE_CRITICAL_HIGH.value:
        return "diabetes_range", f"fasting glucose {value:g} {record.unit} is at or above {FASTING_GLUCOSE_DIABETES_MIN.value:g} {FASTING_GLUCOSE_DIABETES_MIN.unit}"
    return "critical_high", f"fasting glucose {value:g} {record.unit} is at or above the critical level {FASTING_GLUCOSE_CRITICAL_HIGH.value:g} {FASTING_GLUCOSE_CRITICAL_HIGH.unit}"


def _hba1c_status(record: LabRecord) -> tuple[str, str]:
    value = record.value
    if value < HBA1C_NORMAL_MAX.value:
        return "normal", f"HbA1c {value:g}{record.unit} is below {HBA1C_NORMAL_MAX.value:g}%"
    if value < HBA1C_DIABETES_MIN.value:
        return "prediabetes_risk", f"HbA1c {value:g}{record.unit} is between 5.7% and 6.4%"
    return "diabetes_range", f"HbA1c {value:g}{record.unit} is at or above {HBA1C_DIABETES_MIN.value:g}%"


def evaluate_glucose(current: dict[str, LabRecord], history: list[LabRecord] | None = None) -> RuleResult | None:
    fasting_glucose = current.get("fasting_glucose")
    hba1c = current.get("hba1c")
    if fasting_glucose is None and hba1c is None:
        return None

    evidence: list[str] = []
    limitations = [
        "This rule does not diagnose diabetes or hypoglycemia.",
        "Diabetes-range values usually require repeat confirmation and clinical context.",
    ]
    statuses: list[str] = []

    if fasting_glucose is not None:
        status, status_evidence = _fasting_glucose_status(fasting_glucose)
        statuses.append(status)
        evidence.append(status_evidence)
        trend = calculate_trend("fasting_glucose", fasting_glucose, history or [])
        if trend.significant:
            statuses.append("rising_trend")
            evidence.append(trend.message)
        else:
            limitations.append(trend.message)
    else:
        limitations.append("Fasting glucose is missing.")

    if hba1c is not None:
        status, status_evidence = _hba1c_status(hba1c)
        statuses.append(status)
        evidence.append(status_evidence)
    else:
        limitations.append("HbA1c is missing.")

    if "critical_low" in statuses or "critical_high" in statuses:
        urgency = "urgent_review"
        triggered = True
        if "critical_low" in statuses:
            message = "Fasting glucose is in a critically low range."
            plain = "The fasting glucose value is critically low and should be reviewed promptly by a clinician."
        else:
            message = "Fasting glucose is in a critically high range."
            plain = "The fasting glucose value is critically high and should be reviewed promptly by a clinician."
    elif "low" in statuses:
        urgency = "prompt_review"
        triggered = True
        message = "Fasting glucose is below the MVP low-glucose threshold."
        plain = "The fasting glucose value is lower than the threshold used by this prototype and should be reviewed with a clinician."
    elif "diabetes_range" in statuses:
        urgency = "prompt_review"
        triggered = True
        message = "One or more glucose markers are in a diabetes-range band."
        if "rising_trend" in statuses:
            message = "One or more glucose markers are in a diabetes-range band with a rising fasting-glucose trend."
        plain = "One or more blood sugar markers are in a range that can be associated with diabetes risk. This is not a diagnosis and should be discussed with a clinician."
    elif "prediabetes_risk" in statuses:
        urgency = "prompt_review" if "rising_trend" in statuses else "monitor"
        triggered = True
        message = "One or more glucose markers are in a prediabetes-risk band."
        if "rising_trend" in statuses:
            message = "One or more glucose markers are in a prediabetes-risk band with a rising fasting-glucose trend."
        plain = "One or more blood sugar markers are higher than the normal range used by this prototype and may deserve follow-up."
    elif "rising_trend" in statuses:
        urgency = "monitor"
        triggered = True
        message = "Fasting glucose remains below the diabetes-range threshold but is rising across recent results."
        plain = "Your fasting glucose values are still below the diabetes-range threshold used by this prototype, but they appear to be gradually increasing across recent tests. This is not an emergency, but it may be worth monitoring or discussing during a routine doctor visit."
    else:
        urgency = "routine"
        triggered = False
        message = "Glucose markers do not trigger the MVP glucose-risk rule."
        plain = "The glucose markers provided do not cross the glucose-risk thresholds used by this prototype."

    return RuleResult(
        rule_id="glucose_fpg_hba1c",
        pattern="glucose",
        triggered=triggered,
        urgency_level=urgency,
        message=message,
        plain_language_explanation=plain,
        evidence=evidence,
        limitations=limitations,
    )
