import csv
from pathlib import Path

POLICIES_CSV = Path(__file__).resolve().parent.parent.parent / "policies.csv"


def lookup_policy(policy_name: str) -> str:
    """Return the answer for a policy, or a friendly message if not found."""
    with POLICIES_CSV.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["policy"].strip().lower() == policy_name.strip().lower():
                return row["answer"]

    return f"No policy found matching '{policy_name}'. Use list_policies to see available policies."
