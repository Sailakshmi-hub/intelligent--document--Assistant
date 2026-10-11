from pathlib import Path

import pandas as pd

from src.excel_processor import extract_excel_records


def test_excel_row_and_sheet_metadata(tmp_path):
    workbook_path = tmp_path / "attendance.xlsx"
    frame = pd.DataFrame(
        {
            "Student_ID": ["ST101", "ST102"],
            "Subject": ["Computer Networks", "Databases"],
            "Total_Classes": [40, 35],
            "Present_Classes": [34, 31],
        }
    )
    with pd.ExcelWriter(workbook_path) as writer:
        frame.to_excel(writer, sheet_name="Attendance", index=False)

    records = extract_excel_records(workbook_path)

    assert len(records) == 2
    assert records[0]["worksheet_name"] == "Attendance"
    assert records[0]["row_number"] == 2
    assert "Student_ID" in records[0]["content"]
    assert "Computer Networks" in records[0]["content"]


def test_excel_unsupported_extension(tmp_path):
    bad_path = tmp_path / "notes.txt"
    bad_path.write_text("not a spreadsheet")

    try:
        extract_excel_records(bad_path)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for unsupported file type.")
