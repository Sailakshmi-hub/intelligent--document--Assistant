from src.chunking import chunk_records


def test_chunk_metadata_preserved():
    records = [
        {
            "source_type": "pdf",
            "file_name": "notes.pdf",
            "page_number": 3,
            "content": "alpha beta gamma delta epsilon zeta eta theta",
        }
    ]

    chunks = chunk_records(records, chunk_size=4, overlap=1)

    assert len(chunks) > 0
    assert chunks[0]["metadata"]["source_type"] == "pdf"
    assert chunks[0]["metadata"]["file_name"] == "notes.pdf"
    assert chunks[0]["metadata"]["page_number"] == 3
    assert chunks[0]["text"]
