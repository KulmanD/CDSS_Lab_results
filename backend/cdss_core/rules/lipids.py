from __future__ import annotations

from cdss_core.models import LabRecord, PatientDemographics, RuleResult, UrgencyLevel, max_urgency
from cdss_core.thresholds import (
    HDL_LOW_FEMALE,
    HDL_LOW_MALE,
    LDL_BORDERLINE_HIGH_MIN,
    LDL_HIGH_MIN,
    LDL_OPTIMAL_MAX,
    LDL_VERY_HIGH_MIN,
    TOTAL_CHOLESTEROL_DESIRABLE_MAX,
    TOTAL_CHOLESTEROL_HIGH_MIN,
    TRIGLYCERIDES_HIGH_MIN,
    TRIGLYCERIDES_NORMAL_MAX,
    TRIGLYCERIDES_SEVERE_MIN,
    VLDL_HIGH_MIN,
)


LIPID_MARKERS = ("total_cholesterol", "ldl", "hdl", "triglycerides", "vldl")


def _total_cholesterol_status(record: LabRecord) -> tuple[bool, UrgencyLevel, str, str]:
    value = record.value
    if value < TOTAL_CHOLESTEROL_DESIRABLE_MAX.value:
        return False, "routine", "total cholesterol desirable", f"total cholesterol {value:g} {record.unit} is below 200 mg/dL"
    if value < TOTAL_CHOLESTEROL_HIGH_MIN.value:
        return True, "monitor", "total cholesterol borderline high", f"total cholesterol {value:g} {record.unit} is between 200 and 239 mg/dL"
    return True, "prompt_review", "total cholesterol high", f"total cholesterol {value:g} {record.unit} is at or above 240 mg/dL"


def _ldl_status(record: LabRecord) -> tuple[bool, UrgencyLevel, str, str]:
    value = record.value
    if value < LDL_OPTIMAL_MAX.value:
        return False, "routine", "LDL optimal", f"LDL {value:g} {record.unit} is below 100 mg/dL"
    if value < LDL_BORDERLINE_HIGH_MIN.value:
        return False, "routine", "LDL near optimal", f"LDL {value:g} {record.unit} is between 100 and 129 mg/dL"
    if value < LDL_HIGH_MIN.value:
        return True, "monitor", "LDL borderline high", f"LDL {value:g} {record.unit} is between 130 and 159 mg/dL"
    if value < LDL_VERY_HIGH_MIN.value:
        return True, "prompt_review", "LDL high", f"LDL {value:g} {record.unit} is between 160 and 189 mg/dL"
    return True, "prompt_review", "LDL very high", f"LDL {value:g} {record.unit} is at or above 190 mg/dL"


def _hdl_low_threshold(patient: PatientDemographics) -> tuple[float, list[str]]:
    if patient.sex == "female":
        return HDL_LOW_FEMALE.value, []
    if patient.sex == "male":
        return HDL_LOW_MALE.value, []
    return HDL_LOW_MALE.value, ["Sex is unknown, so the lower 40 mg/dL HDL threshold is used."]


def _hdl_status(patient: PatientDemographics, record: LabRecord) -> tuple[bool, UrgencyLevel, str, str, list[str]]:
    threshold, limitations = _hdl_low_threshold(patient)
    value = record.value
    if value < threshold:
        return True, "monitor", "HDL low", f"HDL {value:g} {record.unit} is below {threshold:g} mg/dL", limitations
    return False, "routine", "HDL not low", f"HDL {value:g} {record.unit} is at or above {threshold:g} mg/dL", limitations


def _triglycerides_status(record: LabRecord) -> tuple[bool, UrgencyLevel, str, str]:
    value = record.value
    if value < TRIGLYCERIDES_NORMAL_MAX.value:
        return False, "routine", "triglycerides normal", f"triglycerides {value:g} {record.unit} are below 150 mg/dL"
    if value < TRIGLYCERIDES_HIGH_MIN.value:
        return True, "monitor", "triglycerides borderline high", f"triglycerides {value:g} {record.unit} are between 150 and 199 mg/dL"
    if value < TRIGLYCERIDES_SEVERE_MIN.value:
        return True, "prompt_review", "triglycerides high", f"triglycerides {value:g} {record.unit} are between 200 and 499 mg/dL"
    return True, "urgent_review", "triglycerides very high", f"triglycerides {value:g} {record.unit} are at or above 500 mg/dL"


