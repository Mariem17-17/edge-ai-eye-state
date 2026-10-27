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
    summarize_inventory,
    summarize_subjects,
    summarize_subject_statistics,
    create_subject_table,
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


def test_summarizes_inventory_distributions():
    records = [
        {
            "subject_id": "s0001",
            "eye_state": 1,
            "gender": 0,
            "glasses": 0,
            "reflections": 0,
            "lighting": 1,
            "image_mode": "L",
            "channels": 1,
            "sensor_id": "01",
        },
        {
            "subject_id": "s0001",
            "eye_state": 0,
            "gender": 0,
            "glasses": 1,
            "reflections": 1,
            "lighting": 0,
            "image_mode": "L",
            "channels": 1,
            "sensor_id": "01",
        },
        {
            "subject_id": "s0002",
            "eye_state": 1,
            "gender": 1,
            "glasses": 0,
            "reflections": 2,
            "lighting": 1,
            "image_mode": "RGB",
            "channels": 3,
            "sensor_id": "02",
        },
    ]

    summary = summarize_inventory(records)

    assert summary["total_images"] == 3
    assert summary["unique_subjects"] == 2

    assert summary["eye_state_counts"] == {
        0: 1,
        1: 2,
    }

    assert summary["gender_counts"] == {
        0: 2,
        1: 1,
    }

    assert summary["glasses_counts"] == {
        0: 2,
        1: 1,
    }

    assert summary["reflections_counts"] == {
        0: 1,
        1: 1,
        2: 1,
    }

    assert summary["lighting_counts"] == {
        0: 1,
        1: 2,
    }

    assert summary["image_mode_counts"] == {
        "L": 2,
        "RGB": 1,
    }

    assert summary["channel_counts"] == {
        1: 2,
        3: 1,
    }

    assert summary["sensor_counts"] == {
        "01": 2,
        "02": 1,
    }


def test_counts_unique_subjects_only_once():
    records = [
        {
            "subject_id": "s0001",
            "eye_state": 1,
            "gender": 0,
            "glasses": 0,
            "reflections": 0,
            "lighting": 1,
            "image_mode": "L",
            "channels": 1,
            "sensor_id": "01",
        },
        {
            "subject_id": "s0001",
            "eye_state": 0,
            "gender": 0,
            "glasses": 0,
            "reflections": 0,
            "lighting": 1,
            "image_mode": "L",
            "channels": 1,
            "sensor_id": "01",
        },
    ]

    summary = summarize_inventory(records)

    assert summary["total_images"] == 2
    assert summary["unique_subjects"] == 1


def test_returns_empty_summary_for_empty_inventory():
    summary = summarize_inventory([])

    assert summary == {
        "total_images": 0,
        "unique_subjects": 0,
        "eye_state_counts": {},
        "gender_counts": {},
        "glasses_counts": {},
        "reflections_counts": {},
        "lighting_counts": {},
        "image_mode_counts": {},
        "channel_counts": {},
        "sensor_counts": {},
    }

def test_summary_distribution_counts_match_total():
    records = [
        {
            "subject_id": "s0001",
            "eye_state": 1,
            "gender": 0,
            "glasses": 0,
            "reflections": 0,
            "lighting": 1,
            "image_mode": "L",
            "channels": 1,
            "sensor_id": "01",
        },
        {
            "subject_id": "s0002",
            "eye_state": 0,
            "gender": 1,
            "glasses": 1,
            "reflections": 2,
            "lighting": 0,
            "image_mode": "L",
            "channels": 1,
            "sensor_id": "02",
        },
    ]

    summary = summarize_inventory(records)
    total = summary["total_images"]

    distribution_keys = [
        "eye_state_counts",
        "gender_counts",
        "glasses_counts",
        "reflections_counts",
        "lighting_counts",
        "image_mode_counts",
        "channel_counts",
        "sensor_counts",
    ]

    for key in distribution_keys:
        assert sum(summary[key].values()) == total


def test_summarizes_records_per_subject():
    records = [
        {
            "subject_id": "s0001",
            "eye_state": 1,
            "glasses": 0,
            "reflections": 0,
            "lighting": 1,
            "sensor_id": "01",
        },
        {
            "subject_id": "s0001",
            "eye_state": 0,
            "glasses": 1,
            "reflections": 2,
            "lighting": 0,
            "sensor_id": "01",
        },
    ]

    summaries = summarize_subjects(records)

    assert len(summaries) == 1
    assert "s0001" in summaries

    subject = summaries["s0001"]

    assert subject["total_images"] == 2
    assert subject["eye_state_counts"] == {
        0: 1,
        1: 1,
    }
    assert subject["glasses_counts"] == {
        0: 1,
        1: 1,
    }
    assert subject["reflection_counts"] == {
        0: 1,
        2: 1,
    }
    assert subject["lighting_counts"] == {
        0: 1,
        1: 1,
    }
    assert subject["sensor_counts"] == {
        "01": 2,
    }


