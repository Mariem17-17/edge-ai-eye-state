
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
    """
    Load and validate inventory records from a CSV file.

    Converts numerical fields to integers while preserving identifiers
    such as image ID and sensor ID as strings.
    """
    records = []
    path = Path(inventory_path)
    if not path.exists():
        raise FileNotFoundError(f"Inventory path does not exist: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Inventory path is a directory {path}")

    with path.open(mode='r', newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = REQUIRED_INVENTORY_COLUMNS - fieldnames
        if missing_columns:
            raise ValueError(f"Inventory CSV is missing required columns : {sorted(missing_columns)}")
        
        for row_number, row in enumerate(reader, start=2):
            try:
                for column in INTEGER_COLUMNS:
                    row[column] = int(row[column])
                    
            except ValueError as exc:
                raise ValueError(f"Invalid numeric value at CSV row {row_number}") from exc
                
            records.append(row)
    return records

