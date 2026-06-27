from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SexPayload = Literal["female", "male", "other_unknown"]


class PatientPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: str | None = None
    age: int = Field(..., ge=0)
    sex: SexPayload
    pregnant: bool | None = None


class LabRecordPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    test_name: str
    value: float
    unit: str
    collected_at: str
    source_label: str | None = None
    reference_min: float | None = None
    reference_max: float | None = None

    @field_validator("test_name", "unit", "collected_at")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value.strip()


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient: PatientPayload
    current_results: list[LabRecordPayload] = Field(..., min_length=1)
    historical_results: list[LabRecordPayload] = Field(default_factory=list)


class HistoryRecordsPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: list[LabRecordPayload] = Field(..., min_length=1)
