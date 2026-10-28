import random
from collections import Counter
from pathlib import Path

from src.data_audit.csv_exporter import write_records_csv


SPLIT_NAMES = ("train", "validation", "test")

SPLIT_COLUMNS = [
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
    "split",
]


def calculate_split_summary(
    subject_ids: list[str],
    subject_table_by_id: dict[str, dict],
) -> dict:
    """
    Calculate image and condition counts for a group of subjects.
    """
    summary = {
        "subject_count": len(subject_ids),
        "total_images": 0,
        "closed_images": 0,
        "open_images": 0,
        "without_glasses": 0,
        "with_glasses": 0,
        "no_reflections": 0,
        "small_reflections": 0,
        "big_reflections": 0,
        "bad_lighting": 0,
        "good_lighting": 0,
        "sensor_01_images": 0,
        "sensor_02_images": 0,
        "sensor_03_images": 0,
    }

    count_columns = [
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

    for subject_id in subject_ids:
        subject = subject_table_by_id[subject_id]

        for column in count_columns:
            summary[column] += subject[column]

    return summary


def calculate_distribution(
    summary: dict,
) -> dict:
    """
    Convert split counts into proportions.
    """
    total_images = summary["total_images"]

    if total_images == 0:
        return {
            "open_ratio": 0.0,
            "closed_ratio": 0.0,
            "glasses_ratio": 0.0,
            "bad_lighting_ratio": 0.0,
            "small_reflections_ratio": 0.0,
            "big_reflections_ratio": 0.0,
            "sensor_01_ratio": 0.0,
            "sensor_02_ratio": 0.0,
            "sensor_03_ratio": 0.0,
        }

    return {
        "open_ratio": summary["open_images"] / total_images,
        "closed_ratio": summary["closed_images"] / total_images,
        "glasses_ratio": summary["with_glasses"] / total_images,
        "bad_lighting_ratio": (
            summary["bad_lighting"] / total_images
        ),
        "small_reflections_ratio": (
            summary["small_reflections"] / total_images
        ),
        "big_reflections_ratio": (
            summary["big_reflections"] / total_images
        ),
        "sensor_01_ratio": (
            summary["sensor_01_images"] / total_images
        ),
        "sensor_02_ratio": (
            summary["sensor_02_images"] / total_images
        ),
        "sensor_03_ratio": (
            summary["sensor_03_images"] / total_images
        ),
    }


def calculate_candidate_score(
    split_subjects: dict[str, list[str]],
    subject_table_by_id: dict[str, dict],
    target_ratios: dict[str, float],
    global_distribution: dict,
) -> float:
    """
    Score a candidate split.

    Lower scores represent image proportions and condition
    distributions that are closer to the desired targets.
    """
    total_images = sum(
        subject["total_images"]
        for subject in subject_table_by_id.values()
    )

    score = 0.0

    distribution_keys = [
        "open_ratio",
        "glasses_ratio",
        "bad_lighting_ratio",
        "small_reflections_ratio",
        "big_reflections_ratio",
        "sensor_02_ratio",
    ]

    for split_name in SPLIT_NAMES:
        split_summary = calculate_split_summary(
            split_subjects[split_name],
            subject_table_by_id,
        )

        split_distribution = calculate_distribution(
            split_summary
        )

        actual_image_ratio = (
            split_summary["total_images"] / total_images
        )

        target_image_ratio = target_ratios[split_name]

        # Give image-count balance the greatest importance.
        score += (
            abs(actual_image_ratio - target_image_ratio)
            * 10.0
        )

        # Preserve global class and acquisition distributions.
        for key in distribution_keys:
            score += abs(
                split_distribution[key]
                - global_distribution[key]
            )

    return score


def satisfies_split_constraints(
    split_subjects: dict[str, list[str]],
    subject_table_by_id: dict[str, dict],
) -> bool:
    """
    Check the mandatory constraints for one candidate split.
    """
    train_subjects = set(split_subjects["train"])
    validation_subjects = set(
        split_subjects["validation"]
    )
    test_subjects = set(split_subjects["test"])

    # No subject overlap.
    if not train_subjects.isdisjoint(validation_subjects):
        return False

    if not train_subjects.isdisjoint(test_subjects):
        return False

    if not validation_subjects.isdisjoint(test_subjects):
        return False

    all_assigned_subjects = (
        train_subjects
        | validation_subjects
        | test_subjects
    )

    if all_assigned_subjects != set(subject_table_by_id):
        return False

    # Every split must contain both eye states.
    for split_name in SPLIT_NAMES:
        summary = calculate_split_summary(
            split_subjects[split_name],
            subject_table_by_id,
        )

        if summary["open_images"] == 0:
            return False

        if summary["closed_images"] == 0:
            return False

        # Sensor 01 and Sensor 02 should appear in every split.
        if summary["sensor_01_images"] == 0:
            return False

        if summary["sensor_02_images"] == 0:
            return False

    # Sensor 03 exists for only s0012 and s0014.
    # Keep one in training and the other in testing.
    sensor_03_subjects = {"s0012", "s0014"}

    if len(train_subjects & sensor_03_subjects) != 1:
        return False

    if len(test_subjects & sensor_03_subjects) != 1:
        return False

    if validation_subjects & sensor_03_subjects:
        return False

    # Subjects without open-eye images should not be together
    # in the same evaluation split.
    missing_open_subjects = {"s0004", "s0008"}

    if missing_open_subjects.issubset(validation_subjects):
        return False

    if missing_open_subjects.issubset(test_subjects):
        return False

    return True


def generate_subject_split(
    subject_table: list[dict],
    train_subject_count: int = 26,
    validation_subject_count: int = 5,
    test_subject_count: int = 6,
    attempts: int = 20_000,
    random_seed: int = 42,
) -> tuple[dict[str, list[str]], dict]:
    """
    Generate a balanced subject-independent dataset split.

    Repeated candidate assignments are evaluated, and the valid
    assignment with the lowest balancing score is returned.
    """
    total_requested_subjects = (
        train_subject_count
        + validation_subject_count
        + test_subject_count
    )

    if total_requested_subjects != len(subject_table):
        raise ValueError(
            "Requested split counts do not match the number "
            f"of subjects: requested {total_requested_subjects}, "
            f"available {len(subject_table)}"
        )

    if attempts <= 0:
        raise ValueError(
            "The number of split-generation attempts must "
            "be greater than zero."
        )

    subject_table_by_id = {
        record["subject_id"]: record
        for record in subject_table
    }

    subject_ids = sorted(subject_table_by_id)

    total_images = sum(
        record["total_images"]
        for record in subject_table
    )

    global_summary = calculate_split_summary(
        subject_ids,
        subject_table_by_id,
    )

    global_distribution = calculate_distribution(
        global_summary
    )

    target_ratios = {
        "train": 0.70,
        "validation": 0.15,
        "test": 0.15,
    }

    rng = random.Random(random_seed)

    best_split = None
    best_score = float("inf")

    for _ in range(attempts):
        shuffled_subjects = subject_ids.copy()
        rng.shuffle(shuffled_subjects)

        train_end = train_subject_count
        validation_end = (
            train_end + validation_subject_count
        )

        candidate = {
            "train": shuffled_subjects[:train_end],
            "validation": shuffled_subjects[
                train_end:validation_end
            ],
            "test": shuffled_subjects[validation_end:],
        }

        if not satisfies_split_constraints(
            candidate,
            subject_table_by_id,
        ):
            continue

        candidate_score = calculate_candidate_score(
            candidate,
            subject_table_by_id,
            target_ratios,
            global_distribution,
        )

        if candidate_score < best_score:
            best_score = candidate_score
            best_split = {
                split_name: sorted(subjects)
                for split_name, subjects
                in candidate.items()
            }

    if best_split is None:
        raise RuntimeError(
            "Unable to generate a subject split that satisfies "
            "the required constraints."
        )

    split_report = build_split_report(
        best_split,
        subject_table_by_id,
        total_images,
        best_score,
    )

    return best_split, split_report


def build_split_report(
    split_subjects: dict[str, list[str]],
    subject_table_by_id: dict[str, dict],
    total_images: int,
    score: float,
) -> dict:
    """
    Build a summary report for a generated subject split.
    """
    report = {
        "score": score,
        "total_images": total_images,
        "splits": {},
    }

    for split_name in SPLIT_NAMES:
        summary = calculate_split_summary(
            split_subjects[split_name],
            subject_table_by_id,
        )

        summary["image_percentage"] = (
            summary["total_images"]
            / total_images
            * 100.0
        )

        summary["subjects"] = split_subjects[split_name]
        summary["distribution"] = calculate_distribution(
            summary
        )

        report["splits"][split_name] = summary

    return report


def assign_records_to_splits(
    records: list[dict],
    split_subjects: dict[str, list[str]],
) -> dict[str, list[dict]]:
    """
    Assign inventory records to splits using subject membership.
    """
    subject_to_split = {}

    for split_name, subject_ids in split_subjects.items():
        for subject_id in subject_ids:
            if subject_id in subject_to_split:
                raise ValueError(
                    f"Subject appears in multiple splits: "
                    f"{subject_id}"
                )

            subject_to_split[subject_id] = split_name

    split_records = {
        "train": [],
        "validation": [],
        "test": [],
    }

    for record in records:
        subject_id = record["subject_id"]

        if subject_id not in subject_to_split:
            raise ValueError(
                f"Subject has no split assignment: {subject_id}"
            )

        split_name = subject_to_split[subject_id]

        split_record = record.copy()
        split_record["split"] = split_name

        split_records[split_name].append(split_record)

    return split_records


def validate_record_splits(
    original_records: list[dict],
    split_records: dict[str, list[dict]],
) -> dict:
    """
    Validate subject separation and record completeness.
    """
    expected_splits = set(SPLIT_NAMES)
    provided_splits = set(split_records)

    if provided_splits != expected_splits:
        raise ValueError(
            "Split records must contain train, validation, "
            "and test collections."
        )

    subjects_by_split = {}

    for split_name in SPLIT_NAMES:
        subjects_by_split[split_name] = {
            record["subject_id"]
            for record in split_records[split_name]
        }

    if not subjects_by_split["train"].isdisjoint(
        subjects_by_split["validation"]
    ):
        raise ValueError(
            "Subject overlap detected between train "
            "and validation splits."
        )

    if not subjects_by_split["train"].isdisjoint(
        subjects_by_split["test"]
    ):
        raise ValueError(
            "Subject overlap detected between train and test splits."
        )

    if not subjects_by_split["validation"].isdisjoint(
        subjects_by_split["test"]
    ):
        raise ValueError(
            "Subject overlap detected between validation "
            "and test splits."
        )

    original_paths = [
        record["relative_path"]
        for record in original_records
    ]

    assigned_records = [
        record
        for split_name in SPLIT_NAMES
        for record in split_records[split_name]
    ]

    assigned_paths = [
        record["relative_path"]
        for record in assigned_records
    ]

    if len(assigned_paths) != len(set(assigned_paths)):
        raise ValueError(
            "Duplicate relative paths detected across splits."
        )

    if set(original_paths) != set(assigned_paths):
        raise ValueError(
            "Split records do not match the original inventory."
        )

    split_validation = {
        "total_original_records": len(original_records),
        "total_assigned_records": len(assigned_records),
        "subjects_by_split": {
            split_name: sorted(subjects)
            for split_name, subjects
            in subjects_by_split.items()
        },
        "records_by_split": {
            split_name: len(split_records[split_name])
            for split_name in SPLIT_NAMES
        },
    }

    for split_name in SPLIT_NAMES:
        eye_state_counts = Counter(
            record["eye_state"]
            for record in split_records[split_name]
        )

        if eye_state_counts.get(0, 0) == 0:
            raise ValueError(
                f"{split_name} split contains no closed-eye images."
            )

        if eye_state_counts.get(1, 0) == 0:
            raise ValueError(
                f"{split_name} split contains no open-eye images."
            )

        split_validation.setdefault(
            "eye_state_counts",
            {},
        )[split_name] = dict(eye_state_counts)

    return split_validation


def export_split_csv_files(
    split_records: dict[str, list[dict]],
    output_directory: str | Path,
) -> dict[str, Path]:
    """
    Export train, validation, and test records to CSV files.
    """
    output_dir = Path(output_directory)

    output_paths = {}

    for split_name in SPLIT_NAMES:
        output_path = output_dir / f"{split_name}.csv"

        write_records_csv(
            records=split_records[split_name],
            output_path=output_path,
            columns=SPLIT_COLUMNS,
        )

        output_paths[split_name] = output_path

    return output_paths