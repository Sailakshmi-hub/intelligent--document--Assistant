from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.chunking import chunk_records
from src.config import ALLOWED_EXTENSIONS, CHUNK_OVERLAP, CHUNK_SIZE, DEFAULT_MODEL, OLLAMA_BASE_URL, TOP_K, UPLOAD_LIMIT_BYTES, sanitize_filename
from src.citations import format_citation
from src.excel_processor import extract_excel_records
from src.ollama_service import check_connection, generate_answer, is_model_available, list_available_models
from src.pdf_processor import extract_pdf_text
from src.rag_pipeline import answer_question
from src.ui_components import configure_page, render_css, render_summary_cards, status_badge
from src.vector_store import VectorStore

configure_page()
render_css()


@st.cache_resource(show_spinner=False)
def load_vector_store() -> VectorStore:
    return VectorStore()


def initialize_session_state() -> None:
    st.session_state.setdefault("documents", [])
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("selected_model", DEFAULT_MODEL)
    st.session_state.setdefault("vector_store", load_vector_store())
    st.session_state.setdefault("chunk_size", CHUNK_SIZE)
    st.session_state.setdefault("chunk_overlap", CHUNK_OVERLAP)
    st.session_state.setdefault("top_k", TOP_K)


initialize_session_state()


def reset_index() -> None:
    store = VectorStore()
    st.session_state["vector_store"] = store
    st.session_state["documents"] = []
    st.session_state["chat_history"] = []


def rebuild_index() -> None:
    files = st.session_state.get("documents", [])
    all_chunks: list[dict] = []
    for item in files:
        if not item.get("chunks"):
            continue
        all_chunks.extend(item["chunks"])
    store = VectorStore()
    if all_chunks:
        store.add_chunks(all_chunks)
    st.session_state["vector_store"] = store


def process_uploaded_files(files) -> None:
    if not files:
        st.warning("Choose at least one PDF or Excel file before processing.")
        return

    processed_items: list[dict] = []
    all_chunks: list[dict] = []
    for uploaded_file in files:
        safe_name = sanitize_filename(uploaded_file.name)
        if Path(safe_name).suffix.lower() not in ALLOWED_EXTENSIONS:
            st.warning(f"Unsupported file type: {uploaded_file.name}")
            continue
        if uploaded_file.size > UPLOAD_LIMIT_BYTES:
            st.warning(f"{uploaded_file.name} exceeds the {UPLOAD_LIMIT_BYTES // 1048576} MB upload limit.")
            continue

        target_path = Path("data") / safe_name
        target_path.parent.mkdir(exist_ok=True)
        target_path.write_bytes(uploaded_file.getvalue())

        try:
            if target_path.suffix.lower() == ".pdf":
                records = []
                for page in extract_pdf_text(target_path):
                    if page["content"]:
                        records.append({
                            "source_type": "pdf",
                            "file_name": page["file_name"],
                            "page_number": page["page_number"],
                            "content": page["content"],
                            "page_is_empty": page["is_empty"],
                        })
            else:
                records = extract_excel_records(target_path)
        except Exception as exc:  # pragma: no cover - UI safety
            st.error(f"Could not process {uploaded_file.name}: {exc}")
            continue

        chunks = chunk_records(records, chunk_size=st.session_state["chunk_size"], overlap=st.session_state["chunk_overlap"])
        for chunk in chunks:
            chunk["metadata"]["content"] = chunk["text"]
        all_chunks.extend(chunks)
        processed_items.append(
            {
                "file_name": safe_name,
                "file_type": target_path.suffix.lower().lstrip("."),
                "status": "processed",
                "chunk_count": len(chunks),
                "rows": len(records),
                "chunks": chunks,
            }
        )

    if not processed_items:
        st.info("No valid documents were indexed.")
        return

    existing = st.session_state.get("documents", [])
    merged = existing + processed_items
    st.session_state["documents"] = merged
    store = VectorStore()
    if all_chunks:
        store.add_chunks(all_chunks)
    st.session_state["vector_store"] = store
    st.success(f"Indexed {len(processed_items)} document(s) and {len(all_chunks)} chunk(s).")