def test_separates_different_subjects():
    records = [
        {
            "subject_id": "s0001",
            "eye_state": 1,
            "glasses": 0,
            "reflections": 0,
            "lighting": 1,
            "sensor_id": "01",
        },
        {
            "subject_id": "s0002",
            "eye_state": 0,
            "glasses": 1,
            "reflections": 1,
            "lighting": 0,
            "sensor_id": "02",
        },
    ]

    summaries = summarize_subjects(records)

    assert len(summaries) == 2

    assert summaries["s0001"]["total_images"] == 1
    assert summaries["s0002"]["total_images"] == 1

    assert summaries["s0001"]["eye_state_counts"] == {
        1: 1,
    }
    assert summaries["s0002"]["eye_state_counts"] == {
        0: 1,
    }

    assert summaries["s0001"]["sensor_counts"] == {
        "01": 1,
    }
    assert summaries["s0002"]["sensor_counts"] == {
        "02": 1,
    }


def test_counts_multiple_sensors_per_subject():
    records = [
        {
            "subject_id": "s0001",
            "eye_state": 1,
            "glasses": 0,
            "reflections": 0,
            "lighting": 1,
            "sensor_id": "01",
        },
        {
            "subject_id": "s0001",
            "eye_state": 1,
            "glasses": 0,
            "reflections": 0,
            "lighting": 1,
            "sensor_id": "02",
        },
        {
            "subject_id": "s0001",
            "eye_state": 0,
            "glasses": 0,
            "reflections": 1,
            "lighting": 0,
            "sensor_id": "01",
        },
    ]

    summaries = summarize_subjects(records)
    subject = summaries["s0001"]

    assert subject["sensor_counts"] == {
        "01": 2,
        "02": 1,
    }

def test_summarizes_empty_subject_inventory():
    summaries = summarize_subjects([])

    assert summaries == {}

def test_subject_distribution_counts_match_total():
    records = [
        {
            "subject_id": "s0001",
            "eye_state": 1,
            "glasses": 0,
            "reflections": 0,
            "lighting": 1,
            "sensor_id": "01",
        },
        {
            "subject_id": "s0001",
            "eye_state": 0,
            "glasses": 1,
            "reflections": 2,
            "lighting": 0,
            "sensor_id": "02",
        },
    ]

    summaries = summarize_subjects(records)
    subject = summaries["s0001"]
    total = subject["total_images"]

    distribution_keys = [
        "eye_state_counts",
        "glasses_counts",
        "reflection_counts",
        "lighting_counts",
        "sensor_counts",
    ]

    for key in distribution_keys:
        assert sum(subject[key].values()) == total

def test_summarizes_subject_statistics():
    subject_summaries = {
        "s0001": {
            "total_images": 100,
            "eye_state_counts": {
                0: 40,
                1: 60,
            },
            "sensor_counts": {
                "01": 100,
            },
        },
        "s0002": {
            "total_images": 200,
            "eye_state_counts": {
                0: 120,
                1: 80,
            },
            "sensor_counts": {
                "01": 150,
                "02": 50,
            },
        },
        "s0003": {
            "total_images": 300,
            "eye_state_counts": {
                0: 200,
                1: 100,
            },
            "sensor_counts": {
                "03": 300,
            },
        },
    }

    statistics = summarize_subject_statistics(
        subject_summaries
    )

    assert statistics["total_subjects"] == 3
    assert statistics["min_images_per_subject"] == 100
    assert statistics["max_images_per_subject"] == 300
    assert statistics["mean_images_per_subject"] == 200
    assert statistics["median_images_per_subject"] == 200

    assert statistics["subjects_with_min_images"] == ["s0001"]
    assert statistics["subjects_with_max_images"] == ["s0003"]

    assert statistics["subjects_missing_open_images"] == []
    assert statistics["subjects_missing_closed_images"] == []

    assert statistics["subjects_by_sensor"] == {
        "01": ["s0001", "s0002"],
        "02": ["s0002"],
        "03": ["s0003"],
    }

def test_identifies_subjects_missing_eye_states():
    subject_summaries = {
        "s0001": {
            "total_images": 100,
            "eye_state_counts": {
                1: 100,
            },
            "sensor_counts": {
                "01": 100,
            },
        },
        "s0002": {
            "total_images": 150,
            "eye_state_counts": {
                0: 150,
            },
            "sensor_counts": {
                "02": 150,
            },
        },
        "s0003": {
            "total_images": 200,
            "eye_state_counts": {
                0: 100,
                1: 100,
            },
            "sensor_counts": {
                "03": 200,
            },
        },
    }

    statistics = summarize_subject_statistics(subject_summaries)

    assert statistics["subjects_missing_open_images"] == ["s0002"]
    assert statistics["subjects_missing_closed_images"] == ["s0001"]

