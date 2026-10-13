from pathlib import Path

EXPECTED_COMPONENT_COUNT = 8
ALLOWED_EXTENSIONS = {".png"}

# example image name : "s0001_01842_0_0_1_0_0_01.png"
# subject_id image_id gender glasses eye_state reflections lighting sensor_id

def parse_mrl_filename(path: str | Path):
    
    file_path = Path(path)
    filename_without_extension = file_path.stem
    extension = file_path.suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension {extension!r}. "
            f"Expected one of: {sorted(ALLOWED_EXTENSIONS)}"
        )
    components = filename_without_extension.split("_")   # List of strings: ["s0001", "01842", "0", "0", "1", "0", "0", "01"]
    
    if len(components) != EXPECTED_COMPONENT_COUNT:
        raise ValueError(
        f"Invalid MRL filename {file_path.name!r}: "
        f"expected {EXPECTED_COMPONENT_COUNT} components, "
        f"found {len(components)}"
        )
    
    subject_id =  components[0]
    image_id = components[1]
    sensor_id = components[7]

    if not subject_id.startswith("s"):
        raise ValueError(
            f"Invalid subject ID {subject_id} in {file_path.name}"
        )

    if not image_id.isdigit():
        raise ValueError(
            f"Invalid image ID {image_id} in {file_path.name}"
        )

    try:
        gender = int(components[2])
        glasses = int(components[3])
        eye_state = int(components[4])
        reflections = int(components[5])
        lighting = int(components[6])
    except ValueError as exc:
        raise ValueError(
            f"Invalid numeric metadata in filename {file_path.name}"
            ) from exc
    if eye_state not in {0, 1} :
        raise ValueError(
            f"Invalid eye state {eye_state} in {file_path.name}; expected 0 or 1"
            )

    if gender not in {0, 1}:
        raise ValueError(
            f"Invalid gender value {gender} in {file_path.name}; expected 0 or 1"
            )

    if glasses not in {0, 1}:
        raise ValueError(
            f"Invalid glasses value {glasses} in {file_path.name}; expected 0 or 1"
            )

    if reflections not in {0, 1, 2}:
        raise ValueError(
            f"Invalid reflections value {reflections} in {file_path.name}; expected 0 or 1"
            )


    if lighting not in {0, 1}:
        raise ValueError(
            f"Invalid lighting value {lighting} in {file_path.name}; expected 0 or 1"
            )
    if sensor_id not in {"01", "02", "03"}:
        raise ValueError(
            f"Invalid sensor ID {sensor_id} in {file_path.name}; expected 01, 02 or 03"
            )
            
    metadata = {
        "subject_id": subject_id,
        "image_id": image_id,
        "gender": gender,
        "glasses": glasses,
        "eye_state": eye_state,
        "reflections": reflections,
        "lighting": lighting,
        "sensor_id": sensor_id,
        "extension": extension,
    }

    return metadata