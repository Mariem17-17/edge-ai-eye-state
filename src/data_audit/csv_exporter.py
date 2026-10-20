import csv
from pathlib import Path

INVENTORY_COLUMNS = [
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
]

FAILURE_COLUMNS = [
    "relative_path",
    "stage",
    "error",
]

def write_records_csv(records: list[dict], output_path: str | Path, columns: list[str],) -> Path:
    """
    Write dictionary records to a CSV file using the given columns.
    Returns the path of the generated CSV file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns,)
        writer.writeheader()
        writer.writerows(records)
    return path


def export_audit_results(inventory: list[dict], failures: list[dict], output_directory: str | Path,) -> tuple[Path, Path]:
    """
    Export dataset inventory and processing failures to CSV files.

    Returns the two generated CSV paths.
    """
    path = Path(output_directory)

    dataset_inventory_path = path / "dataset_inventory.csv"
    processing_failure_path = path / "processing_failures.csv"
    
    write_records_csv(
    inventory,
    dataset_inventory_path,
    INVENTORY_COLUMNS,
    )

    write_records_csv(
        failures,
        processing_failure_path,
        FAILURE_COLUMNS,
    )

    return dataset_inventory_path, processing_failure_path

