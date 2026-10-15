import streamlit as st
from app.pipeline import answer

st.set_page_config(page_title="East India Geo-Assistant", page_icon="🗺️")
st.title("East India Geo-Assistant")
st.caption("Answers are grounded in the locally indexed sources.")

question = st.text_input("Ask a question")

if question.strip():
    with st.spinner("Searching sources..."):
        try:
            result = answer(question.strip())
            st.subheader("Answer")
            st.write(result["answer"])
            st.metric("Confidence (uncalibrated)", f'{result["confidence"]:.2f}')
            st.write("Citations", result["citations"])
            st.write("Entities", result["entities_used"])
            st.write("Graph paths", result.get("graph_paths", []))
            st.json(result["settings"])
        except Exception as exc:
            st.error(f"Request failed: {exc}")
