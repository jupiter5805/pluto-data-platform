import csv
import json


def load_clean_sales(records, filepath):
    """
    Write transformed sales records to a CSV file.
    """
    if not records:
        return

    fieldnames = records[0].keys()

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def load_summary(summary, filepath):
    """
    Write summary metrics to a JSON file.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)
