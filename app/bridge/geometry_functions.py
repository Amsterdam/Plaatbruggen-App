"""Functions for geometry calculations in the Bridge application."""

import csv
from pathlib import Path


def get_steel_qualities() -> list[str]:
    """
    Get list of available steel qualities from the CSV file.

    Returns:
        list: List of steel quality names

    """
    csv_path = Path(__file__).parent.parent.parent / "resources" / "data" / "materials" / "betonstaalkwaliteit.csv"
    with open(csv_path) as f:
        csv_reader = csv.DictReader(f, delimiter=";")
        return [row["Betonstaalkwaliteit"].strip('"') for row in csv_reader]
