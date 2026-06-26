from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cdss_core import LabRecord, PatientDemographics, analyze_lab_results
from cdss_core.models import URGENCY_ORDER


MVP_RULE_IDS = ["anemia_hgb_mcv", "glucose_fpg_hba1c", "kidney_egfr_creatinine"]


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    expected_triggered: set[str]
    actual_triggered: set[str]
    expected_urgency: str
    actual_urgency: str

    @property
    def passed(self) -> bool:
        return self.expected_triggered == self.actual_triggered and self.expected_urgency == self.actual_urgency


def _patient_from_dict(data: dict[str, Any]) -> PatientDemographics:
    return PatientDemographics(
        patient_id=data.get("patient_id"),
        age=int(data["age"]),
        sex=data["sex"],
        pregnant=data.get("pregnant"),
    )


def _record_from_dict(data: dict[str, Any]) -> LabRecord:
    return LabRecord(
        test_name=data["test_name"],
        value=float(data["value"]),
        unit=data["unit"],
        collected_at=data["collected_at"],
        source_label=data.get("source_label"),
        reference_min=data.get("reference_min"),
        reference_max=data.get("reference_max"),
    )


def load_cases(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Evaluation file must contain a list of cases.")
    return data


def evaluate_case(case: dict[str, Any]) -> CaseResult:
    response = analyze_lab_results(
        patient=_patient_from_dict(case["patient"]),
        current_results=[_record_from_dict(record) for record in case["current_results"]],
        historical_results=[_record_from_dict(record) for record in case.get("historical_results", [])],
    )
    actual_triggered = {result.rule_id for result in response.results if result.triggered}
    expected = case["expected"]
    return CaseResult(
        case_id=case["case_id"],
        expected_triggered=set(expected["triggered_rule_ids"]),
        actual_triggered=actual_triggered,
        expected_urgency=expected["overall_urgency"],
        actual_urgency=response.overall_urgency,
    )


def summarize(results: list[CaseResult]) -> dict[str, Any]:
    total_cases = len(results)
    passed_cases = sum(1 for result in results if result.passed)
    per_rule: dict[str, dict[str, int | float]] = {}

    for rule_id in MVP_RULE_IDS:
        tp = fp = tn = fn = 0
        for result in results:
            expected = rule_id in result.expected_triggered
            actual = rule_id in result.actual_triggered
            if expected and actual:
                tp += 1
            elif not expected and actual:
                fp += 1
            elif expected and not actual:
                fn += 1
            else:
                tn += 1
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        per_rule[rule_id] = {
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }

    urgency_matches = sum(1 for result in results if result.expected_urgency == result.actual_urgency)
    return {
        "cases": total_cases,
        "case_accuracy": round(passed_cases / total_cases if total_cases else 0.0, 4),
        "urgency_accuracy": round(urgency_matches / total_cases if total_cases else 0.0, 4),
        "per_rule": per_rule,
        "failures": [
            {
                "case_id": result.case_id,
                "expected_triggered": sorted(result.expected_triggered),
                "actual_triggered": sorted(result.actual_triggered),
                "expected_urgency": result.expected_urgency,
                "actual_urgency": result.actual_urgency,
            }
            for result in results
            if not result.passed
        ],
    }


def run_evaluation(path: Path) -> dict[str, Any]:
    cases = load_cases(path)
    results = [evaluate_case(case) for case in cases]
    return summarize(results)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate deterministic CDSS MVP cases.")
    parser.add_argument("--data", type=Path, default=Path("../data/evaluation/mvp_cases.json"))
    parser.add_argument("--min-f1", type=float, default=1.0)
    args = parser.parse_args()

    summary = run_evaluation(args.data)
    print(json.dumps(summary, indent=2))

    low_f1 = [
        rule_id
        for rule_id, metrics in summary["per_rule"].items()
        if float(metrics["f1"]) < args.min_f1
    ]
    if summary["failures"] or low_f1:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
