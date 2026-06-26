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

MCV_MICROCYTIC_MAX = Threshold(80.0, "fL", SOURCE_ANEMIA, "MCV below this value is microcytic context.")
MCV_MACROCYTIC_MIN = Threshold(100.0, "fL", SOURCE_ANEMIA, "MCV above this value is macrocytic context.")

FASTING_GLUCOSE_LOW = Threshold(70.0, "mg/dL", SOURCE_GLUCOSE, "Below this value is a low glucose warning.")
FASTING_GLUCOSE_NORMAL_MAX = Threshold(100.0, "mg/dL", SOURCE_GLUCOSE, "Below this value is normal range.")
FASTING_GLUCOSE_DIABETES_MIN = Threshold(126.0, "mg/dL", SOURCE_GLUCOSE, "At or above this value is diabetes-range.")

HBA1C_NORMAL_MAX = Threshold(5.7, "%", SOURCE_GLUCOSE, "Below this value is normal range.")
HBA1C_DIABETES_MIN = Threshold(6.5, "%", SOURCE_GLUCOSE, "At or above this value is diabetes-range.")

EGFR_STAGE_2_MIN = Threshold(60.0, "mL/min/1.73m2", SOURCE_KIDNEY, "Stage II lower bound.")
EGFR_STAGE_3_MIN = Threshold(30.0, "mL/min/1.73m2", SOURCE_KIDNEY, "Stage III lower bound.")
EGFR_STAGE_4_MIN = Threshold(15.0, "mL/min/1.73m2", SOURCE_KIDNEY, "Stage IV lower bound.")


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
