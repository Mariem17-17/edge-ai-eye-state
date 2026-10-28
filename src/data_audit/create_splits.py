import argparse
from pathlib import Path

from src.data_audit.inventory_analyzer import (
    create_subject_table,
    load_inventory_csv,
    summarize_subjects,
)
from src.data_audit.split_generator import (
    assign_records_to_splits,
    export_split_csv_files,
    generate_subject_split,
    validate_record_splits,
)


def parse_arguments():
    """
    Parse command-line arguments for split generation.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Generate leakage-safe subject-independent "
            "dataset splits."
        )
    )

    parser.add_argument(
        "--inventory",
        required=True,
        type=Path,
        help="Path to dataset_inventory.csv.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("metadata"),
        help="Directory for generated split CSV files.",
    )

    parser.add_argument(
        "--attempts",
        type=int,
        default=20_000,
        help="Number of candidate subject assignments to evaluate.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used for deterministic split generation.",
    )

    return parser.parse_args()


def main():
    """
    Generate, validate, and export subject-independent splits.
    """
    args = parse_arguments()

    records = load_inventory_csv(args.inventory)

    subject_summaries = summarize_subjects(records)
    subject_table = create_subject_table(
        subject_summaries
    )

    split_subjects, split_report = generate_subject_split(
        subject_table=subject_table,
        attempts=args.attempts,
        random_seed=args.seed,
    )

    split_records = assign_records_to_splits(
        records=records,
        split_subjects=split_subjects,
    )

    validation = validate_record_splits(
        original_records=records,
        split_records=split_records,
    )

    output_paths = export_split_csv_files(
        split_records=split_records,
        output_directory=args.output_dir,
    )

    print("Subject-independent split generated.")
    print()

    for split_name in ("train", "validation", "test"):
        report = split_report["splits"][split_name]

        print(f"{split_name.upper()}")
        print(
            f"  Subjects: {report['subject_count']}"
        )
        print(
            f"  Images: {report['total_images']}"
        )
        print(
            "  Image percentage: "
            f"{report['image_percentage']:.2f}%"
        )
        print(
            f"  Closed images: {report['closed_images']}"
        )
        print(
            f"  Open images: {report['open_images']}"
        )
        print(
            f"  Sensor 01: {report['sensor_01_images']}"
        )
        print(
            f"  Sensor 02: {report['sensor_02_images']}"
        )
        print(
            f"  Sensor 03: {report['sensor_03_images']}"
        )
        print(
            f"  Subject IDs: {', '.join(report['subjects'])}"
        )
        print(
            f"  CSV: {output_paths[split_name]}"
        )
        print()

    print(
        "Total assigned records: "
        f"{validation['total_assigned_records']}"
    )
    print(
        f"Split score: {split_report['score']:.6f}"
    )


if __name__ == "__main__":
    main()