def _vldl_status(record: LabRecord) -> tuple[bool, UrgencyLevel, str, str]:
    value = record.value
    if value < VLDL_HIGH_MIN.value:
        return False, "routine", "VLDL in usual range", f"VLDL {value:g} {record.unit} is below 30 mg/dL"
    return True, "monitor", "VLDL above usual range", f"VLDL {value:g} {record.unit} is at or above 30 mg/dL"


def evaluate_lipids(patient: PatientDemographics, current: dict[str, LabRecord]) -> RuleResult | None:
    if not any(marker in current for marker in LIPID_MARKERS):
        return None

    evidence: list[str] = []
    limitations = [
        "This rule does not diagnose cardiovascular disease or determine medication need.",
        "Lipid goals depend on age, diabetes status, ASCVD risk, fasting status, pregnancy, medications, and clinician context.",
        "This prototype expects lipid values in mg/dL and does not convert units.",
    ]
    urgencies: list[UrgencyLevel] = []
    triggered = False
    abnormal_findings: list[str] = []

    total_cholesterol = current.get("total_cholesterol")
    if total_cholesterol is not None:
        total_triggered, urgency, finding, status_evidence = _total_cholesterol_status(total_cholesterol)
        triggered = triggered or total_triggered
        urgencies.append(urgency)
        if total_triggered:
            abnormal_findings.append(finding)
        evidence.append(status_evidence)
    else:
        limitations.append("Total cholesterol is missing.")

    ldl = current.get("ldl")
    if ldl is not None:
        ldl_triggered, urgency, finding, status_evidence = _ldl_status(ldl)
        triggered = triggered or ldl_triggered
        urgencies.append(urgency)
        if ldl_triggered:
            abnormal_findings.append(finding)
        evidence.append(status_evidence)
    else:
        limitations.append("LDL is missing.")

    hdl = current.get("hdl")
    if hdl is not None:
        hdl_triggered, urgency, finding, status_evidence, hdl_limitations = _hdl_status(patient, hdl)
        triggered = triggered or hdl_triggered
        urgencies.append(urgency)
        if hdl_triggered:
            abnormal_findings.append(finding)
        evidence.append(status_evidence)
        limitations.extend(hdl_limitations)
    else:
        limitations.append("HDL is missing.")

    triglycerides = current.get("triglycerides")
    if triglycerides is not None:
        tg_triggered, urgency, finding, status_evidence = _triglycerides_status(triglycerides)
        triggered = triggered or tg_triggered
        urgencies.append(urgency)
        if tg_triggered:
            abnormal_findings.append(finding)
        evidence.append(status_evidence)
    else:
        limitations.append("Triglycerides are missing.")

    vldl = current.get("vldl")
    if vldl is not None:
        vldl_triggered, urgency, finding, status_evidence = _vldl_status(vldl)
        triggered = triggered or vldl_triggered
        urgencies.append(urgency)
        if vldl_triggered:
            abnormal_findings.append(finding)
        evidence.append(status_evidence)
        limitations.append("VLDL is often calculated from triglycerides, so direct VLDL interpretation should be reviewed carefully.")

    urgency = max_urgency(urgencies)
    if triggered:
        message = "Lipid markers trigger the deterministic lipid-risk rule: " + "; ".join(abnormal_findings)
        plain = "One or more cholesterol or triglyceride markers are outside the reference bands used by this prototype and should be reviewed with a clinician."
    else:
        message = "Lipid markers do not trigger the deterministic lipid-risk rule."
        plain = "The lipid values provided do not cross the lipid-risk thresholds used by this prototype."

    return RuleResult(
        rule_id="lipid_panel",
        pattern="lipids",
        triggered=triggered,
        urgency_level=urgency,
        message=message,
        plain_language_explanation=plain,
        evidence=evidence,
        limitations=limitations,
    )
