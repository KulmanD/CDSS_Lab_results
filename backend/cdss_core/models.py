from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Sex = Literal["female", "male", "other_unknown"]
UrgencyLevel = Literal["routine", "monitor", "prompt_review", "urgent_review"]


URGENCY_ORDER: dict[UrgencyLevel, int] = {
    "routine": 0,
    "monitor": 1,
    "prompt_review": 2,
    "urgent_review": 3,
}


@dataclass(frozen=True)
class PatientDemographics:
    patient_id: str | None
    age: int
    sex: Sex
    pregnant: bool | None = None

    def __post_init__(self) -> None:
        if self.age < 0:
            raise ValueError("age must be non-negative")
        if self.sex not in {"female", "male", "other_unknown"}:
            raise ValueError("sex must be female, male, or other_unknown")


@dataclass(frozen=True)
class LabRecord:
    test_name: str
    value: float
    unit: str
    collected_at: str
    source_label: str | None = None
    reference_min: float | None = None
    reference_max: float | None = None

    def __post_init__(self) -> None:
        if not self.test_name.strip():
            raise ValueError("test_name is required")
        if not self.unit.strip():
            raise ValueError("unit is required")


@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    pattern: str
    triggered: bool
    urgency_level: UrgencyLevel
    message: str
    plain_language_explanation: str
    evidence: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    charts: list[Any] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AnalysisResponse:
    disclaimer: str
    overall_urgency: UrgencyLevel
    results: list[RuleResult]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["results"] = [result.to_dict() for result in self.results]
        return data


def max_urgency(levels: list[UrgencyLevel]) -> UrgencyLevel:
    if not levels:
        return "routine"
    return max(levels, key=lambda level: URGENCY_ORDER[level])
