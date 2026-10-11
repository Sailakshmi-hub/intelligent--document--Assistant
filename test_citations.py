from src.citations import format_citation


def test_pdf_and_excel_citations():
    pdf_meta = {"source_type": "pdf", "file_name": "report.pdf", "page_number": 12}
    excel_meta = {"source_type": "excel", "file_name": "attendance.xlsx", "worksheet_name": "Attendance", "row_number": 5}

    assert format_citation(pdf_meta) == "report.pdf (page 12)"
    assert format_citation(excel_meta) == "attendance.xlsx / Attendance (row 5)"
