from __future__ import annotations

from collections.abc import Iterable

from cdss_core.models import AnalysisResponse, LabRecord, PatientDemographics, RuleResult, max_urgency
from cdss_core.normalization import records_by_test_name
from cdss_core.rules import (
    evaluate_anemia,
    evaluate_glucose,
    evaluate_inflammation,
    evaluate_kidney,
    evaluate_lipids,
)


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
            results.append(result)

    return AnalysisResponse(
        disclaimer=DISCLAIMER,
        overall_urgency=max_urgency([result.urgency_level for result in results]),
        results=results,
    )
