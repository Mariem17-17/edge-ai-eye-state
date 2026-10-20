import argparse
from pathlib import Path

from src.data_audit.inventory_builder import build_dataset_inventory
from src.data_audit.csv_exporter import export_audit_results

def parse_arguments():
    """Parse command-line arguments for the dataset audit."""
    parser = argparse.ArgumentParser(description="Audit the MRL Eye Dataset and export inventory and failure reports")
    parser.add_argument(
        '--dataset-root',
        required=True,
        type=Path,
        help='Path to the extracted MRL Eye Dataset.'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path("metadata"),
        help='Directory for generated CSV reports.'
    )

    args = parser.parse_args()
    return args


def run_audit(dataset_root: str | Path, output_directory: str | Path,) -> tuple[list[dict], list[dict], Path, Path]:
    """
    Build the dataset inventory and export the audit reports.
    Returns the inventory, failures, and generated CSV paths.
    """
    inventory, failures = build_dataset_inventory(dataset_root)

    inventory_path, failures_path = export_audit_results(
        inventory,
        failures,
        output_directory,
    )

    return (
        inventory,
        failures,
        inventory_path,
        failures_path,
    )



def main():
    """Run the dataset-audit command-line application."""
    args = parse_arguments()

    inventory, failures, inventory_path, failures_path = (
        run_audit(
            dataset_root=args.dataset_root,
            output_directory=args.output_dir,
        )
    )

    print(f"Valid inventory records: {len(inventory)}")
    print(f"Processing failures: {len(failures)}")
    print(f"Inventory CSV: {inventory_path}")
    print(f"Failures CSV: {failures_path}")


if __name__ == "__main__":
    main()