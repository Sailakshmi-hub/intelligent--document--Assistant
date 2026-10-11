# Intelligent Document Assistant

A local, document-grounded RAG application for PDF and Excel question answering. It uses Streamlit for the interface, FAISS for retrieval, sentence-transformers for embeddings, and Ollama for local LLM inference.

## Overview

This project lets you upload PDF documents and spreadsheets, build a searchable local index, and ask questions in natural language. The app retrieves the most relevant passages and sends only a compact evidence set to the selected local LLM. Answers and citations are grounded in the uploaded files rather than general model memory.

## Features

- PDF upload and extraction with page-level metadata
- Excel and CSV workbook processing with worksheet and row metadata
- Chunking with configurable size and overlap
- Local embedding model using sentence-transformers
- FAISS vector-store retrieval
- Multiple local Ollama model selection
- Source citations for PDF pages and Excel rows
- Streamlit-based chat interface with conversation memory and document management
- Clear validation and error handling for unsupported files and missing models
- Pytest suite for core processing and retrieval behavior

## Architecture

The application is organized into modular service layers:

- app.py: Streamlit entry point and UI orchestration
- src/config.py: environment and validation settings
- src/ollama_service.py: model discovery, connection checks, and chat requests
- src/pdf_processor.py: PDF extraction and page metadata
- src/excel_processor.py: workbook extraction and row metadata
- src/chunking.py: text chunk creation with metadata preservation
- src/embeddings.py: shared embedding model initialization
- src/vector_store.py: FAISS index lifecycle and deduplication
- src/retrieval.py: relevant context retrieval
- src/rag_pipeline.py: grounded answer generation pipeline
- src/citations.py: formatting for trustworthy citations
- src/ui_components.py: reusable UI helpers and styling

## Folder structure

```text
intelligent_document_assistant/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
├── assets/
│   └── background.svg
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── ollama_service.py
│   ├── pdf_processor.py
│   ├── excel_processor.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retrieval.py
│   ├── rag_pipeline.py
│   ├── citations.py
│   └── ui_components.py
└── tests/
    ├── test_pdf_processor.py
    ├── test_excel_processor.py
    ├── test_chunking.py
    ├── test_retrieval.py
    ├── test_citations.py
    └── test_ollama_service.py
```

## Prerequisites

- Python 3.11.9
- Ollama installed locally
- Access to the following local models:
  - llama3.2:3b
  - qwen2.5:3b
- Optional: a local sentence-transformers model download on first use

## Python 3.11.9 installation

On Windows PowerShell:

```powershell
py -3.11 --version
```

If Python 3.11 is not installed, download and install it from the official Python website, then confirm it is available in PATH.

## Ollama installation

1. Download and install Ollama from https://ollama.com/download
2. Start the Ollama service
3. Verify the local API is reachable at http://localhost:11434
4. Pull the required models if they are not available:

```powershell
ollama pull llama3.2:3b
ollama pull qwen2.5:3b
```

## Check installed models

```powershell
ollama list
```

## Virtual environment setup

```powershell
cd "C:\Users\Laksh\OneDrive\Documents\Intelligent doc Assist"
py -3.11 -m venv venv311
.\venv311\Scripts\Activate.ps1
```

## Dependency installation

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Application launch

```powershell
cd "C:\Users\Laksh\OneDrive\Documents\Intelligent doc Assist"
.\venv311\Scripts\Activate.ps1
streamlit run app.py
```

## Embedding model setup

The application uses a separate embedding model from the Ollama chat models. The default local embedding model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

This model is downloaded automatically on first use if needed. It is different from the local LLMs used for answer generation.

## Background image configuration

The project includes a local SVG background asset at `assets/background.svg`. This is a subtle dark technology-themed pattern used for the app shell. It is intentionally low-contrast so the interface remains readable while the visual design feels polished. The file is self-created and included in the repo, so no external image download is needed.

## Document usage instructions

1. Open the app in the browser.
2. Upload one or more PDF, XLSX, XLS, or CSV files.
3. Click Process Documents.
4. Review the indexed file list and chunk counts.
5. Ask questions in the chat box.
6. Inspect any source citations and retrieved excerpts shown in the answer.

## Switching local LLMs

Use the sidebar model selector. The selected model is used for the current chat request. When Ollama is unavailable or a model is missing, the app shows a clear message and suggests the correct `ollama pull` command.

## Troubleshooting

- If Streamlit does not start: confirm the virtual environment is active and dependencies are installed.
- If Ollama is offline: start the Ollama service with `ollama serve` or ensure a local Ollama instance is running.
- If a model is missing: run `ollama pull llama3.2:3b` or `ollama pull qwen2.5:3b`.
- If no answer is returned: check whether the uploaded documents were successfully processed and indexed.
- If a file is unsupported: only PDF, XLSX, XLS, and CSV files are accepted.

## Testing

Run the tests with:

```powershell
cd "C:\Users\Laksh\OneDrive\Documents\Intelligent doc Assist"
.\venv311\Scripts\Activate.ps1
pytest -q
```

The project includes tests for PDF extraction, Excel metadata, chunking, retrieval, citations, and Ollama service checks.

## Important concepts

- LLM: a large language model that generates responses from text prompts.
- Embedding model: a model that converts text into numeric vectors so similar content can be compared.
- Vector database: a database optimized for similarity search over embedding vectors.
- Retrieval: finding the most relevant document chunks for a user question.
- Augmented generation: combining retrieved document evidence with an LLM prompt to produce grounded responses.

## Limitations and future improvements

- OCR is not implemented as a production workflow for scanned PDFs; the code reports empty or scanned-like pages and prompts users to consider OCR extension.
- Large document collections may need better indexing and cache management for more demanding workflows.
- More advanced answer validation and document summarization are possible expansions.

## Manual end-to-end checklist

- Launch the app
- Verify Ollama model list
- Upload a PDF and Excel file
- Process the documents
- Confirm file counts and indexed chunks
- Ask a question that should match a document fact
- Confirm the answer includes a citation
- Ask an unsupported or out-of-domain question and verify the app is honest about missing evidence

## Validated status

This project was validated with the local pytest suite in the workspace environment. The latest run passed with 10 tests passing.
