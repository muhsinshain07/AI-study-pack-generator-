"""Main file: Streamlit UI. Run with:  streamlit run app.py"""
import streamlit as st

from core import generate_study_pack, get_api_key
from utils import extract_text, to_markdown

st.set_page_config(page_title="AI Study Pack Generator", page_icon="📚", layout="wide")
st.title("📚 AI Study Pack Generator")
st.caption("Upload notes or paste text → get a summary, flashcards, quiz and study plan.")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
    n_cards = st.slider("Flashcards", 5, 20, 10)
    n_q = st.slider("Quiz questions", 3, 10, 5)
    if not get_api_key():
        st.warning("No API key found. Add ANTHROPIC_API_KEY to secrets.")

# ---------- Inputs ----------
col1, col2 = st.columns(2)
with col1:
    upload = st.file_uploader("Upload PDF / TXT / MD", type=["pdf", "txt", "md"])
with col2:
    topic = st.text_input("Topic (optional)")
pasted = st.text_area("...or paste your notes here", height=180)

if st.button("Generate study pack", type="primary"):
    text = pasted
    try:
        if upload is not None:
            text = extract_text(upload, upload.name) + "\n" + pasted
        with st.spinner("Building your study pack..."):
            st.session_state["pack"] = generate_study_pack(
                text, topic, n_cards, n_q, difficulty
            )
    except Exception as e:
        st.error(f"Something went wrong: {e}")

# ---------- Output ----------
pack = st.session_state.get("pack")
if pack:
    st.header(pack.get("title", "Your Study Pack"))
    st.download_button("⬇️ Download as Markdown", to_markdown(pack),
                       file_name="study_pack.md", mime="text/markdown")

    tabs = st.tabs(["Summary", "Key concepts", "Flashcards", "Quiz", "Study plan"])

    with tabs[0]:
        st.write(pack.get("summary", ""))

    with tabs[1]:
        for c in pack.get("key_concepts", []):
            st.markdown(f"**{c['term']}** — {c['definition']}")

    with tabs[2]:
        for i, f in enumerate(pack.get("flashcards", []), 1):
            with st.expander(f"Card {i}: {f['q']}"):
                st.write(f["a"])

    with tabs[3]:
        for i, q in enumerate(pack.get("quiz", [])):
            choice = st.radio(f"{i + 1}. {q['question']}", q["options"],
                              index=None, key=f"quiz_{i}")
            if choice is not None:
                if q["options"].index(choice) == q["answer_index"]:
                    st.success("Correct! " + q["explanation"])
                else:
                    st.error("Not quite. " + q["explanation"])

    with tabs[4]:
        for d in pack.get("study_plan", []):
            st.subheader(f"{d['day']}: {d['focus']}")
            for t in d.get("tasks", []):
                st.checkbox(t, key=f"{d['day']}_{t}")
