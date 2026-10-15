"""Convert latihan1.csv into a JavaScript data file for Streamlit."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "latihan1.csv"
DESTINATION = ROOT / "latihan1.js"
JS_PREFIX = "globalThis.LATIHAN1_DATA = "


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as source_file:
        table = list(csv.reader(source_file))
    columns, source_rows = table[0], table[1:]
    rows = []
    for source_row in source_rows:
        row = []
        for column, value in zip(columns, source_row):
            if column == "Gender":
                row.append(value)
            else:
                number = float(value)
                row.append(int(number) if number.is_integer() else number)
        rows.append(row)
    object_literal = json.dumps(
        {"columns": columns, "rows": rows}, separators=(",", ":"), ensure_ascii=False
    )
    DESTINATION.write_text(JS_PREFIX + object_literal + ";\n", encoding="utf-8")
    print(f"Selesai: {len(rows)} baris -> {DESTINATION.name} ({DESTINATION.stat().st_size} byte)")


if __name__ == "__main__":
    main()
