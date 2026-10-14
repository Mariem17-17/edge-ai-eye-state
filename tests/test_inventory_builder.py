import pytest
from pathlib import Path

from src.data_audit.inventory_builder import discover_image_files
from src.data_audit.inventory_builder import build_dataset_inventory

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
    image_path.touch()

    inventory = build_dataset_inventory(tmp_path)
    expected_relative_path = str(Path("train")/ "open"/ "s0001_01842_0_0_1_0_0_01.png")
    assert len(inventory) == 1

    record = inventory[0]

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


def test_builds_multiple_inventory_records(tmp_path):
    image1_dir = tmp_path / "train" / "open"
    image2_dir = tmp_path / "train" / "closed"
    image3_dir = tmp_path / "validation" / "open"

    image1_dir.mkdir(parents=True)
    image2_dir.mkdir(parents=True)
    image3_dir.mkdir(parents=True)

    image1_path = (image1_dir / "s0001_00001_0_0_1_0_0_01.png")
    image1_path.touch()

    image2_path = (image2_dir / "s0001_00002_0_0_0_0_0_01.png")
    image2_path.touch()

    image3_path = (image3_dir / "s0002_00003_1_1_1_1_1_02.png")
    image3_path.touch()

    inventory = build_dataset_inventory(tmp_path)

    assert len(inventory) == 3
    assert inventory[0]["image_id"] == "00002"
    assert inventory[0]["eye_state"] == 0

    assert inventory[1]["image_id"] == "00001"
    assert inventory[1]["eye_state"] == 1

    assert inventory[2]["subject_id"] == "s0002"
    assert inventory[2]["image_id"] == "00003"
    assert inventory[2]["gender"] == 1
    assert inventory[2]["glasses"] == 1
    assert inventory[2]["sensor_id"] == "02"

def test_build_inventory_returns_empty_list_for_empty_directory(tmp_path,):
    inventory = build_dataset_inventory(tmp_path)

    assert inventory == []


def test_build_inventory_ignores_unsupported_files(tmp_path):
    image_dir = tmp_path / "train" / "open"
    text_dir = tmp_path / "train" / "closed"
    csv_dir = tmp_path / "validation" / "open"

    image_dir.mkdir(parents=True)
    text_dir.mkdir(parents=True)
    csv_dir.mkdir(parents=True)

    image_path = (image_dir / "s0001_00001_0_0_1_0_0_01.png")
    image_path.touch()

    text_path = (text_dir / "text.txt")
    text_path.touch()

    csv_path = (csv_dir / "csv_file.csv")
    csv_path.touch()

    inventory = build_dataset_inventory(tmp_path)
    assert len(inventory) == 1


def test_build_inventory_rejects_invalid_filename(tmp_path):
    invalid_image = tmp_path / "invalid_image.png"
    invalid_image.touch()

    with pytest.raises(ValueError,match="expected 8 components",):
        build_dataset_inventory(tmp_path)
