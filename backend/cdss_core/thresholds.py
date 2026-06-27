from __future__ import annotations

from dataclasses import dataclass

from cdss_core.models import PatientDemographics


@dataclass(frozen=True)
class Threshold:
    value: float
    unit: str
    source: str
    note: str


SOURCE_ANEMIA = "docs/thresholds.md#anemia-like-pattern"
SOURCE_GLUCOSE = "docs/thresholds.md#glucose-risk-pattern"
SOURCE_KIDNEY = "docs/thresholds.md#kidney-function-alert"
SOURCE_LIPIDS = "docs/thresholds.md#lipid-risk-pattern"
SOURCE_INFLAMMATION = "docs/thresholds.md#crpinflammation-pattern"

MCV_MICROCYTIC_MAX = Threshold(80.0, "fL", SOURCE_ANEMIA, "MCV below this value is microcytic context.")
MCV_MACROCYTIC_MIN = Threshold(100.0, "fL", SOURCE_ANEMIA, "MCV above this value is macrocytic context.")

HEMOGLOBIN_CRITICAL_LOW = Threshold(7.0, "g/dL", SOURCE_ANEMIA, "Below this value is a critical-low hemoglobin needing prompt review.")
HEMOGLOBIN_CRITICAL_HIGH = Threshold(20.0, "g/dL", SOURCE_ANEMIA, "Above this value is a critical-high hemoglobin needing prompt review.")

FASTING_GLUCOSE_CRITICAL_LOW = Threshold(54.0, "mg/dL", SOURCE_GLUCOSE, "Below this value is a critical-low glucose value needing prompt review.")
FASTING_GLUCOSE_LOW = Threshold(70.0, "mg/dL", SOURCE_GLUCOSE, "Below this value is a low glucose warning.")
FASTING_GLUCOSE_NORMAL_MAX = Threshold(100.0, "mg/dL", SOURCE_GLUCOSE, "Below this value is normal range.")
FASTING_GLUCOSE_DIABETES_MIN = Threshold(126.0, "mg/dL", SOURCE_GLUCOSE, "At or above this value is diabetes-range.")
FASTING_GLUCOSE_CRITICAL_HIGH = Threshold(400.0, "mg/dL", SOURCE_GLUCOSE, "At or above this value is a critical-high glucose value needing prompt review.")

HBA1C_NORMAL_MAX = Threshold(5.7, "%", SOURCE_GLUCOSE, "Below this value is normal range.")
HBA1C_DIABETES_MIN = Threshold(6.5, "%", SOURCE_GLUCOSE, "At or above this value is diabetes-range.")

EGFR_STAGE_2_MIN = Threshold(60.0, "mL/min/1.73m2", SOURCE_KIDNEY, "Stage II lower bound.")
EGFR_STAGE_3_MIN = Threshold(30.0, "mL/min/1.73m2", SOURCE_KIDNEY, "Stage III lower bound.")
EGFR_STAGE_4_MIN = Threshold(15.0, "mL/min/1.73m2", SOURCE_KIDNEY, "Stage IV lower bound.")

CREATININE_CRITICAL_HIGH = Threshold(4.0, "mg/dL", SOURCE_KIDNEY, "At or above this value is a critical-high creatinine needing prompt review.")

TOTAL_CHOLESTEROL_DESIRABLE_MAX = Threshold(200.0, "mg/dL", SOURCE_LIPIDS, "Below this value is desirable.")
TOTAL_CHOLESTEROL_HIGH_MIN = Threshold(240.0, "mg/dL", SOURCE_LIPIDS, "At or above this value is high.")

LDL_OPTIMAL_MAX = Threshold(100.0, "mg/dL", SOURCE_LIPIDS, "Below this value is optimal.")
LDL_BORDERLINE_HIGH_MIN = Threshold(130.0, "mg/dL", SOURCE_LIPIDS, "At or above this value is borderline high.")
LDL_HIGH_MIN = Threshold(160.0, "mg/dL", SOURCE_LIPIDS, "At or above this value is high.")
LDL_VERY_HIGH_MIN = Threshold(190.0, "mg/dL", SOURCE_LIPIDS, "At or above this value is very high.")

HDL_LOW_MALE = Threshold(40.0, "mg/dL", SOURCE_LIPIDS, "Below this value is low for men.")
HDL_LOW_FEMALE = Threshold(50.0, "mg/dL", SOURCE_LIPIDS, "Below this value is low for women.")

