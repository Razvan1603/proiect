import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env", override=True)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Bob - Chatbot Suport",
    layout="centered",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 900px; padding-top: 2rem; }
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: #eef6ff;
        color: #175cd3;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 0.35rem;
    }
    .meta-box {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.8rem;
        background: #fafafa;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def call_api(path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{API_BASE_URL}{path}"
    if method == "POST":
        response = requests.post(url, json=payload, timeout=30)
    else:
        response = requests.get(url, timeout=10)
    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(detail)
    return response.json()


def ensure_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("last_meta", None)
    st.session_state.setdefault("user_id", "user_001")
    st.session_state.setdefault("show_analysis", False)


ensure_state()

with st.sidebar:
    st.header("Setari demo")
    st.session_state.user_id = st.text_input("User ID", value=st.session_state.user_id)

    try:
        health = call_api("/health")
        st.success("API conectat")
        st.caption(f"Model: {health['model']}")
        st.caption("Mod: Groq LLM")
    except Exception:
        st.error("API indisponibil")
        st.caption("Porneste backend-ul FastAPI pe portul 8000.")

    if st.button("Reseteaza conversatia", use_container_width=True):
        try:
            call_api(f"/reset/{st.session_state.user_id}", method="POST")
        except Exception:
            pass
        st.session_state.messages = []
        st.session_state.last_meta = None
        st.rerun()

    st.divider()
    st.caption("Contract API")
    st.code('{"user_id": "user_001", "message": "text"}', language="json")

st.title("Bob")
st.caption("Chatbot suport social media")


for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        if item["role"] == "assistant":
            st.markdown("**Bob**")
        st.markdown(item["content"])

if prompt := st.chat_input("Scrie un mesaj pentru chatbot..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st.markdown("**Bob**")
        with st.spinner("Generez raspunsul..."):
            try:
                payload = {"user_id": st.session_state.user_id, "message": prompt}
                result = call_api("/chat", method="POST", payload=payload)
                answer = result["response"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.last_meta = result
            except Exception as exc:
                error_message = f"LLM-ul nu a putut genera raspunsul: {exc}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

if st.session_state.last_meta:
    meta = st.session_state.last_meta
    st.markdown("---")
    button_label = "Ascunde analiza intentului" if st.session_state.show_analysis else "Arata analiza intentului"
    if st.button(button_label, use_container_width=True):
        st.session_state.show_analysis = not st.session_state.show_analysis
        st.rerun()

    if st.session_state.show_analysis:
        st.markdown(
            f"""
            <div class="meta-box">
                <span class="status-badge">intent: {meta["intent"]}</span>
                <span class="status-badge">confidence: {meta["confidence"]:.2f}</span>
                <span class="status-badge">provider: {meta["llm_provider"]}</span>
                <br><br>
                <strong>Entitati:</strong> {meta["entities"] or "{}"}
                {'<br><strong>LLM fallback:</strong> ' + meta["llm_error"] if meta.get("llm_error") else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if meta.get("intent_scores"):
            st.caption("Probabilitati intent BERT")
            st.dataframe(
                [
                    {
                        "intent": item["intent"],
                        "label_model": item["label"],
                        "probabilitate": round(item["confidence"], 4),
                    }
                    for item in meta["intent_scores"]
                ],
                hide_index=True,
                use_container_width=True,
            )
