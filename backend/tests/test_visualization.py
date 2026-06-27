import unittest

from cdss_core import LabRecord, PatientDemographics, analyze_lab_results
from cdss_core.visualization import build_marker_chart


class VisualizationTests(unittest.TestCase):
    def test_chart_attached_to_each_rule_result(self):
        patient = PatientDemographics(patient_id="demo", age=30, sex="female")
        response = analyze_lab_results(
            patient,
            [
                LabRecord(test_name="hemoglobin", value=11.4, unit="g/dL", collected_at="2026-06-26"),
                LabRecord(test_name="mcv", value=72.0, unit="fL", collected_at="2026-06-26"),
            ],
        )

        anemia = response.results[0]
        charts = {chart["test_name"]: chart for chart in anemia.to_dict()["charts"]}
        self.assertEqual(set(charts), {"hemoglobin", "mcv"})

        hgb = charts["hemoglobin"]
        # Reference threshold for a pre-menopausal woman is 12 g/dL; 11.4 is below it.
        self.assertEqual(hgb["reference_low"], 12.0)
        self.assertEqual(hgb["range_position"], "below")
        self.assertEqual(hgb["band_label"], "Low")
        self.assertEqual(hgb["value"], 11.4)
        self.assertLessEqual(hgb["axis_min"], 11.4)
        self.assertGreaterEqual(hgb["axis_max"], 11.4)
        self.assertTrue(hgb["bands"])

    def test_value_within_range_reports_normal_band(self):
        patient = PatientDemographics(patient_id="demo", age=30, sex="male")
        chart = build_marker_chart(
            "mcv",
            LabRecord(test_name="mcv", value=88.0, unit="fL", collected_at="2026-06-26"),
            patient,
            [],
        )
        self.assertIsNotNone(chart)
        self.assertEqual(chart.range_position, "within")
        self.assertEqual(chart.band_label, "Normal")
        self.assertEqual(chart.severity, "normal")

    def test_trend_points_built_from_dated_history(self):
        patient = PatientDemographics(patient_id="demo", age=55, sex="male")
        history = [
            LabRecord(test_name="fasting_glucose", value=82.0, unit="mg/dL", collected_at="2026-04-26"),
            LabRecord(test_name="fasting_glucose", value=90.0, unit="mg/dL", collected_at="2026-05-26"),
        ]
        chart = build_marker_chart(
            "fasting_glucose",
            LabRecord(test_name="fasting_glucose", value=98.0, unit="mg/dL", collected_at="2026-06-26"),
            patient,
            history,
        )
        self.assertIsNotNone(chart)
        self.assertEqual([point.value for point in chart.trend], [82.0, 90.0, 98.0])
        self.assertEqual([point.collected_at for point in chart.trend][-1], "2026-06-26")

    def test_single_point_has_no_trend_line(self):
        patient = PatientDemographics(patient_id="demo", age=55, sex="male")
        chart = build_marker_chart(
            "crp",
            LabRecord(test_name="crp", value=2.4, unit="mg/dL", collected_at="2026-06-26"),
            patient,
            [],
        )
        self.assertIsNotNone(chart)
        self.assertEqual(chart.trend, [])
        self.assertEqual(chart.range_position, "above")


if __name__ == "__main__":
    unittest.main()
