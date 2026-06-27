import unittest
import warnings
from io import BytesIO

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated.*")
from fastapi.testclient import TestClient

from api.history_store import clear_all_history
from app.main import app


def _pdf_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def make_text_pdf(lines: list[str]) -> bytes:
    text_ops = ["BT", "/F1 10 Tf", "72 740 Td", "12 TL"]
    for index, line in enumerate(lines):
        if index:
            text_ops.append("T*")
        text_ops.append(f"({_pdf_escape(line)}) Tj")
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, obj in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{object_number} 0 obj\n".encode())
        output.write(obj)
        output.write(b"\nendobj\n")
    xref_offset = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode())
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode())
    output.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode())
    return output.getvalue()


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

    def test_pdf_analyze_endpoint_accepts_text_pdf_with_csv_rows(self):
        pdf_bytes = make_text_pdf(
            [
                "patient_id,age,sex,test_name,value,unit,collected_at,pregnant,source_label",
                "demo-001,54,male,FPG,130,mg/dL,2026-06-26,false,Fasting Glucose",
                "demo-001,54,male,HbA1c,6.6,%,2026-06-26,false,HbA1c",
            ]
        )

        response = self.client.post(
            "/api/analyze/pdf",
            files={"file": ("labs.pdf", pdf_bytes, "application/pdf")},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["results"][0]["rule_id"], "glucose_fpg_hba1c")
        self.assertEqual(body["overall_urgency"], "prompt_review")

    def test_pdf_analyze_endpoint_rejects_unreadable_pdf(self):
        response = self.client.post(
            "/api/analyze/pdf",
            files={"file": ("labs.pdf", b"not-a-real-pdf", "application/pdf")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("PDF could not be read", response.json()["detail"]["errors"][0]["message"])

    def test_unified_upload_endpoint_detects_csv_and_returns_patient_metadata(self):
        csv_text = "\n".join(
            [
                "patient_id,patient_name,date_of_birth,age,sex,test_name,value,unit,collected_at,pregnant,source_label",
                "demo-010,Alex Demo,1971-03-12,55,female,fasting_glucose,82,mg/dL,2026-04-26,false,Fasting glucose",
                "demo-010,Alex Demo,1971-03-12,55,female,fasting_glucose,90,mg/dL,2026-05-26,false,Fasting glucose",
                "demo-010,Alex Demo,1971-03-12,55,female,fasting_glucose,98,mg/dL,2026-06-26,false,Fasting glucose",
            ]
        )

        response = self.client.post(
            "/api/analyze/upload",
            files={"file": ("labs.csv", csv_text, "text/csv")},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["upload"]["file_type"], "csv")
        self.assertEqual(body["upload"]["patient"]["patient_name"], "Alex Demo")
        self.assertEqual(body["upload"]["patient"]["date_of_birth"], "1971-03-12")
        self.assertEqual(len(body["upload"]["current_results"]), 1)
        self.assertEqual(len(body["upload"]["historical_results"]), 2)
        self.assertEqual(body["results"][0]["rule_id"], "glucose_fpg_hba1c")
        self.assertTrue(body["results"][0]["triggered"])
        self.assertEqual(body["overall_urgency"], "monitor")

    def test_unified_upload_endpoint_detects_pdf(self):
        pdf_bytes = make_text_pdf(
            [
                "patient_id,age,sex,test_name,value,unit,collected_at,pregnant,source_label",
                "demo-011,54,male,FPG,130,mg/dL,2026-06-26,false,Fasting Glucose",
                "demo-011,54,male,HbA1c,6.6,%,2026-06-26,false,HbA1c",
            ]
        )

        response = self.client.post(
            "/api/analyze/upload",
            files={"file": ("labs.pdf", pdf_bytes, "application/pdf")},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["upload"]["file_type"], "pdf")
        self.assertEqual(body["results"][0]["rule_id"], "glucose_fpg_hba1c")

    def test_unified_upload_endpoint_rejects_unsupported_file_type(self):
        response = self.client.post(
            "/api/analyze/upload",
            files={"file": ("labs.txt", b"not,csv", "text/plain")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Unsupported file type", response.json()["detail"]["errors"][0]["message"])

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
