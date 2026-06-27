# Example Upload Files

These files contain synthetic data only. They are formatted for the app's CSV upload flow.

Use the frontend at `http://127.0.0.1:5173/`, choose one of these CSV files, and submit it through the single upload form.

To try PDF upload, create a text-based PDF from one of these CSV files. On macOS, open the CSV in a text editor, choose Print, then Save as PDF. The same upload control accepts that PDF. The PDF upload path only supports readable text that still contains these CSV-compatible rows; scanned/image PDFs are not supported.

## Files

- `normal_panel.csv`: normal example across the implemented rule families.
- `anemia_glucose_kidney_alerts.csv`: low hemoglobin, diabetes-range glucose markers, and reduced eGFR.
- `glucose_trend_upload.csv`: fasting glucose values that remain below 100 mg/dL but rise across three dated records.
- `lipids_crp_alerts.csv`: lipid and CRP values that trigger review.
- `urgent_mixed_panel.csv`: severe triglycerides, very low eGFR, and severe CRP elevation.

All examples use the required CSV columns:

- `patient_id`
- `age`
- `sex`
- `test_name`
- `value`
- `unit`
- `collected_at`

Optional columns included:

- `pregnant`
- `source_label`
- `patient_name`
- `date_of_birth`
