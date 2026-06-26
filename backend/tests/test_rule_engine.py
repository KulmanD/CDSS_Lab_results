import unittest

from cdss_core import LabRecord, PatientDemographics, analyze_lab_results
from cdss_core.normalization import normalize_test_name
from cdss_core.trends import calculate_trend


class RuleEngineTests(unittest.TestCase):
    def test_normalizes_common_test_names(self):
        self.assertEqual(normalize_test_name("Hb"), "hemoglobin")
        self.assertEqual(normalize_test_name("Fasting Plasma Glucose"), "fasting_glucose")
        self.assertEqual(normalize_test_name("Estimated Glomerular Filtration Rate"), "egfr")

    def test_anemia_rule_uses_documented_threshold_not_uploaded_reference_range(self):
        patient = PatientDemographics(patient_id="demo", age=30, sex="female")
        response = analyze_lab_results(
            patient,
            [
                LabRecord(
                    test_name="Hemoglobin",
                    value=11.5,
                    unit="g/dL",
                    collected_at="2026-06-26",
                    reference_min=10.0,
                    reference_max=16.0,
                ),
                LabRecord(test_name="MCV", value=72.0, unit="fL", collected_at="2026-06-26"),
            ],
        )

        anemia = response.results[0]
        self.assertEqual(anemia.rule_id, "anemia_hgb_mcv")
        self.assertTrue(anemia.triggered)
        self.assertEqual(anemia.urgency_level, "monitor")
        self.assertIn("microcytic", anemia.message)
        self.assertTrue(any("threshold 12" in item for item in anemia.evidence))

    def test_anemia_rule_can_report_normal_result(self):
        patient = PatientDemographics(patient_id="demo", age=30, sex="female")
        response = analyze_lab_results(
            patient,
            [
                LabRecord(test_name="Hemoglobin", value=13.2, unit="g/dL", collected_at="2026-06-26"),
                LabRecord(test_name="MCV", value=88.0, unit="fL", collected_at="2026-06-26"),
            ],
        )

        anemia = response.results[0]
        self.assertFalse(anemia.triggered)
        self.assertEqual(anemia.urgency_level, "routine")

    def test_glucose_rule_flags_diabetes_range_without_diagnosis_language(self):
        patient = PatientDemographics(patient_id="demo", age=45, sex="male")
        response = analyze_lab_results(
            patient,
            [
                LabRecord(test_name="FPG", value=130.0, unit="mg/dL", collected_at="2026-06-26"),
                LabRecord(test_name="HbA1c", value=6.7, unit="%", collected_at="2026-06-26"),
            ],
        )

        glucose = response.results[0]
        self.assertEqual(glucose.rule_id, "glucose_fpg_hba1c")
        self.assertTrue(glucose.triggered)
        self.assertEqual(glucose.urgency_level, "prompt_review")
        combined_text = " ".join([glucose.message, glucose.plain_language_explanation]).lower()
        self.assertNotIn("you are diabetic", combined_text)

    def test_glucose_rule_flags_low_glucose(self):
        patient = PatientDemographics(patient_id="demo", age=45, sex="male")
        response = analyze_lab_results(
            patient,
            [LabRecord(test_name="fasting_glucose", value=62.0, unit="mg/dL", collected_at="2026-06-26")],
        )

        glucose = response.results[0]
        self.assertTrue(glucose.triggered)
        self.assertEqual(glucose.urgency_level, "prompt_review")
        self.assertTrue(any("below 70" in item for item in glucose.evidence))

    def test_kidney_rule_flags_stage_three_egfr_and_creatinine_context(self):
        patient = PatientDemographics(patient_id="demo", age=70, sex="female")
        response = analyze_lab_results(
            patient,
            [
                LabRecord(test_name="eGFR", value=45.0, unit="mL/min/1.73m2", collected_at="2026-06-26"),
                LabRecord(test_name="Creatinine", value=1.2, unit="mg/dL", collected_at="2026-06-26"),
            ],
        )

        kidney = response.results[0]
        self.assertEqual(kidney.rule_id, "kidney_egfr_creatinine")
        self.assertTrue(kidney.triggered)
        self.assertEqual(kidney.urgency_level, "prompt_review")
        self.assertTrue(any("between 30 and 59" in item for item in kidney.evidence))
        self.assertTrue(any("above 0.95" in item for item in kidney.evidence))

    def test_kidney_rule_escalates_very_low_egfr(self):
        patient = PatientDemographics(patient_id="demo", age=70, sex="male")
        response = analyze_lab_results(
            patient,
            [LabRecord(test_name="eGFR", value=12.0, unit="mL/min/1.73m2", collected_at="2026-06-26")],
        )

        kidney = response.results[0]
        self.assertTrue(kidney.triggered)
        self.assertEqual(kidney.urgency_level, "urgent_review")

    def test_trend_analysis_detects_significant_change(self):
        current = LabRecord(test_name="Hemoglobin", value=10.0, unit="g/dL", collected_at="2026-06-26")
        history = [LabRecord(test_name="Hgb", value=13.0, unit="g/dL", collected_at="2026-05-01")]

        trend = calculate_trend("hemoglobin", current, history)

        self.assertTrue(trend.significant)
        self.assertLess(trend.percent_change, -20.0)

    def test_dispatcher_returns_stable_order_and_overall_urgency(self):
        patient = PatientDemographics(patient_id="demo", age=65, sex="male")
        response = analyze_lab_results(
            patient,
            [
                LabRecord(test_name="Hemoglobin", value=12.0, unit="g/dL", collected_at="2026-06-26"),
                LabRecord(test_name="FPG", value=90.0, unit="mg/dL", collected_at="2026-06-26"),
                LabRecord(test_name="eGFR", value=12.0, unit="mL/min/1.73m2", collected_at="2026-06-26"),
            ],
        )

        self.assertEqual([result.pattern for result in response.results], ["anemia", "glucose", "kidney"])
        self.assertEqual(response.overall_urgency, "urgent_review")
        self.assertIn("does not provide diagnosis", response.disclaimer)


if __name__ == "__main__":
    unittest.main()
