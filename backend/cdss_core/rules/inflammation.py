from __future__ import annotations

from cdss_core.models import LabRecord, RuleResult, UrgencyLevel
from cdss_core.thresholds import CRP_MARKED_MIN, CRP_MODERATE_MIN, CRP_NORMAL_MAX, CRP_SEVERE_MIN


def _crp_status(record: LabRecord) -> tuple[bool, UrgencyLevel, str, str]:
    value = record.value
    if value < CRP_NORMAL_MAX.value:
        return False, "routine", "CRP normal", f"CRP {value:g} {record.unit} is below 0.9 mg/dL"
    if value < CRP_MODERATE_MIN.value:
        return False, "routine", "CRP near upper reference range", f"CRP {value:g} {record.unit} is between 0.9 and 1.0 mg/dL"
    if value <= CRP_MARKED_MIN.value:
        return True, "monitor", "CRP moderately elevated", f"CRP {value:g} {record.unit} is between 1.0 and 10 mg/dL"
    if value <= CRP_SEVERE_MIN.value:
        return True, "prompt_review", "CRP markedly elevated", f"CRP {value:g} {record.unit} is above 10 mg/dL"
    return True, "urgent_review", "CRP severely elevated", f"CRP {value:g} {record.unit} is above 50 mg/dL"


def evaluate_inflammation(current: dict[str, LabRecord]) -> RuleResult | None:
    crp = current.get("crp")
    if crp is None:
        return None

    triggered, urgency, finding, evidence = _crp_status(crp)
    limitations = [
        "This rule does not diagnose infection, inflammatory disease, cardiovascular disease, or autoimmune disease.",
        "CRP is nonspecific and can rise for many transient reasons, including infection, injury, chronic disease, medications, and recent procedures.",
        "This prototype expects CRP values in mg/dL and does not convert units.",
    ]

    if triggered:
        message = f"CRP triggers the deterministic inflammation rule: {finding}."
        plain = "The CRP value is elevated according to the threshold bands used by this prototype and should be reviewed with a clinician."
    else:
        message = "CRP does not trigger the deterministic inflammation rule."
        plain = "The CRP value provided does not cross the inflammation thresholds used by this prototype."

    return RuleResult(
        rule_id="inflammation_crp",
        pattern="inflammation",
        triggered=triggered,
        urgency_level=urgency,
        message=message,
        plain_language_explanation=plain,
        evidence=[evidence],
        limitations=limitations,
    )
