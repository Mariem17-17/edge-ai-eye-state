import pytest
from pathlib import Path
from PIL import Image


from src.data_audit.inventory_builder import (
    discover_image_files,
    build_dataset_inventory,
    )

def test_discovers_png_files_recursively(tmp_path):
    subject_1 = tmp_path / "subject_1"
    subject_2 = tmp_path / "subject_2" / "nested"

    subject_1.mkdir()
    subject_2.mkdir(parents=True)

    image_1 = subject_1 / "image_1.png"
    image_2 = subject_1 / "image_2.png"
    image_3 = subject_2 / "image_3.png"

    image_1.touch()
    image_2.touch()
    image_3.touch()

    discovered_files = discover_image_files(tmp_path)

    assert discovered_files == sorted([image_1, image_2, image_3])

def test_unsupported_files_are_ignored(tmp_path):
    subject_1 = tmp_path / "subject_1"
    subject_2 = tmp_path / "subject_2" / "nested"

    subject_1.mkdir()
    subject_2.mkdir(parents=True)

    image = subject_1 / "image.png"
    text = subject_1 / "notes.txt"
    csv_file = subject_2 / "metadata.csv"

    image.touch()
    text.touch()
    csv_file.touch()

    discovered_files = discover_image_files(tmp_path)

    assert discovered_files == [image]

def test_accepts_uppercase_png_extension(tmp_path):
    image_path = tmp_path / "image.PNG"
    image_path.touch()

    discovered_files = discover_image_files(tmp_path)

    assert discovered_files == [image_path]

def test_rejects_missing_dataset_root(tmp_path):
    missing_root = tmp_path / "missing"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        discover_image_files(missing_root)


def test_rejects_file_as_dataset_root(tmp_path):
    file_path = tmp_path / "file.png"
    file_path.touch()
    with pytest.raises(NotADirectoryError, match="not a directory"):
        discover_image_files(file_path)

def test_returns_empty_list_for_empty_directory(tmp_path):
    discovered_files = discover_image_files(tmp_path)

    assert discovered_files == []


def test_builds_inventory_record(tmp_path):
    image_dir = tmp_path / "train" / "open"
    image_dir.mkdir(parents=True)

    image_path = (image_dir / "s0001_01842_0_0_1_0_0_01.png")
    Image.new(
    mode="L",
    size=(80, 40),
    color=128,
    ).save(image_path)

    inventory, failures = build_dataset_inventory(tmp_path)
    expected_relative_path = str(Path("train")/ "open"/ "s0001_01842_0_0_1_0_0_01.png")
    assert len(inventory) == 1

    record = inventory[0]

    assert failures == []

    assert record["subject_id"] == "s0001"
    assert record["image_id"] == "01842"
    assert record["gender"] == 0
    assert record["glasses"] == 0
    assert record["eye_state"] == 1
    assert record["reflections"] == 0
    assert record["lighting"] == 0
    assert record["sensor_id"] == "01"
    assert record["extension"] == ".png"
    assert record["relative_path"] == expected_relative_path

    assert record["width"] == 80
    assert record["height"] == 40
    assert record["channels"] == 1
    assert record["image_mode"] == "L"
    assert record["file_size_bytes"] == image_path.stat().st_size


