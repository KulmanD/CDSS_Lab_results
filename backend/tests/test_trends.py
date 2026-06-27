import unittest

from cdss_core import LabRecord, PatientDemographics, analyze_lab_results
from cdss_core.trends import calculate_trend


def _record(value, collected_at, test_name="hemoglobin", unit="g/dL"):
    return LabRecord(test_name=test_name, value=value, unit=unit, collected_at=collected_at)


class TrendEngineTests(unittest.TestCase):
    def test_adverse_drop_is_significant(self):
        trend = calculate_trend(
            "hemoglobin",
            _record(10.0, "2026-06-26"),
            [_record(13.0, "2026-05-01")],
        )
        self.assertTrue(trend.significant)
        self.assertEqual(trend.direction, "falling")
        self.assertLess(trend.percent_change, -20.0)

    def test_improving_trend_is_not_flagged(self):
        # Regression test for the old direction-blind behaviour (issue #23):
        # a rising hemoglobin is an improvement and must not raise an alert.
        trend = calculate_trend(
            "hemoglobin",
            _record(13.5, "2026-06-26"),
            [_record(11.0, "2026-05-01")],
        )
        self.assertEqual(trend.direction, "rising")
        self.assertFalse(trend.significant)

    def test_single_dip_does_not_hide_a_real_rising_trend(self):
        # 82 -> 79 -> 98 is not strictly monotonic, but the slope is clearly
        # upward; the regression engine still detects it.
        trend = calculate_trend(
            "fasting_glucose",
            _record(98.0, "2026-06-26", "fasting_glucose", "mg/dL"),
            [
                _record(82.0, "2026-04-26", "fasting_glucose", "mg/dL"),
                _record(79.0, "2026-05-26", "fasting_glucose", "mg/dL"),
            ],
        )
        self.assertEqual(trend.direction, "rising")
        self.assertTrue(trend.significant)

    def test_scattered_results_are_not_confirmed(self):
        # A large swing with no consistent direction should not confirm a trend.
        trend = calculate_trend(
            "fasting_glucose",
            _record(99.0, "2026-06-26", "fasting_glucose", "mg/dL"),
            [
                _record(80.0, "2026-04-26", "fasting_glucose", "mg/dL"),
                _record(140.0, "2026-05-26", "fasting_glucose", "mg/dL"),
            ],
        )
        self.assertFalse(trend.significant)

    def test_results_too_close_in_time_are_insufficient(self):
        trend = calculate_trend(
            "hemoglobin",
            _record(11.0, "2026-06-26"),
            [_record(13.0, "2026-06-20")],
        )
        self.assertFalse(trend.significant)
        self.assertEqual(trend.confidence, "insufficient")

    def test_improving_egfr_does_not_trigger_kidney_rule(self):
        patient = PatientDemographics(patient_id="demo", age=63, sex="male")
        response = analyze_lab_results(
            patient,
            [LabRecord(test_name="egfr", value=95.0, unit="mL/min/1.73m2", collected_at="2026-06-26")],
            [LabRecord(test_name="egfr", value=70.0, unit="mL/min/1.73m2", collected_at="2026-03-01")],
        )
        kidney = response.results[0]
        self.assertEqual(kidney.rule_id, "kidney_egfr_creatinine")
        self.assertFalse(kidney.triggered)
        self.assertEqual(kidney.urgency_level, "routine")


if __name__ == "__main__":
    unittest.main()