TRIGLYCERIDES_NORMAL_MAX = Threshold(150.0, "mg/dL", SOURCE_LIPIDS, "Below this value is normal.")
TRIGLYCERIDES_BORDERLINE_HIGH_MIN = Threshold(150.0, "mg/dL", SOURCE_LIPIDS, "At or above this value is borderline high.")
TRIGLYCERIDES_HIGH_MIN = Threshold(200.0, "mg/dL", SOURCE_LIPIDS, "At or above this value is high.")
TRIGLYCERIDES_SEVERE_MIN = Threshold(500.0, "mg/dL", SOURCE_LIPIDS, "At or above this value is very high.")

VLDL_HIGH_MIN = Threshold(30.0, "mg/dL", SOURCE_LIPIDS, "At or above this value is above the usual VLDL range.")

CRP_NORMAL_MAX = Threshold(0.9, "mg/dL", SOURCE_INFLAMMATION, "Below this value is typical normal range.")
CRP_MODERATE_MIN = Threshold(1.0, "mg/dL", SOURCE_INFLAMMATION, "At or above this value is moderate elevation.")
CRP_MARKED_MIN = Threshold(10.0, "mg/dL", SOURCE_INFLAMMATION, "Above this value is marked elevation.")
CRP_SEVERE_MIN = Threshold(50.0, "mg/dL", SOURCE_INFLAMMATION, "Above this value is severe elevation.")


def hemoglobin_threshold(patient: PatientDemographics) -> tuple[Threshold, list[str]]:
    limitations: list[str] = []
    if patient.sex == "male":
        return (
            Threshold(13.0, "g/dL", SOURCE_ANEMIA, "WHO threshold used for men."),
            limitations,
        )
    if patient.sex == "female":
        if patient.age >= 50:
            limitations.append("Age 50 or older is used only as a rough post-menopausal proxy in this MVP.")
            return (
                Threshold(13.0, "g/dL", SOURCE_ANEMIA, "Threshold used for post-menopausal women in the guidance."),
                limitations,
            )
        if patient.pregnant:
            limitations.append("Pregnancy can change hemoglobin interpretation; clinician review is important.")
        return (
            Threshold(12.0, "g/dL", SOURCE_ANEMIA, "WHO threshold used for pre-menopausal women."),
            limitations,
        )

    limitations.append("Sex is unknown, so the more conservative 13 g/dL hemoglobin threshold is used.")
    return (
        Threshold(13.0, "g/dL", SOURCE_ANEMIA, "Conservative threshold for unknown sex."),
        limitations,
    )


def hemoglobin_high_threshold(patient: PatientDemographics) -> tuple[Threshold, list[str]]:
    """Upper reference limit for hemoglobin. A value above this is highlighted
    for review (high hemoglobin can reflect dehydration, smoking, lung disease,
    or a primary marrow condition); it is not a diagnosis."""
    limitations: list[str] = []
    if patient.sex == "male":
        return (
            Threshold(17.5, "g/dL", SOURCE_ANEMIA, "Common adult upper reference range for men."),
            limitations,
        )
    if patient.sex == "female":
        return (
            Threshold(15.5, "g/dL", SOURCE_ANEMIA, "Common adult upper reference range for women."),
            limitations,
        )

    limitations.append("Sex is unknown, so the higher 17.5 g/dL upper reference is used to avoid over-flagging.")
    return (
        Threshold(17.5, "g/dL", SOURCE_ANEMIA, "Upper reference for unknown sex."),
        limitations,
    )


def creatinine_range(patient: PatientDemographics) -> tuple[Threshold, Threshold, list[str]]:
    limitations: list[str] = []
    if patient.sex == "male":
        return (
            Threshold(0.7, "mg/dL", SOURCE_KIDNEY, "Common lower range for men."),
            Threshold(1.3, "mg/dL", SOURCE_KIDNEY, "Common upper range for men."),
            limitations,
        )
    if patient.sex == "female":
        return (
            Threshold(0.5, "mg/dL", SOURCE_KIDNEY, "Common lower range for women."),
            Threshold(0.95, "mg/dL", SOURCE_KIDNEY, "Common upper range for women."),
            limitations,
        )

    limitations.append("Sex is unknown, so the broad 0.5-1.3 mg/dL creatinine range is used.")
    return (
        Threshold(0.5, "mg/dL", SOURCE_KIDNEY, "Broad lower range for unknown sex."),
        Threshold(1.3, "mg/dL", SOURCE_KIDNEY, "Broad upper range for unknown sex."),
        limitations,
    )
