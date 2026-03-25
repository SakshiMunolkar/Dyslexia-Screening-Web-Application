import csv
import os

def save_record(record, filename="records.csv"):

    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=record.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)