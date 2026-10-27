
from pathlib import Path
import csv
from collections import Counter
from statistics import mean, median

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

SUBJECT_TABLE_COLUMNS = [
    "subject_id",
    "total_images",
    "closed_images",
    "open_images",
    "without_glasses",
    "with_glasses",
    "no_reflections",
    "small_reflections",
    "big_reflections",
    "bad_lighting",
    "good_lighting",
    "sensor_01_images",
    "sensor_02_images",
    "sensor_03_images",
]

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

def summarize_inventory(records: list[dict],) -> dict:
    """
    Summarize the main distributions in dataset inventory records.
    """
    subject_ids = set()
    eye_state_counts = Counter()
    sensor_counts = Counter()
    gender_counts = Counter()
    glasses_counts = Counter()
    reflections_counts = Counter()
    lighting_counts = Counter()
    image_mode_counts = Counter()
    channel_counts = Counter()

    for record in records:
        subject_ids.add(record["subject_id"])
        eye_state_counts[record["eye_state"]] += 1
        sensor_counts[record["sensor_id"]] += 1
        gender_counts[record["gender"]] += 1
        glasses_counts[record["glasses"]] += 1
        reflections_counts[record["reflections"]] += 1
        lighting_counts[record["lighting"]] += 1
        image_mode_counts[record["image_mode"]] += 1
        channel_counts[record["channels"]] += 1


    summary = {
        "total_images": len(records),
        "unique_subjects": len(subject_ids),
        "eye_state_counts": dict(eye_state_counts),
        "gender_counts": dict(gender_counts),
        "glasses_counts": dict(glasses_counts),
        "reflections_counts": dict(reflections_counts),
        "lighting_counts": dict(lighting_counts),
        "image_mode_counts": dict(image_mode_counts),
        "channel_counts": dict(channel_counts),
        "sensor_counts": dict(sensor_counts),
    }

    return summary


def summarize_subjects(records: list[dict],) -> dict[str, dict]:
    """
    Summarize image and acquisition-condition distributions per subject.
    """
    subject_summaries = {}

    for record in records:
        subject_id = record["subject_id"]

        if subject_id not in subject_summaries:
            subject_summaries[subject_id] = {
                "total_images": 0,
                "eye_state_counts": Counter(),
                "glasses_counts": Counter(),
                "reflection_counts": Counter(),
                "lighting_counts": Counter(),
                "sensor_counts": Counter(),
            }

        subject_summary = subject_summaries[subject_id]

        subject_summary["total_images"] += 1
        subject_summary["eye_state_counts"][record["eye_state"]] += 1
        subject_summary["glasses_counts"][record["glasses"]] += 1
        subject_summary["reflection_counts"][record["reflections"]] += 1
        subject_summary["lighting_counts"][record["lighting"]] += 1
        subject_summary["sensor_counts"][record["sensor_id"]] += 1

    for subject_summary in subject_summaries.values():
        subject_summary["eye_state_counts"] = dict(subject_summary["eye_state_counts"])
        subject_summary["glasses_counts"] = dict(subject_summary["glasses_counts"])
        subject_summary["reflection_counts"] = dict(subject_summary["reflection_counts"])
        subject_summary["lighting_counts"] = dict(subject_summary["lighting_counts"])
        subject_summary["sensor_counts"] = dict(subject_summary["sensor_counts"])

    return subject_summaries


def summarize_subject_statistics(subject_summaries: dict[str, dict],) -> dict:
    """
    Summarize dataset-level statistics across subjects.
    """
    if not subject_summaries:
        return {
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

    subject_sizes = {
        subject_id: summary["total_images"]
        for subject_id, summary in subject_summaries.items()
    }

    min_images = min(subject_sizes.values())
    max_images = max(subject_sizes.values())

    subjects_with_min_images = sorted(
        subject_id
        for subject_id, image_count in subject_sizes.items()
        if image_count == min_images
    )

    subjects_with_max_images = sorted(
        subject_id
        for subject_id, image_count in subject_sizes.items()
        if image_count == max_images
    )

    subjects_missing_open_images = sorted(
        subject_id
        for subject_id, summary in subject_summaries.items()
        if summary["eye_state_counts"].get(1, 0) == 0
    )

    subjects_missing_closed_images = sorted(
        subject_id
        for subject_id, summary in subject_summaries.items()
        if summary["eye_state_counts"].get(0, 0) == 0
    )

    subjects_by_sensor = {}

    for subject_id, summary in subject_summaries.items():
        for sensor_id in summary["sensor_counts"]:
            if sensor_id not in subjects_by_sensor:
                subjects_by_sensor[sensor_id] = []

            subjects_by_sensor[sensor_id].append(subject_id)

    for sensor_id in subjects_by_sensor:
        subjects_by_sensor[sensor_id].sort()

    return {
        "total_subjects": len(subject_summaries),
        "min_images_per_subject": min_images,
        "max_images_per_subject": max_images,
        "mean_images_per_subject": mean(subject_sizes.values()),
        "median_images_per_subject": median(subject_sizes.values()),
        "subjects_with_min_images": subjects_with_min_images,
        "subjects_with_max_images": subjects_with_max_images,
        "subjects_missing_open_images": subjects_missing_open_images,
        "subjects_missing_closed_images": subjects_missing_closed_images,
        "subjects_by_sensor": subjects_by_sensor,
    }

def create_subject_table(subject_summaries: dict[str, dict],) -> list[dict]:
    """
    Convert nested subject summaries into flat table records.
    """
    subject_table = []

    for subject_id, summary in subject_summaries.items():
        subject_record = {
        "subject_id": subject_id,
        "total_images": summary["total_images"],
        "closed_images": summary["eye_state_counts"].get(0, 0),
        "open_images": summary["eye_state_counts"].get(1, 0),
        "without_glasses": summary["glasses_counts"].get(0, 0),
        "with_glasses": summary["glasses_counts"].get(1, 0),
        "no_reflections": summary["reflection_counts"].get(0, 0),
        "small_reflections": summary["reflection_counts"].get(1, 0),
        "big_reflections": summary["reflection_counts"].get(2, 0),
        "good_lighting": summary["lighting_counts"].get(1, 0),
        "bad_lighting": summary["lighting_counts"].get(0, 0),
        "sensor_01_images": summary["sensor_counts"].get("01", 0),
        "sensor_02_images": summary["sensor_counts"].get("02", 0),
        "sensor_03_images": summary["sensor_counts"].get("03", 0),
        }
        subject_table.append(subject_record)

    subject_table.sort(key=lambda record: record["subject_id"])

    return subject_table