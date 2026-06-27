import unittest
import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated.*")
from fastapi.testclient import TestClient

from api.history_store import clear_all_history
from app.main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        clear_all_history()
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "cdss-lab-results"})

    def test_json_analyze_endpoint_returns_rule_response(self):
        response = self.client.post(
            "/api/analyze",
            json={
                "patient": {"patient_id": "demo-001", "age": 32, "sex": "female", "pregnant": False},
                "current_results": [
                    {
                        "test_name": "hemoglobin",
                        "value": 11.4,
                        "unit": "g/dL",
                        "collected_at": "2026-06-26",
                    },
                    {"test_name": "mcv", "value": 78.0, "unit": "fL", "collected_at": "2026-06-26"},
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["overall_urgency"], "monitor")
        self.assertEqual(body["results"][0]["rule_id"], "anemia_hgb_mcv")
        self.assertTrue(body["results"][0]["triggered"])
        self.assertIn("does not provide diagnosis", body["disclaimer"])

    def test_json_analyze_endpoint_rejects_invalid_payload(self):
        response = self.client.post(
            "/api/analyze",
            json={
                "patient": {"patient_id": "demo-001", "age": -1, "sex": "female"},
                "current_results": [],
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_json_analyze_endpoint_rejects_unsupported_test_name(self):
        response = self.client.post(
            "/api/analyze",
            json={
                "patient": {"patient_id": "demo-001", "age": 32, "sex": "female"},
                "current_results": [
                    {
                        "test_name": "vitamin_d",
                        "value": 20,
                        "unit": "mg/dL",
                        "collected_at": "2026-06-26",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Unsupported test_name", response.json()["detail"]["errors"][0]["message"])

    def test_json_analyze_endpoint_accepts_lipid_and_crp_markers(self):
        response = self.client.post(
            "/api/analyze",
            json={
                "patient": {"patient_id": "demo-001", "age": 52, "sex": "female"},
                "current_results": [
                    {"test_name": "ldl", "value": 170.0, "unit": "mg/dL", "collected_at": "2026-06-26"},
                    {"test_name": "hdl", "value": 42.0, "unit": "mg/dL", "collected_at": "2026-06-26"},
                    {"test_name": "crp", "value": 2.5, "unit": "mg/dL", "collected_at": "2026-06-26"},
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual([result["rule_id"] for result in body["results"]], ["lipid_panel", "inflammation_crp"])
        self.assertEqual(body["overall_urgency"], "prompt_review")

    def test_csv_analyze_endpoint_accepts_valid_upload(self):
        csv_text = "\n".join(
            [
                "patient_id,age,sex,test_name,value,unit,collected_at,pregnant,source_label",
                "demo-001,54,male,FPG,130,mg/dL,2026-06-26,,Fasting Glucose",
                "demo-001,54,male,HbA1c,6.6,%,2026-06-26,,HbA1c",
            ]
        )

        response = self.client.post(
            "/api/analyze/csv",
            files={"file": ("labs.csv", csv_text, "text/csv")},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["results"][0]["rule_id"], "glucose_fpg_hba1c")
        self.assertEqual(body["results"][0]["urgency_level"], "prompt_review")

    def test_csv_analyze_endpoint_reports_missing_columns(self):
        csv_text = "\n".join(
            [
                "patient_id,age,sex,test_name,value,unit",
                "demo-001,54,male,FPG,130,mg/dL",
            ]
        )

        response = self.client.post(
            "/api/analyze/csv",
            files={"file": ("labs.csv", csv_text, "text/csv")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Missing required columns", response.json()["detail"]["errors"][0]["message"])

    def test_csv_analyze_endpoint_reports_invalid_number(self):
        csv_text = "\n".join(
            [
                "patient_id,age,sex,test_name,value,unit,collected_at",
                "demo-001,54,male,FPG,not-a-number,mg/dL,2026-06-26",
            ]
        )

        response = self.client.post(
            "/api/analyze/csv",
            files={"file": ("labs.csv", csv_text, "text/csv")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["errors"][0]["field"], "value")

    def test_csv_analyze_endpoint_reports_unsupported_test(self):
        csv_text = "\n".join(
            [
                "patient_id,age,sex,test_name,value,unit,collected_at",
                "demo-001,54,male,vitamin_d,20,ng/mL,2026-06-26",
            ]
        )

        response = self.client.post(
            "/api/analyze/csv",
            files={"file": ("labs.csv", csv_text, "text/csv")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Unsupported test_name", response.json()["detail"]["errors"][0]["message"])

    def test_history_endpoints_save_read_and_delete_records(self):
        save_response = self.client.post(
            "/api/history/demo-001",
            json={
                "records": [
                    {"test_name": "hemoglobin", "value": 13.8, "unit": "g/dL", "collected_at": "2026-05-01"},
                ]
            },
        )

        self.assertEqual(save_response.status_code, 200)
        self.assertEqual(save_response.json()["count"], 1)

        get_response = self.client.get("/api/history/demo-001")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["records"][0]["test_name"], "hemoglobin")

        delete_response = self.client.delete("/api/history/demo-001")
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json()["deleted_count"], 1)

        empty_response = self.client.get("/api/history/demo-001")
        self.assertEqual(empty_response.json()["count"], 0)

    def test_analyze_can_use_saved_history_for_trend_checks(self):
        self.client.post(
            "/api/history/demo-002",
            json={
                "records": [
                    {"test_name": "hemoglobin", "value": 14.0, "unit": "g/dL", "collected_at": "2026-05-01"},
                ]
            },
        )

        response = self.client.post(
            "/api/analyze?use_saved_history=true",
            json={
                "patient": {"patient_id": "demo-002", "age": 30, "sex": "female"},
                "current_results": [
                    {"test_name": "hemoglobin", "value": 12.4, "unit": "g/dL", "collected_at": "2026-06-26"},
                    {"test_name": "mcv", "value": 88.0, "unit": "fL", "collected_at": "2026-06-26"},
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        anemia = response.json()["results"][0]
        self.assertEqual(anemia["rule_id"], "anemia_hgb_mcv")
        self.assertTrue(anemia["triggered"])
        self.assertTrue(any("trend threshold" in item for item in anemia["evidence"]))

    def test_saved_history_requires_patient_id_when_requested(self):
        response = self.client.post(
            "/api/analyze?use_saved_history=true",
            json={
                "patient": {"age": 30, "sex": "female"},
                "current_results": [
                    {"test_name": "hemoglobin", "value": 13.0, "unit": "g/dL", "collected_at": "2026-06-26"},
                ],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("patient_id is required", response.json()["detail"]["errors"][0]["message"])


if __name__ == "__main__":
    unittest.main()
