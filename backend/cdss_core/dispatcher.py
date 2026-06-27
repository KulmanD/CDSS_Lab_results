from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from cdss_core.models import AnalysisResponse, LabRecord, PatientDemographics, RuleResult, max_urgency
from cdss_core.normalization import records_by_test_name
from cdss_core.rules import (
    evaluate_anemia,
    evaluate_glucose,
    evaluate_inflammation,
    evaluate_kidney,
    evaluate_lipids,
)
from cdss_core.visualization import build_charts_for_rule


DISCLAIMER = (
    "This educational prototype does not provide diagnosis or treatment. "
    "It uses predefined rules to highlight values that may deserve attention. "
    "Discuss abnormal or concerning results with a qualified clinician."
)


def analyze_lab_results(
    patient: PatientDemographics,
    current_results: Iterable[LabRecord],
    historical_results: Iterable[LabRecord] | None = None,
) -> AnalysisResponse:
    current_records = list(current_results)
    history = list(historical_results or [])
    current = records_by_test_name(current_records)

    results: list[RuleResult] = []
    for result in (
        evaluate_anemia(patient, current, history),
        evaluate_glucose(current, history),
        evaluate_kidney(patient, current, history),
        evaluate_lipids(patient, current),
        evaluate_inflammation(current),
    ):
        if result is not None:
            charts = build_charts_for_rule(result.rule_id, patient, current, history)
            results.append(replace(result, charts=charts))

    return AnalysisResponse(
        disclaimer=DISCLAIMER,
        overall_urgency=max_urgency([result.urgency_level for result in results]),
        results=results,
    )