def test_builds_multiple_inventory_records(tmp_path):
    image1_dir = tmp_path / "train" / "open"
    image2_dir = tmp_path / "train" / "closed"
    image3_dir = tmp_path / "validation" / "open"

    image1_dir.mkdir(parents=True)
    image2_dir.mkdir(parents=True)
    image3_dir.mkdir(parents=True)

    image1_path = (image1_dir / "s0001_00001_0_0_1_0_0_01.png")
    Image.new(
    mode="L",
    size=(80, 40),
    color=128,
    ).save(image1_path)

    image2_path = (image2_dir / "s0001_00002_0_0_0_0_0_01.png")
    Image.new(
    mode="L",
    size=(64, 32),
    color=100,
    ).save(image2_path)

    image3_path = (image3_dir / "s0002_00003_1_1_1_1_1_02.png")
    Image.new(
    mode="RGB",
    size=(96, 48),
    color=(120, 150, 200),
    ).save(image3_path)

    inventory, failures = build_dataset_inventory(tmp_path)

    assert len(inventory) == 3

    assert failures == []

    assert inventory[0]["image_id"] == "00002"
    assert inventory[0]["eye_state"] == 0

    assert inventory[1]["image_id"] == "00001"
    assert inventory[1]["eye_state"] == 1

    assert inventory[2]["subject_id"] == "s0002"
    assert inventory[2]["image_id"] == "00003"
    assert inventory[2]["gender"] == 1
    assert inventory[2]["glasses"] == 1
    assert inventory[2]["sensor_id"] == "02"

    assert inventory[0]["width"] == 64
    assert inventory[0]["height"] == 32

    assert inventory[1]["width"] == 80
    assert inventory[1]["channels"] == 1

    assert inventory[2]["width"] == 96
    assert inventory[2]["height"] == 48
    assert inventory[2]["channels"] == 3
    assert inventory[2]["image_mode"] == "RGB"

def test_build_inventory_returns_empty_list_for_empty_directory(tmp_path,):
    inventory, failures = build_dataset_inventory(tmp_path)

    assert inventory == []
    assert failures == []


def test_build_inventory_ignores_unsupported_files(tmp_path):
    image_dir = tmp_path / "train" / "open"
    text_dir = tmp_path / "train" / "closed"
    csv_dir = tmp_path / "validation" / "open"

    image_dir.mkdir(parents=True)
    text_dir.mkdir(parents=True)
    csv_dir.mkdir(parents=True)

    image_path = (image_dir / "s0001_00001_0_0_1_0_0_01.png")
    Image.new(
    mode="L",
    size=(80, 40),
    color=128,
    ).save(image_path)

    text_path = (text_dir / "text.txt")
    text_path.touch()

    csv_path = (csv_dir / "csv_file.csv")
    csv_path.touch()

    inventory, failures = build_dataset_inventory(tmp_path)
    assert len(inventory) == 1
    assert failures == []


def test_collects_invalid_filename_failure(tmp_path):
    invalid_image = tmp_path / "invalid_image.png"
    invalid_image.touch()

    inventory, failures = build_dataset_inventory(tmp_path)

    assert inventory == []
    assert len(failures) == 1

    assert failures[0]["stage"] == "filename_parsing"
    assert failures[0]["relative_path"] == "invalid_image.png"
    assert "expected 8 components" in failures[0]["error"]

def test_continues_after_invalid_filename(tmp_path):
    valid_image = (tmp_path / "s0001_01842_0_0_1_0_0_01.png")
    invalid_image = tmp_path / "invalid_image.png"

    Image.new(
    mode="L",
    size=(80, 40),
    color=128,
    ).save(valid_image)
    invalid_image.touch()

    inventory, failures = build_dataset_inventory(tmp_path)

    assert len(inventory) == 1
    assert inventory[0]["subject_id"] == "s0001"
    assert inventory[0]["image_id"] == "01842"

    assert len(failures) == 1
    assert failures[0]["relative_path"] == "invalid_image.png"

def test_collects_multiple_filename_failures(tmp_path):
    invalid_image_1 = tmp_path / "invalid_1.png"
    invalid_image_2 = tmp_path / "invalid_2.png"

    invalid_image_1.touch()
    invalid_image_2.touch()

    inventory, failures = build_dataset_inventory(tmp_path)

    assert inventory == []
    assert len(failures) == 2

    failure_paths = {
        failure["relative_path"]
        for failure in failures
    }

    assert failure_paths == {
        "invalid_1.png",
        "invalid_2.png",
    }
    assert all(
    failure["stage"] == "filename_parsing"
    for failure in failures
    )

def test_collects_image_inspection_failure(tmp_path):
    corrupted_image = (tmp_path / "s0001_01842_0_0_1_0_0_01.png")
    corrupted_image.write_text("This is not image data.")

    inventory, failures = build_dataset_inventory(tmp_path)

    assert inventory == []
    assert len(failures) == 1

    failure = failures[0]

    assert failure["relative_path"] == corrupted_image.name
    assert failure["stage"] == "image_inspection"
    assert "Unable to read image" in failure["error"]