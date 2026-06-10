import csv
from pathlib import Path

POLICIES_CSV = Path(__file__).resolve().parent.parent.parent / "policies.csv"


def list_policies() -> list[str]:
    """Return all available policy names from the CSV."""
    with POLICIES_CSV.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [row["policy"] for row in reader]
