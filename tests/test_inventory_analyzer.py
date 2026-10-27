# test_loads_inventory_records
# test_rejects_missing_inventory_csv
# test_rejects_directory_as_inventory_path
# test_rejects_missing_required_columns
# test_rejects_invalid_numeric_value
# test_returns_empty_list_for_header_only_csv
import pytest
import csv

from src.data_audit.csv_exporter import INVENTORY_COLUMNS
from src.data_audit.inventory_analyzer import (
    INTEGER_COLUMNS,
    load_inventory_csv,
)

def write_inventory_csv(csv_path, records, columns=None):
    if columns is None:
        columns = INVENTORY_COLUMNS

    with csv_path.open(
        mode="w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=columns,
        )
        writer.writeheader()
        writer.writerows(records)


def create_valid_inventory_record():
    return {
        "relative_path": (
            "train/open/"
            "s0001_01842_0_0_1_0_0_01.png"
        ),
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

def test_loads_inventory_record(tmp_path):
    csv_path = tmp_path / "dataset_inventory.csv"

    write_inventory_csv(
        csv_path,
        [create_valid_inventory_record()],
    )

    records = load_inventory_csv(csv_path)

    assert len(records) == 1

    record = records[0]

    assert record["relative_path"].endswith(".png")
    assert record["subject_id"] == "s0001"
    assert record["image_id"] == "01842"
    assert record["sensor_id"] == "01"
    assert record["eye_state"] == 1
    assert record["width"] == 80
    assert record["height"] == 40
    assert record["channels"] == 1
    assert record["file_size_bytes"] == 1254


def test_converts_numeric_columns_to_integers(tmp_path):
    csv_path = tmp_path / "dataset_inventory.csv"

    write_inventory_csv(
        csv_path,
        [create_valid_inventory_record()],
    )

    records = load_inventory_csv(csv_path)
    record = records[0]

    for column in INTEGER_COLUMNS:
        assert isinstance(record[column], int)


def test_rejects_missing_inventory_path(tmp_path):
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        load_inventory_csv(missing_path)


def test_rejects_directory_as_inventory_path(tmp_path):
    with pytest.raises(
        IsADirectoryError,
        match="is a directory",
    ):
        load_inventory_csv(tmp_path)


def test_rejects_missing_required_column(tmp_path):
    csv_path = tmp_path / "missing_column.csv"

    record = create_valid_inventory_record()
    record.pop("eye_state")

    columns = [
        column
        for column in INVENTORY_COLUMNS
        if column != "eye_state"
    ]

    write_inventory_csv(
        csv_path,
        [record],
        columns=columns,
    )

    with pytest.raises(ValueError) as exc_info:
        load_inventory_csv(csv_path)

    assert "missing required columns" in str(exc_info.value)
    assert "eye_state" in str(exc_info.value)


def test_rejects_invalid_numeric_value(tmp_path):
    csv_path = tmp_path / "invalid_numeric_value.csv"

    record = create_valid_inventory_record()
    record["width"] = "invalid"

    write_inventory_csv(
        csv_path,
        [record],
    )

    with pytest.raises(
        ValueError,
        match="Invalid numeric value at CSV row 2",
    ):
        load_inventory_csv(csv_path)


def test_reports_later_invalid_csv_row(tmp_path):
    csv_path = tmp_path / "multiple_records.csv"

    first_record = create_valid_inventory_record()

    second_record = create_valid_inventory_record()
    second_record["image_id"] = "01843"
    second_record["width"] = "invalid"

    write_inventory_csv(
        csv_path,
        [first_record, second_record],
    )

    with pytest.raises(
        ValueError,
        match="CSV row 3",
    ):
        load_inventory_csv(csv_path)


def test_returns_empty_list_for_header_only_csv(tmp_path):
    csv_path = tmp_path / "empty_inventory.csv"

    write_inventory_csv(
        csv_path,
        records=[],
    )

    records = load_inventory_csv(csv_path)

    assert records == []


def test_rejects_csv_without_header(tmp_path):
    csv_path = tmp_path / "empty_file.csv"
    csv_path.touch()

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        load_inventory_csv(csv_path)


def test_preserves_identifiers_as_strings(tmp_path):
    csv_path = tmp_path / "dataset_inventory.csv"

    write_inventory_csv(
        csv_path,
        [create_valid_inventory_record()],
    )

    records = load_inventory_csv(csv_path)
    record = records[0]

    assert record["subject_id"] == "s0001"
    assert record["image_id"] == "01842"
    assert record["sensor_id"] == "01"

    assert isinstance(record["subject_id"], str)
    assert isinstance(record["image_id"], str)
    assert isinstance(record["sensor_id"], str)