import pytest

from src.data_audit.inventory_builder import discover_image_files

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