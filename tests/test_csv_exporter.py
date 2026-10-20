import csv
from src.data_audit.csv_exporter import export_audit_results



def test_exports_inventory_and_failures(tmp_path):
    inventory = [
        {
            "relative_path": "train/open/image.png",
            "subject_id": "s0001",
            "image_id": "01842",
            "gender": 0,
            "glasses": 0,
            "eye_state": 1,
            "reflections": 0,
            "lighting": 0,
            "sensor_id": "01",
            "extension": ".png",
            "width": 80,
            "height": 40,
            "channels": 1,
            "image_mode": "L",
            "file_size_bytes": 1254,
        }
    ]

    failures = [
        {
            "relative_path": "invalid.png",
            "stage": "filename_parsing",
            "error": "Invalid filename",
        }
    ]

    inventory_path, failures_path = export_audit_results(
        inventory,
        failures,
        tmp_path / "metadata",
    )

    assert inventory_path.exists()
    assert failures_path.exists()
    assert inventory_path.name == "dataset_inventory.csv"
    assert failures_path.name == "processing_failures.csv"

    with inventory_path.open(
        newline="",
        encoding="utf-8",
    ) as csv_file:
        inventory_rows = list(csv.DictReader(csv_file))

    assert len(inventory_rows) == 1
    assert inventory_rows[0]["subject_id"] == "s0001"
    assert inventory_rows[0]["image_id"] == "01842"
    assert inventory_rows[0]["eye_state"] == "1"
    assert inventory_rows[0]["width"] == "80"
    assert inventory_rows[0]["sensor_id"] == "01"

    with failures_path.open(
        newline="",
        encoding="utf-8",
    ) as csv_file:
        failure_rows = list(csv.DictReader(csv_file))

    assert len(failure_rows) == 1
    assert failure_rows[0]["relative_path"] == "invalid.png"
    assert failure_rows[0]["stage"] == "filename_parsing"
    assert failure_rows[0]["error"] == "Invalid filename"


def test_exports_failure_headers_when_no_failures_exist(tmp_path):
    inventory = []
    failures = []

    _, failures_path = export_audit_results(
        inventory,
        failures,
        tmp_path / "metadata",
    )

    with failures_path.open(
        newline="",
        encoding="utf-8",
    ) as csv_file:
        rows = list(csv.reader(csv_file))

    assert rows == [["relative_path", "stage", "error"]]