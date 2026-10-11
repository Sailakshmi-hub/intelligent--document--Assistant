from pathlib import Path

import fitz
import pytest

from src.pdf_processor import extract_pdf_text


def test_pdf_extraction_and_page_metadata(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    document = fitz.open()
    first_page = document.new_page()
    first_page.insert_text((72, 72), "Alpha beta gamma")
    second_page = document.new_page()
    second_page.insert_text((72, 72), "Second page of sample")
    document.save(pdf_path)
    document.close()

    pages = extract_pdf_text(pdf_path)

    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert "Alpha" in pages[0]["content"]
    assert pages[1]["page_number"] == 2
    assert "Second page" in pages[1]["content"]


def test_empty_and_malformed_pdf(tmp_path):
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")

    with pytest.raises(ValueError):
        extract_pdf_text(empty_file)

    missing_file = tmp_path / "missing.pdf"
    with pytest.raises(FileNotFoundError):
        extract_pdf_text(missing_file)
