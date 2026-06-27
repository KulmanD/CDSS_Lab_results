from __future__ import annotations

from cdss_core.models import LabRecord, PatientDemographics, RuleResult
from cdss_core.thresholds import (
    HEMOGLOBIN_CRITICAL_HIGH,
    HEMOGLOBIN_CRITICAL_LOW,
    MCV_MACROCYTIC_MIN,
    MCV_MICROCYTIC_MAX,
    hemoglobin_high_threshold,
    hemoglobin_threshold,
)
from cdss_core.trends import calculate_trend


def _mcv_context(mcv: LabRecord | None) -> tuple[str | None, list[str]]:
    if mcv is None:
        return None, ["MCV is missing, so red-cell size context cannot be classified."]
    if mcv.value < MCV_MICROCYTIC_MAX.value:
        return "microcytic", [f"MCV {mcv.value:g} {mcv.unit} is below {MCV_MICROCYTIC_MAX.value:g} {MCV_MICROCYTIC_MAX.unit}."]
    if mcv.value > MCV_MACROCYTIC_MIN.value:
        return "macrocytic", [f"MCV {mcv.value:g} {mcv.unit} is above {MCV_MACROCYTIC_MIN.value:g} {MCV_MACROCYTIC_MIN.unit}."]
    return "normocytic", [f"MCV {mcv.value:g} {mcv.unit} is within 80-100 fL context range."]


def evaluate_anemia(
    patient: PatientDemographics,
    current: dict[str, LabRecord],
    history: list[LabRecord],
) -> RuleResult | None:
    hemoglobin = current.get("hemoglobin")
    mcv = current.get("mcv")
    if hemoglobin is None and mcv is None:
        return None

    limitations = [
        "This rule does not diagnose anemia.",
        "Iron studies, hematocrit, B12, folate, medications, bleeding history, and clinical context may be needed.",
    ]
    evidence: list[str] = []

    if hemoglobin is None:
        limitations.append("Hemoglobin is missing, so anemia-range low hemoglobin cannot be evaluated.")
        context, context_evidence = _mcv_context(mcv)
        evidence.extend(context_evidence)
        return RuleResult(
            rule_id="anemia_hgb_mcv",
            pattern="anemia",
            triggered=False,
            urgency_level="routine",
            message="MCV was provided, but hemoglobin is required for the MVP anemia-like rule.",
            plain_language_explanation="The prototype needs a hemoglobin value to check the anemia-like rule. MCV alone can describe red-cell size but cannot confirm low hemoglobin.",
            evidence=evidence,
            limitations=limitations,
        )

    threshold, threshold_limitations = hemoglobin_threshold(patient)
    limitations.extend(threshold_limitations)
    high_threshold, high_threshold_limitations = hemoglobin_high_threshold(patient)
    limitations.extend(high_threshold_limitations)
    evidence.append(f"hemoglobin {hemoglobin.value:g} {hemoglobin.unit} compared with threshold {threshold.value:g} {threshold.unit}")

    context, context_evidence = _mcv_context(mcv)
    evidence.extend(context_evidence)

    trend = calculate_trend("hemoglobin", hemoglobin, history)
    evidence.append(trend.message)
    if trend.percent_change is None:
        limitations.append(trend.message)
    elif trend.significant:
        evidence.append(f"hemoglobin changed from {trend.previous_value:g} to {trend.current_value:g} {hemoglobin.unit}")

    low_hgb = hemoglobin.value < threshold.value
    high_hgb = hemoglobin.value > high_threshold.value
    critical_low = hemoglobin.value < HEMOGLOBIN_CRITICAL_LOW.value
    critical_high = hemoglobin.value > HEMOGLOBIN_CRITICAL_HIGH.value
    if high_hgb:
        evidence.append(f"hemoglobin {hemoglobin.value:g} {hemoglobin.unit} is above the upper reference {high_threshold.value:g} {high_threshold.unit}")
    abnormal = low_hgb or high_hgb
    critical = critical_low or critical_high
    triggered = abnormal or trend.significant
    urgency = "routine"
    if critical:
        urgency = "urgent_review"
    elif abnormal and trend.significant:
        urgency = "prompt_review"
    elif abnormal or trend.significant:
        urgency = "monitor"

    if critical_low:
        message = "Hemoglobin is in a critically low range."
        plain = "Your hemoglobin value is critically low and should be reviewed promptly by a clinician."
    elif critical_high:
        message = "Hemoglobin is in a critically high range."
        plain = "Your hemoglobin value is critically high and should be reviewed promptly by a clinician."
    elif low_hgb:
        if context:
            message = f"Hemoglobin is below the MVP threshold with {context} MCV context."
        else:
            message = "Hemoglobin is below the MVP threshold."
        plain = "Your hemoglobin value is lower than the threshold used by this educational prototype. This can happen for many reasons and should be reviewed with a clinician."
    elif high_hgb:
        if context:
            message = f"Hemoglobin is above the MVP upper reference range with {context} MCV context."
        else:
            message = "Hemoglobin is above the MVP upper reference range."
        plain = "Your hemoglobin value is higher than the upper reference range used by this educational prototype. This can happen for several reasons and should be reviewed with a clinician."
    elif trend.significant:
        message = "Hemoglobin is within threshold but changed enough to trigger the MVP trend rule."
        plain = "Your hemoglobin is not below the rule threshold, but it changed noticeably compared with the previous value provided."
    else:
        message = "Hemoglobin does not trigger the MVP anemia-like rule."
        plain = "The hemoglobin value provided does not cross the anemia-like threshold used by this prototype."

    return RuleResult(
        rule_id="anemia_hgb_mcv",
        pattern="anemia",
        triggered=triggered,
        urgency_level=urgency,
        message=message,
        plain_language_explanation=plain,
        evidence=evidence,
        limitations=limitations,
    )