st.title("Intelligent Document Assistant")
st.caption("Upload PDFs and spreadsheets, ask grounded questions, and use local LLMs with retrieved citations.")

with st.sidebar:
    st.markdown("### Intelligent Document Assistant")

    ollama_ok = check_connection()
    st.markdown(f"Ollama status: {status_badge('Connected' if ollama_ok else 'Offline', ollama_ok)}", unsafe_allow_html=True)
    if ollama_ok:
        available_models = list_available_models()
        if not available_models:
            st.warning("No models are currently available in Ollama.")
        else:
            selected = st.selectbox("Model", available_models, index=0 if st.session_state["selected_model"] not in available_models else available_models.index(st.session_state["selected_model"]))
            st.session_state["selected_model"] = selected
    else:
        st.warning("Start Ollama locally before using the assistant.")

    st.subheader("Embedding status")
    st.caption("Using sentence-transformers/all-MiniLM-L6-v2 locally.")

    st.subheader("Upload documents")
    uploaded = st.file_uploader("Choose PDF, Excel, or CSV files", type=[".pdf", ".xlsx", ".xls", ".csv"], accept_multiple_files=True)
    if st.button("Process Documents"):
        process_uploaded_files(uploaded)

    st.subheader("Settings")
    st.session_state["chunk_size"] = st.slider("Chunk size", min_value=150, max_value=1000, value=st.session_state["chunk_size"])
    st.session_state["chunk_overlap"] = st.slider("Chunk overlap", min_value=20, max_value=250, value=st.session_state["chunk_overlap"])
    st.session_state["top_k"] = st.slider("Retrieval count", min_value=1, max_value=10, value=st.session_state["top_k"])

    st.subheader("Workspace")
    if st.button("Clear chat"):
        st.session_state["chat_history"] = []
    if st.button("Clear workspace"):
        reset_index()

    st.caption(f"Ollama URL: {OLLAMA_BASE_URL}")

if not st.session_state["documents"]:
    st.markdown(
        """
        <div class='card'>
            <h3>Welcome to the Intelligent Document Assistant</h3>
            <p>Upload PDFs or spreadsheets to build a local RAG index. Ask grounded questions and inspect the retrieved evidence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

render_summary_cards(len(st.session_state["documents"]), sum(item.get("chunk_count", 0) for item in st.session_state["documents"]), st.session_state["selected_model"])

st.subheader("Documents")
for item in st.session_state["documents"]:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        colA, colB, colC = st.columns([3, 1, 1])
        with colA:
            st.write(f"**{item['file_name']}**")
            st.caption(f"{item['file_type']} • {item['rows']} records • {item['chunk_count']} chunks")
        with colB:
            st.write(item["status"])
        with colC:
            if st.button(f"Remove {item['file_name']}", key=f"remove-{item['file_name']}"):
                st.session_state["documents"] = [doc for doc in st.session_state["documents"] if doc["file_name"] != item["file_name"]]
                rebuild_index()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.subheader("Conversation")
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("citations"):
            with st.expander("Source citations"):
                for citation in message["citations"]:
                    st.write(citation)

question = st.chat_input("Ask a question about your documents")
if question:
    if not st.session_state["documents"]:
        st.warning("Process at least one document before asking a question.")
    else:
        selected_model = st.session_state.get("selected_model")
        if not selected_model or not is_model_available(selected_model):
            st.warning(f"Model '{selected_model}' is not available in Ollama. Pull it with `ollama pull {selected_model}`.")
        else:
            with st.spinner("Retrieving context and generating a grounded answer..."):
                result = answer_question(question, st.session_state["vector_store"], selected_model, top_k=st.session_state["top_k"])
            st.session_state["chat_history"].append({"role": "user", "content": question})
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": result["answer"],
                "citations": result.get("citations", []),
                "sources": result.get("sources", []),
            })
            st.rerun()

if st.session_state["chat_history"]:
    st.caption("The assistant uses retrieved context from the uploaded files and shows source references when available.")
