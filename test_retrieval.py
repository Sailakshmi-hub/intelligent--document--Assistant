import numpy as np

from src.vector_store import VectorStore


def test_empty_index_returns_no_results():
    store = VectorStore(embedding_model_name="dummy-model")
    store.clear()

    assert store.search("nothing here", top_k=3) == []


def test_search_returns_relevant_context():
    store = VectorStore(embedding_model_name="dummy-model")
    chunks = [
        {"text": "Paris is the capital of France.", "metadata": {"file_name": "doc1.pdf", "source_type": "pdf", "page_number": 2}},
        {"text": "Berlin is the capital of Germany.", "metadata": {"file_name": "doc2.pdf", "source_type": "pdf", "page_number": 4}},
    ]
    embeddings = np.array([
        [1.0, 0.0],
        [0.0, 1.0],
    ], dtype=np.float32)
    store.add_chunks(chunks, embeddings=embeddings)

    results = store.search("capital of France", top_k=2)

    assert len(results) == 2
    assert results[0]["metadata"]["file_name"] == "doc1.pdf"