def test_identifies_tied_minimum_and_maximum_subjects():
    subject_summaries = {
        "s0001": {
            "total_images": 100,
            "eye_state_counts": {
                0: 50,
                1: 50,
            },
            "sensor_counts": {
                "01": 100,
            },
        },
        "s0002": {
            "total_images": 100,
            "eye_state_counts": {
                0: 50,
                1: 50,
            },
            "sensor_counts": {
                "01": 100,
            },
        },
        "s0003": {
            "total_images": 300,
            "eye_state_counts": {
                0: 150,
                1: 150,
            },
            "sensor_counts": {
                "02": 300,
            },
        },
        "s0004": {
            "total_images": 300,
            "eye_state_counts": {
                0: 150,
                1: 150,
            },
            "sensor_counts": {
                "03": 300,
            },
        },
    }

    statistics = summarize_subject_statistics(subject_summaries)

    assert statistics["subjects_with_min_images"] == ["s0001","s0002",]
    assert statistics["subjects_with_max_images"] == ["s0003","s0004",]

def test_returns_empty_subject_statistics():
    statistics = summarize_subject_statistics({})

    assert statistics == {
        "total_subjects": 0,
        "min_images_per_subject": 0,
        "max_images_per_subject": 0,
        "mean_images_per_subject": 0,
        "median_images_per_subject": 0,
        "subjects_with_min_images": [],
        "subjects_with_max_images": [],
        "subjects_missing_open_images": [],
        "subjects_missing_closed_images": [],
        "subjects_by_sensor": {},
    }

def test_creates_flat_subject_record():
    subject_summaries = {
        "s0001": {
            "total_images": 10,
            "eye_state_counts": {
                0: 4,
                1: 6,
            },
            "glasses_counts": {
                0: 7,
                1: 3,
            },
            "reflection_counts": {
                0: 5,
                1: 2,
                2: 3,
            },
            "lighting_counts": {
                0: 6,
                1: 4,
            },
            "sensor_counts": {
                "01": 8,
                "02": 2,
            },
        }
    }

    subject_table = create_subject_table(
        subject_summaries
    )

    assert subject_table == [
        {
            "subject_id": "s0001",
            "total_images": 10,
            "closed_images": 4,
            "open_images": 6,
            "without_glasses": 7,
            "with_glasses": 3,
            "no_reflections": 5,
            "small_reflections": 2,
            "big_reflections": 3,
            "bad_lighting": 6,
            "good_lighting": 4,
            "sensor_01_images": 8,
            "sensor_02_images": 2,
            "sensor_03_images": 0,
        }
    ]

def test_sorts_subject_table_by_subject_id():
    subject_summaries = {
        "s0003": {
            "total_images": 1,
            "eye_state_counts": {1: 1},
            "glasses_counts": {0: 1},
            "reflection_counts": {0: 1},
            "lighting_counts": {1: 1},
            "sensor_counts": {"01": 1},
        },
        "s0001": {
            "total_images": 1,
            "eye_state_counts": {0: 1},
            "glasses_counts": {0: 1},
            "reflection_counts": {0: 1},
            "lighting_counts": {0: 1},
            "sensor_counts": {"02": 1},
        },
    }

    subject_table = create_subject_table(subject_summaries)

    subject_ids = [
        record["subject_id"]
        for record in subject_table
    ]

    assert subject_ids == [
        "s0001",
        "s0003",
    ]

def test_returns_empty_subject_table():
    subject_table = create_subject_table({})

    assert subject_table == []

def test_subject_table_counts_match_total():
    subject_summaries = {
        "s0001": {
            "total_images": 10,
            "eye_state_counts": {
                0: 4,
                1: 6,
            },
            "glasses_counts": {
                0: 7,
                1: 3,
            },
            "reflection_counts": {
                0: 5,
                1: 2,
                2: 3,
            },
            "lighting_counts": {
                0: 6,
                1: 4,
            },
            "sensor_counts": {
                "01": 8,
                "02": 2,
            },
        }
    }

    subject_table = create_subject_table(
        subject_summaries
    )
    record = subject_table[0]
    total = record["total_images"]

    assert (
        record["closed_images"]
        + record["open_images"]
        == total
    )

    assert (
        record["without_glasses"]
        + record["with_glasses"]
        == total
    )

    assert (
        record["no_reflections"]
        + record["small_reflections"]
        + record["big_reflections"]
        == total
    )

    assert (
        record["bad_lighting"]
        + record["good_lighting"]
        == total
    )

    assert (
        record["sensor_01_images"]
        + record["sensor_02_images"]
        + record["sensor_03_images"]
        == total
    )