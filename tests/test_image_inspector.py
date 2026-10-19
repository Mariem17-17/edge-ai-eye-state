from PIL import Image
import pytest
from pathlib import Path

from src.data_audit.inventory_builder import inspect_image_file

def test_inspects_grayscale_image(tmp_path):
    image_path = tmp_path / "grayscale.png"

    image = Image.new(
        mode="L",
        size=(80, 40),
        color=128,
    )
    image.save(image_path)

    image_info = inspect_image_file(image_path)

    assert image_info["width"] == 80
    assert image_info["height"] == 40
    assert image_info["channels"] == 1
    assert image_info["image_mode"] == "L"
    assert image_info["file_size_bytes"] == image_path.stat().st_size


def test_inspects_rgb_image(tmp_path):
    image_path = tmp_path / "rgb.png"

    image = Image.new(
        mode="RGB",
        size=(80, 40),
        color=(128, 155, 228),
    )
    image.save(image_path)

    image_info = inspect_image_file(image_path)

    assert image_info["width"] == 80
    assert image_info["height"] == 40
    assert image_info["channels"] == 3
    assert image_info["image_mode"] == "RGB"
    assert image_info["file_size_bytes"] == image_path.stat().st_size


def test_inspects_rgba_image(tmp_path):
    image_path = tmp_path / "rgba.png"

    image = Image.new(
        mode="RGBA",
        size=(80, 40),
        color=(128, 155, 228, 18),
    )
    image.save(image_path)

    image_info = inspect_image_file(image_path)

    assert image_info["width"] == 80
    assert image_info["height"] == 40
    assert image_info["channels"] == 4
    assert image_info["image_mode"] == "RGBA"
    assert image_info["file_size_bytes"] == image_path.stat().st_size

def test_rejects_missing_image_path(tmp_path):
    file_path = tmp_path / "file.png"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        inspect_image_file(file_path)


def test_rejects_directory_as_image_path(tmp_path):
    with pytest.raises(IsADirectoryError, match="not a file"):
        inspect_image_file(tmp_path)


def test_rejects_non_image_file(tmp_path):
    fake_image = tmp_path / "fake.png"
    fake_image.write_text("This is not image data.")
    with pytest.raises(ValueError, match="Unable to read image"):
        inspect_image_file(fake_image)


def test_rejects_truncated_image(tmp_path):
    image_path = tmp_path / "truncated.png"

    image = Image.new(
        mode="RGB",
        size=(80, 40),
        color=(128, 155, 228),
    )
    image.save(image_path)

    image_bytes = image_path.read_bytes() # returns a bytes object
    image_path.write_bytes(image_bytes[: len(image_bytes) // 2])

    with pytest.raises(ValueError,match="Unable to read image",):
        inspect_image_file(image_path)