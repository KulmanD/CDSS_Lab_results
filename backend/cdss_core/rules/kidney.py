from __future__ import annotations

from cdss_core.models import LabRecord, PatientDemographics, RuleResult, UrgencyLevel, max_urgency
from cdss_core.thresholds import EGFR_STAGE_2_MIN, EGFR_STAGE_3_MIN, EGFR_STAGE_4_MIN, creatinine_range
from cdss_core.trends import calculate_trend


def _egfr_stage(record: LabRecord) -> tuple[str, str, str, bool]:
    value = record.value
    if value < EGFR_STAGE_4_MIN.value:
        return "Stage V range", "urgent_review", f"eGFR {value:g} {record.unit} is below 15", True
    if value < EGFR_STAGE_3_MIN.value:
        return "Stage IV range", "urgent_review", f"eGFR {value:g} {record.unit} is between 15 and 29", True
    if value < EGFR_STAGE_2_MIN.value:
        return "Stage III range", "prompt_review", f"eGFR {value:g} {record.unit} is between 30 and 59", True
    if value < 90:
        return "Stage II range", "monitor", f"eGFR {value:g} {record.unit} is between 60 and 89", True
    return "Stage I/normal filtration range", "routine", f"eGFR {value:g} {record.unit} is 90 or higher", False


def _creatinine_status(
    patient: PatientDemographics,
    record: LabRecord,
) -> tuple[bool, str, str, list[str]]:
    lower, upper, limitations = creatinine_range(patient)
    if record.value < lower.value:
        return True, "monitor", f"creatinine {record.value:g} {record.unit} is below {lower.value:g} {lower.unit}", limitations
    if record.value > upper.value:
        return True, "prompt_review", f"creatinine {record.value:g} {record.unit} is above {upper.value:g} {upper.unit}", limitations
    return False, "routine", f"creatinine {record.value:g} {record.unit} is within {lower.value:g}-{upper.value:g} {upper.unit}", limitations


def evaluate_kidney(
    patient: PatientDemographics,
    current: dict[str, LabRecord],
    history: list[LabRecord],
) -> RuleResult | None:
    egfr = current.get("egfr")
    creatinine = current.get("creatinine")
    if egfr is None and creatinine is None:
        return None

    limitations = [
        "This rule does not diagnose chronic kidney disease.",
        "CKD staging requires persistence, clinical context, and clinician review.",
    ]
    evidence: list[str] = []
    urgencies: list[UrgencyLevel] = []
    triggered = False
    messages: list[str] = []

    if egfr is not None:
        stage, urgency, stage_evidence, stage_triggered = _egfr_stage(egfr)
        triggered = triggered or stage_triggered
        urgencies.append(urgency)
        evidence.append(stage_evidence)
        messages.append(stage)
        trend = calculate_trend("egfr", egfr, history)
        evidence.append(trend.message)
        if trend.percent_change is None:
            limitations.append(trend.message)
        elif trend.significant:
            triggered = True
            urgencies.append("prompt_review")
            evidence.append(f"eGFR changed from {trend.previous_value:g} to {trend.current_value:g} {egfr.unit}")
    else:
        limitations.append("eGFR is missing, so eGFR stage cannot be evaluated.")

    if creatinine is not None:
        creat_triggered, creat_urgency, creat_evidence, creat_limitations = _creatinine_status(patient, creatinine)
        triggered = triggered or creat_triggered
        urgencies.append(creat_urgency)
        evidence.append(creat_evidence)
        limitations.extend(creat_limitations)
        trend = calculate_trend("creatinine", creatinine, history)
        evidence.append(trend.message)
        if trend.percent_change is None:
            limitations.append(trend.message)
        elif trend.significant:
            triggered = True
            urgencies.append("prompt_review")
            evidence.append(f"creatinine changed from {trend.previous_value:g} to {trend.current_value:g} {creatinine.unit}")
    else:
        limitations.append("Creatinine is missing, so creatinine context cannot be evaluated.")

    urgency = max_urgency(urgencies)
    if triggered:
        message = "Kidney-function markers trigger the MVP kidney rule: " + "; ".join(messages or ["creatinine context"])
        plain = "One or more kidney-function values are in a range that should be reviewed with a clinician. This prototype cannot diagnose kidney disease."
    else:
        message = "Kidney-function markers do not trigger the MVP kidney rule."
        plain = "The kidney-function values provided do not cross the kidney thresholds used by this prototype."

    return RuleResult(
        rule_id="kidney_egfr_creatinine",
        pattern="kidney",
        triggered=triggered,
        urgency_level=urgency,
        message=message,
        plain_language_explanation=plain,
        evidence=evidence,
        limitations=limitations,
    )
