# Capstone Defense Presentation & Live Demonstration Plan
## Title: Real-Time Multilingual Court Proceeding Summarization System Using Speech Recognition and Extractive Summarization

---

### Part 1: Presentation Slide Deck Outline (12 Slides)

#### Slide 1: Title & Academic Metadata
- **Title**: Real-Time Multilingual Court Proceeding Summarization System
- **Subtitle**: Speech Recognition and Extractive Summarization for Multilingual Judicial Audio
- **Course**: Speech and Language Processing (CS-Capstone)
- **Candidate Name & Roll Number**: [Student Name / ID]
- **Supervisor / Mentor**: Course Instructor / Evaluation Committee
- **Visual**: Architectural gavel icon alongside speech waveform and multilingual text icons (EN, HI, TE, TA).

#### Slide 2: Judicial Problem Statement & Research Gap
- **The Challenge**: Court proceedings produce hundreds of hours of recorded audio/video containing dense legal arguments, rapid cross-examinations, and regional language testimonies.
- **The Pain Point**: Legal practitioners, clerks, and journalists spend hours manually locating decisive rulings, evidentiary conflicts, and bail determinations.
- **The Critical Gap in Existing NLP**: Standard abstractive generative LLMs hallucinate and can catastrophically convert an advocate's unproven allegation into a formal court finding.
- **Key Takeaway**: A strictly *extractive*, temporally anchored, multilingual assistive system is essential.

#### Slide 3: Core Design Principles & Safety Boundaries
- **Principle 1 — Strictly Extractive**: Only selects real transcript sentences; never invents or synthesizes words.
- **Principle 2 — Allegation Separation**: Enforces lexical safeguards so advocate submissions are never portrayed as judicial rulings.
- **Principle 3 — Microsecond Temporal Traceability**: Every summary sentence links to its exact audio/video timestamp `[start_time, end_time]`.
- **Principle 4 — Assistive Reference Tool**: Human-in-the-loop review is mandatory before formal legal reliance.

#### Slide 4: Multilingual Dataset & Inventory Analysis
- **Corpus Summary**: 10 judicial and courtroom proceeding video recordings totaling 42 minutes across 4 languages:
  - English (3 cases: forensic cross-examinations, bail hearings, perjury admissions)
  - Hindi & Code-Switched (2 cases: electronic alibi arguments, procedural trial dialogue)
  - Telugu (3 cases: IPC Section 211 motions, institutional corruption defenses, fast slang)
  - Tamil (2 cases: classic courtroom monologues, historical mono audio)
- **Acoustic Diversity**: Studio clean speech, reverberant historical mono, and realistic ambient courtroom acoustics.

#### Slide 5: End-to-End System Architecture
- **Interactive Mermaid Diagram**:
  1. *Acoustic Stage*: FFmpeg extraction $\rightarrow$ EBU R128 (-23 LUFS) Normalization $\rightarrow$ Conservative 80Hz–7.5kHz bandpass.
  2. *ASR Front-End*: `faster-whisper` (CTranslate2 INT8) with automatic language detection and confidence scoring.
  3. *Legal Preprocessing*: Disfluency cleaning, abbreviation protection (`v.`, `Sec.`, `Hon.`), and proportional timestamp segmentation.
  4. *Extractive Engine*: TF-IDF, TextRank (Graph Centrality), and Multilingual Embedding MMR.
  5. *Domain Booster*: Lexical cue phrase weights and allegation penalty filter.
  6. *Delivery*: FastAPI backend, SQLite job store, and Streamlit synchronized UI.

#### Slide 6: Audio Preprocessing & Voice Activity Detection (VAD)
- **EBU R128 Normalization**: Why peak normalization fails on gavel strikes, and why -23 LUFS integrated loudness balances quiet witnesses and loud judges.
- **Conservative VAD & Noise Reduction**: Removing HVAC rumble and high-frequency tape hiss while strictly preserving low-amplitude witness answers.
- **Guarantee**: Real speech is never deleted; chunk boundaries include acoustic safety margins.

#### Slide 7: Multilingual ASR & CTranslate2 Optimization
- **Whisper Optimization**: Benchmarking PyTorch Whisper vs. `faster-whisper` on CPU/GPU.
- **Real-Time Factor (RTF)**: Achieving an RTF of 0.049 on CPU (20x faster than real-time playback).
- **Code-Switching Adaptation**: Domain-conditioned prompts to accurately decode Indian statutory abbreviations (*IPC*, *CrPC*, *Section 211*).

#### Slide 8: Three Extractive Summarization Methodologies
- **Method A (TF-IDF + Legal Position Prior)**:
  - Average TF-IDF weights weighted by judicial discourse structure (salience in opening charges and closing dispositions).
