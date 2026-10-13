import pytest # for testing exceptions

from src.data_audit.filename_parser import parse_mrl_filename

def test_parse_valid_filename():
    metadata = parse_mrl_filename("s0001_01842_0_0_1_0_0_01.png")
    
    assert metadata["subject_id"] == "s0001"
    assert metadata["image_id"] == "01842"
    assert metadata["gender"] == 0
    assert metadata["glasses"] == 0
    assert metadata["eye_state"] == 1
    assert metadata["reflections"] == 0
    assert metadata["lighting"] == 0
    assert metadata["sensor_id"] == "01"
    assert metadata["extension"] == ".png"


def test_rejects_invalid_sensor_id():
    with pytest.raises(ValueError, match="sensor ID"):
        parse_mrl_filename("s0001_01842_0_0_1_0_0_07.png")


def test_rejects_invalid_subject_id():
    with pytest.raises(ValueError, match="subject ID"):
        parse_mrl_filename("m0001_01842_0_0_1_0_0_02.png")


def test_rejects_invalid_image_id():
    with pytest.raises(ValueError, match="image ID"):
        parse_mrl_filename("s0001_01mm2_0_0_1_0_0_02.png")

def test_rejects_out_of_range_gender():
    with pytest.raises(ValueError, match="gender"):
        parse_mrl_filename("s0001_01842_3_0_1_0_0_02.png")


def test_rejects_invalid_glasses():
    with pytest.raises(ValueError, match="glasses"):
        parse_mrl_filename("s0001_01842_0_3_1_0_0_02.png")

def test_rejects_non_numeric_gender():
    with pytest.raises(ValueError, match="numeric metadata"):
        parse_mrl_filename("s0001_01842_n_0_1_0_0_02.png")


def test_rejects_invalid_eye_state():
    with pytest.raises(ValueError, match="eye state"):
        parse_mrl_filename("s0001_01842_0_0_3_0_0_02.png")

def test_rejects_invalid_reflections():
    with pytest.raises(ValueError, match="reflections"):
        parse_mrl_filename("s0001_01842_0_0_1_4_0_02.png")

def test_rejects_invalid_lighting():
    with pytest.raises(ValueError, match="lighting"):
        parse_mrl_filename("s0001_01842_0_0_1_2_3_02.png")

def test_rejects_invalid_extension():
    with pytest.raises(ValueError, match="Unsupported file extension"):
        parse_mrl_filename("s0001_01842_0_0_1_2_0_02.jpeg")

def test_rejects_incorrect_component_count():
    with pytest.raises(ValueError, match="expected 8 components"):
        parse_mrl_filename("s0001_01842_0_0.png")