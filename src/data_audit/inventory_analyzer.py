
from pathlib import Path
import csv

REQUIRED_INVENTORY_COLUMNS = {
    "relative_path",
    "subject_id",
    "image_id",
    "gender",
    "glasses",
    "eye_state",
    "reflections",
    "lighting",
    "sensor_id",
    "extension",
    "width",
    "height",
    "channels",
    "image_mode",
    "file_size_bytes",
}

INTEGER_COLUMNS = {
    "gender",
    "glasses",
    "eye_state",
    "reflections",
    "lighting",
    "width",
    "height",
    "channels",
    "file_size_bytes",
}


def load_inventory_csv(inventory_path: str | Path,) -> list[dict]:
    # Convert the path into Path
    # Reject a missing path
    # Reject a directory passed instead of a CSV file
    # Open the file with UTF-8 encoding
    # Read it using csv.DictReader
    # Verify the required columns
    # Convert numeric values into integers
    # Preserve identifiers such as image_id="01842" and sensor_id="01" as strings
    # Return all records

    path = Path(inventory_path)
    if not path.exists():
        raise FileNotFoundError(f"Iventory path does not exist {path} ")
    if path.is_dir():
        raise IsADirectoryError(f"Inventory path is a directory {path}")

    with path.open(mode='r', newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = REQUIRED_INVENTORY_COLUMNS - fieldnames
        if missing_columns:
            raise ValueError(f"Inventory CSV is missing required columns : {sorted(missing_columns)}")
        for column in INTEGER_COLUMNS:
            for row_number, row in enumerate(reader, start=2):
                try:
                    row[column] = int(row[column])
                except ValueError as exc:
                    raise ValueError(f"Invalid numeric value at CSV row {row_number}") from exc



    