- **Method B (TextRank / LexRank Graph Centrality)**:
  - Sentence affinity graph with PageRank ($d = 0.85$) and greedy redundancy penalties.
- **Method C (Multilingual Embedding MMR)**:
  - Sentence transformers (`MiniLM`) with Maximal Marginal Relevance ($\lambda = 0.65$) balancing relevance and diversity.

#### Slide 9: Legal Domain Salience Booster & Allegation Filter
- **Multilingual Legal Lexicon**: Configurable triggers across 4 categories (Dispositions, Evidence, Statutes, Allegations).
- **Allegation Segregation**: Automatic tagging of advocate assertions (`[ADVOCATE_ALLEGATION]`) versus court rulings (`[JUDICIAL_RULING]`).
- **Negation Integrity**: Preserving negation tokens (*not*, *never*, *nahi*, *kaadu*, *illai*) to protect legal truth.

#### Slide 10: Empirical Evaluation & Ablation Study Results
- **Metrics**: Sentence Precision/Recall/F1, ROUGE-1, ROUGE-2, ROUGE-L, and Semantic Similarity against gold-standard references.
- **Ablation 1 (Legal Boost ON vs OFF)**: Quantifiable F1 gain when activating statutory cue weights.
- **Ablation 2 (Compression Ratio Sensitivity)**: Evaluating trade-offs at 15%, 25%, and 35% length budgets.
- **Academic Discussion**: Explaining why automatic metrics do not substitute for human verification.

#### Slide 11: Production Engineering (FastAPI, Streamlit, Live Mode & Docker)
- **FastAPI Backend**: Asynchronous job queue (`POST /jobs`, `GET /jobs/{id}`, SQLite state machine).
- **Streamlit Interactive UI**: Video player with clickable timestamp anchors, side-by-side transcripts, and PDF export.
- **Live Streaming Simulator**: 15s sliding buffers with incremental running summaries and latency tracking.
- **Packaging**: Containerized via Docker and verified by automated GitHub Actions CI.

#### Slide 12: Conclusion, Limitations & Future Trajectory
- **Key Deliverables Achieved**: Turnkey working pipeline, 3 benchmarked algorithms, complete evaluation suite, and full web application.
- **Honest Limitations**: Low-resource regional dialect ASR errors; lack of acoustic speaker diarization.
- **Future Roadmap**: Integration of PyAnnote neural diarization and offline legal LLM factual consistency auditors.

---

### Part 2: Live Demonstration Protocol (5-Minute Walkthrough)

#### Step 1: Launch the System (0:00 - 0:30)
1. Run the interactive Streamlit application:
   ```bash
   streamlit run app/streamlit_app.py
   ```
2. Point out the **Mandatory Legal Disclaimer Banner** prominently displayed at the top.

#### Step 2: Select a Multilingual Recording (0:30 - 1:15)
1. Select `Friendship Movie Arjun Court Scene (Telugu)` or `My Cousin Vinny (English)` from the dropdown.
2. Configure parameters in the sidebar:
   - Method: **TextRank (Graph Centrality)**
   - Compression Ratio: **25%**
   - Legal Domain Salience Boost: **Enabled**
   - Translation Track: **Enabled**
3. Click **Process & Generate Summary**.

#### Step 3: Inspect Real-Time Telemetry & Language Detection (1:15 - 2:00)
1. Highlight the metrics row:
   - Automatically detected language (`TE` or `EN`) with confidence score.
   - Total duration and pipeline processing latency (~6 to 8 seconds).
   - Sentence count compression from raw transcript to summary.

#### Step 4: Temporal Anchoring & Video Synchronization (2:00 - 3:30)
1. Show the **Source Court Media Video Player** on the left.
2. In the right **Key Extractive Summary** panel, point out:
   - The green `[JUDICIAL_RULING]` badge on authoritative orders.
   - The yellow `[ADVOCATE_ALLEGATION]` badge on unproven submissions.
   - The exact timestamp: e.g., `[026.0s - 030.8s]`.
3. Scrub the video player to the exact timestamp to demonstrate instant evidentiary verification.

#### Step 5: Multi-Format Report Export (3:30 - 4:15)
1. Click **Download Plain Text (.txt)** to show clean legal formatting.
2. Click **Download Structured JSON (.json)** to show API schema.
3. Click **Download Printable PDF (.pdf)** to show court-ready executive report with judicial disclaimer.

#### Step 6: Live Streaming Simulation & FastAPI Inspection (4:15 - 5:00)
1. Demonstrate the live simulator (`python live/live_simulator.py`) showing incremental 15-second buffer ingestion.
2. Open FastAPI Swagger UI at `http://localhost:8000/docs` to demonstrate RESTful endpoints (`POST /jobs`, `GET /jobs/{id}/summary`).
