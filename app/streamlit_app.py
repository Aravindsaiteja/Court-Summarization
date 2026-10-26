"""Phase 11: Interactive Streamlit Web Application for Court Proceeding Summarization.

Provides an interactive user interface:
- Video playback synchronized with extractive transcript sentences
- Selectable summarization methods (TF-IDF, TextRank, Embedding MMR)
- Granular compression ratio sliders & legal domain boost toggles
- Side-by-side original and translated transcript views
- Temporal jump links directly anchored to video timestamps
- Multi-format exports (TXT, JSON, PDF)
- Prominently rendered judicial disclaimer
"""

import os
import sys
import json
import time
from pathlib import Path

import streamlit as st
import pandas as pd

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.pipeline.runner import CourtProceedingSummarizationPipeline
from src.api.db import init_db, list_jobs

# Set Page Config
st.set_page_config(
    page_title="Court Proceeding Summarization System",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .disclaimer-card {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 0.9rem 1.2rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        color: #991B1B;
        font-size: 0.9rem;
    }
    .summary-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .badge-ruling {
        background-color: #DCFCE7;
        color: #166534;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
    .badge-allegation {
        background-color: #FEF3C7;
        color: #92400E;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
    .badge-procedural {
        background-color: #E0F2FE;
        color: #075985;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_pipeline():
    return CourtProceedingSummarizationPipeline(asr_model_size="tiny", default_summarizer="textrank")


pipeline = load_pipeline()

# Title Header
st.markdown('<div class="main-header">⚖️ Multilingual Court Proceeding Summarizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Speech Recognition & Strictly Extractive Summarization with Temporal Anchoring</div>', unsafe_allow_html=True)

# Mandatory Legal Disclaimer
st.markdown("""
<div class="disclaimer-card">
    <b>⚠️ MANDATORY JUDICIAL ASSISTIVE TOOL DISCLAIMER:</b><br>
    This software is strictly an assistive reference tool designed for academic research, legal review, and journalistic analysis.
    <b>It does not constitute formal legal advice.</b> The summarizer is strictly extractive (never paraphrasing or generating words).
    Every excerpt must be independently verified against official judicial recordings before being cited in legal proceedings.
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.header("🛠️ Pipeline Parameters")

# Dataset Inventory Loader
dataset_dir = Path("Dataset")
dataset_files = sorted(list(dataset_dir.glob("*.mp4"))) if dataset_dir.exists() else []
case_options = ["-- Upload New Media --"] + [f.name for f in dataset_files]

selected_case = st.sidebar.selectbox("Select Case Recording:", case_options)

uploaded_file = None
if selected_case == "-- Upload New Media --":
    uploaded_file = st.sidebar.file_uploader("Upload Court Video/Audio", type=["mp4", "mkv", "avi", "mov", "wav"])

method = st.sidebar.selectbox(
    "Extractive Summarization Method:",
    ["textrank", "tfidf", "embedding"],
    format_func=lambda x: {
        "textrank": "Method B: TextRank (Graph Centrality)",
        "tfidf": "Method A: TF-IDF + Position Prior",
        "embedding": "Method C: Multilingual Embedding (MMR)"
    }[x]
)

summary_ratio = st.sidebar.slider("Summary Compression Ratio:", min_value=0.10, max_value=0.50, value=0.25, step=0.05)
legal_boost = st.sidebar.checkbox("Enable Legal Domain Salience Boost", value=True)
enable_translation = st.sidebar.checkbox("Translate Non-English Audio to English", value=True)
judicial_only = st.sidebar.checkbox(
    "⚖️ Extract Judicial Judgment Words Only",
    value=True,
    help="Focus strictly on the Judge's verdict, rulings, and orders delivered after hearing both parties, suppressing advocate allegations and procedural banter."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Telemetry")
st.sidebar.info("Model: `faster-whisper-tiny` (INT8 CPU)\nSummarizer: Strictly Extractive Judicial Rulings with Timestamp Anchors")

# Execution Triggers
run_btn = st.sidebar.button("🚀 Process & Generate Summary", type="primary")
re_summarize_btn = st.sidebar.button("🔄 Update Extractive Summary", help="Instantly re-summarize currently loaded transcript with selected parameters without re-transcribing audio")

# Auto-load existing cached results when a dataset case is selected
if selected_case != "-- Upload New Media --":
    case_stem = Path(selected_case).stem
    cached_json = Path("outputs") / case_stem / f"{case_stem}_summary.json"
    if not cached_json.exists():
        inv_path = Path("data/dataset_inventory.csv")
        if inv_path.exists():
            try:
                inv_df = pd.read_csv(inv_path)
                match = inv_df[inv_df["Original_Filename"] == selected_case]
                if not match.empty:
                    cid = match.iloc[0]["Case_ID"]
                    alt_json = Path("outputs") / cid / f"{cid}_summary.json"
                    if alt_json.exists():
                        cached_json = alt_json
            except Exception:
                pass

    last_loaded = st.session_state.get("loaded_case_stem")
    if cached_json.exists() and (last_loaded != case_stem or "last_result" not in st.session_state):
        try:
            with open(cached_json, "r", encoding="utf-8") as f:
                loaded_res = json.load(f)
                st.session_state["last_result"] = loaded_res
                st.session_state["last_media"] = str(dataset_dir / selected_case)
                st.session_state["loaded_case_stem"] = case_stem
        except Exception:
            pass

# Handle Instant Re-summarize Trigger
if re_summarize_btn and "last_result" in st.session_state:
    cur_res = st.session_state["last_result"]
    updated_summary = pipeline.re_summarize(
        cur_res["full_transcript_sentences"],
        method=method,
        summary_ratio=summary_ratio,
        judicial_only=judicial_only,
        language=cur_res.get("detected_language", "en")
    )
    cur_res["extractive_summary_sentences"] = updated_summary
    cur_res["summary_sentence_count"] = len(updated_summary)
    cur_res["summarization_method"] = {
        "textrank": "TextRank Graph Centrality Summarizer",
        "tfidf": "TF-IDF + Position Prior Summarizer",
        "embedding": "Multilingual Embedding MMR Summarizer"
    }.get(method, method)
    st.session_state["last_result"] = cur_res
    st.sidebar.success("Extractive summary updated!")

# Main Content Layout
if run_btn:
    media_path = None
    if selected_case != "-- Upload New Media --":
        media_path = str(dataset_dir / selected_case)
    elif uploaded_file is not None:
        temp_dir = Path("outputs/temp_uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_save = temp_dir / uploaded_file.name
        with open(temp_save, "wb") as f:
            f.write(uploaded_file.getbuffer())
        media_path = str(temp_save)
    else:
        st.warning("Please select a recording from the inventory or upload a file.")

    if media_path:
        with st.spinner("Processing courtroom audio: Extracting, Transcribing, Segmenting & Summarizing across entire video..."):
            t_start = time.time()
            try:
                pipeline.legal_boost_enabled = legal_boost
                result = pipeline.run(
                    media_path=media_path,
                    method=method,
                    summary_ratio=summary_ratio,
                    enable_translation=enable_translation,
                    judicial_only=judicial_only
                )
                st.session_state["last_result"] = result
                st.session_state["last_media"] = media_path
                st.session_state["loaded_case_stem"] = Path(media_path).stem
                st.success(f"Processing complete in {result['total_pipeline_time_ms']/1000:.2f}s!")
            except Exception as e:
                st.error(f"Pipeline execution error: {e}")

# Render Results
if "last_result" in st.session_state:
    res = st.session_state["last_result"]
    media_file = st.session_state.get("last_media")
    lang_code = res.get("detected_language", "en").lower()
    lang_map = {"te": "Telugu", "hi": "Hindi", "ta": "Tamil", "en": "English", "bn": "Bengali", "mr": "Marathi"}
    lang_label = lang_map.get(lang_code, lang_code.upper())

    # Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Detected Language", lang_label, f"{res['language_confidence']*100:.1f}% Conf")
    m2.metric("Audio Duration", f"{res['audio_duration_sec']:.1f}s")
    m3.metric("Transcript Sentences", res["total_transcript_sentences"])
    m4.metric("Summary Sentences", res["summary_sentence_count"])
    m5.metric("Latency", f"{res['total_pipeline_time_ms']/1000:.2f}s")

    st.markdown("---")

    # Media Playback & Timestamps
    col_media, col_summary = st.columns([1, 1.25])

    with col_media:
        st.subheader("🎥 Source Court Media")
        if media_file and Path(media_file).exists():
            if Path(media_file).suffix.lower() in [".mp4", ".mov", ".mkv"]:
                st.video(media_file)
            else:
                st.audio(media_file)

        st.subheader("📜 Full Chronological Transcript")
        
        # Build 3 view datasets: Parallel, Pure Original, Pure English
        parallel_data = []
        orig_data = []
        eng_data = []

        for s in res["full_transcript_sentences"]:
            eng_text = s.get("translated_text") or s.get("text", "")
            orig_text = s.get("original_text") or s.get("text", "")
            speaker = s.get("speaker", "Court Participant")
            st_str = f"{s['start_time']:05.1f}s"
            et_str = f"{s['end_time']:05.1f}s"

            parallel_data.append({
                "Start": st_str,
                "End": et_str,
                "Speaker": speaker,
                f"Original ({lang_label})": orig_text,
                "English Translation": eng_text
            })
            orig_data.append({
                "Start": st_str,
                "End": et_str,
                "Speaker": speaker,
                f"Transcript ({lang_label})": orig_text
            })
            eng_data.append({
                "Start": st_str,
                "End": et_str,
                "Speaker": speaker,
                "Transcript (English)": eng_text
            })

        tab_parallel, tab_orig, tab_eng = st.tabs([
            f"🌐 Parallel Bilingual ({lang_label} + English)",
            f"🗣️ Original Language ({lang_label})",
            "🇬🇧 English Translation"
        ])

        with tab_parallel:
            st.dataframe(pd.DataFrame(parallel_data), height=380, use_container_width=True)
        with tab_orig:
            st.dataframe(pd.DataFrame(orig_data), height=380, use_container_width=True)
        with tab_eng:
            st.dataframe(pd.DataFrame(eng_data), height=380, use_container_width=True)

    with col_summary:
        if judicial_only:
            st.subheader(f"⚖️ Judicial Judgment & Verdict Summary ({res['summarization_method']})")
            st.caption("Authoritative judicial ruling words delivered by the Judge after hearing both parties • In English & Original Language")
        else:
            st.subheader(f"📌 Key Extractive Summary ({res['summarization_method']})")
            st.caption("Sampled chronologically across entire video duration • Both English and Original Language")

        sents_list = res.get("extractive_summary_sentences", [])
        if not sents_list:
            st.info("ℹ️ No sentences matched current criteria. Try unchecking 'Extract Judicial Judgment Words Only' or adjusting compression ratio.")
        else:
            for idx, s in enumerate(sents_list, 1):
                legal_type = s.get("legal_type", "STATEMENT")
                if legal_type == "JUDICIAL_RULING" or s.get("is_ruling"):
                    badge_html = '<span class="badge-ruling">⚖️ JUDICIAL RULING / VERDICT</span>'
                elif legal_type == "ADVOCATE_ALLEGATION" or s.get("is_allegation"):
                    badge_html = '<span class="badge-allegation">⚠️ ADVOCATE ALLEGATION</span>'
                else:
                    badge_html = '<span class="badge-procedural">TESTIMONY / EVIDENCE</span>'

                eng_summary = s.get("translated_text") or s.get("text", "")
                orig_summary = s.get("original_text") or s.get("text", "")
                speaker_display = s.get("speaker") or ("Judge / Presiding Officer" if s.get("is_ruling") else "Court Participant")

                with st.container(border=True):
                    top_l, top_r = st.columns([2.5, 1.5])
                    top_l.markdown(f"**{idx}. ⏱️ [{s['start_time']:05.1f}s – {s['end_time']:05.1f}s]** &nbsp; • &nbsp; *{speaker_display}*")
                    top_r.markdown(f"<div style='text-align:right;'>{badge_html}</div>", unsafe_allow_html=True)

                    st.markdown("**🇬🇧 English Key Summary:**")
                    st.markdown(f"<div style='font-size:1.02rem; color:#1E3A8A; font-weight:600; line-height:1.45; margin-bottom:8px;'>{eng_summary}</div>", unsafe_allow_html=True)

                    if orig_summary:
                        st.markdown(f"**🗣️ Original Transcript ({lang_label}):**")
                        st.markdown(f"<div style='font-size:1.0rem; color:#065F46; background-color:#F0FDF4; border-left:4px solid #10B981; padding:8px 12px; border-radius:4px; font-weight:500; line-height:1.4; margin-bottom:6px;'>{orig_summary}</div>", unsafe_allow_html=True)

                    st.caption(f"Timeline Anchor: {s['start_time']:05.1f}s – {s['end_time']:05.1f}s • Salience Score: {s.get('final_salience_score', 0.0)}")

    # Download Exports Row
    st.markdown("---")
    st.subheader("📥 Export Traceable Reports")
    d1, d2, d3 = st.columns(3)

    case_stem = res["case_id"]
    case_dir = Path("outputs") / case_stem

    txt_f = case_dir / f"{case_stem}_summary.txt"
    json_f = case_dir / f"{case_stem}_summary.json"
    pdf_f = case_dir / f"{case_stem}_summary.pdf"

    if txt_f.exists():
        with open(txt_f, "r", encoding="utf-8") as f:
            d1.download_button("📄 Download Plain Text (.txt)", f.read(), file_name=txt_f.name, mime="text/plain")

    if json_f.exists():
        with open(json_f, "r", encoding="utf-8") as f:
            d2.download_button("📊 Download Structured JSON (.json)", f.read(), file_name=json_f.name, mime="application/json")

    if pdf_f.exists():
        with open(pdf_f, "rb") as f:
            d3.download_button("📑 Download Printable PDF (.pdf)", f.read(), file_name=pdf_f.name, mime="application/pdf")
