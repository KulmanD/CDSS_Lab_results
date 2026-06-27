from __future__ import annotations

from api.schemas import LabRecordPayload


_HISTORY: dict[str, list[LabRecordPayload]] = {}


def get_patient_history(patient_id: str) -> list[LabRecordPayload]:
    return [record.model_copy(deep=True) for record in _HISTORY.get(patient_id, [])]


def save_patient_history(patient_id: str, records: list[LabRecordPayload]) -> list[LabRecordPayload]:
    _HISTORY[patient_id] = [record.model_copy(deep=True) for record in records]
    return get_patient_history(patient_id)


def delete_patient_history(patient_id: str) -> int:
    existing = _HISTORY.pop(patient_id, [])
    return len(existing)


def clear_all_history() -> None:
    _HISTORY.clear()
