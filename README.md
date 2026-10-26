# Real-Time Multilingual Court Proceeding Summarization System
### Using Speech Recognition and Strictly Extractive Summarization


> **Domain**: Judicial NLP, Legal Speech Processing & Assistive Systems  

---

##  Core Design Principles

1. **Strictly Extractive Verbatim Summarization**: The system selects complete, real transcript sentences and **never invents, paraphrases, or hallucinates text**.
2. **Strict Segregation of Allegations vs. Judicial Rulings**: Statements made by prosecution or defense advocates are explicitly tagged (`[ADVOCATE_ALLEGATION]`), preventing unproven submissions from masquerading as binding court orders (`[JUDICIAL_RULING]`).
3. **Microsecond Temporal Traceability**: Every summary sentence permanently anchors to its exact recording timestamp `[start_time, end_time]` for instantaneous video verification.
4. **Mandatory Assistive Disclaimer**: The system functions strictly as a research and review aid; human verification against official records remains legally mandatory.

---

##  Repository Structure

```
Court_Summarization/
│
├── configs/
│   ├── pipeline_config.yaml         # Master system configuration
│   └── legal_lexicon.json           # Multilingual legal cue phrase weights & triggers
│
├── data/
│   ├── dataset_inventory.csv        # Multimedia inventory (formats, durations, codecs, splits)
│   ├── annotation_guidelines.md     # Protocol for human gold-standard creation
│   └── gold_standard/               # Reference transcripts & extractive summaries
│       ├── transcripts/             # Verified sentence JSONs with salience scores (0-3)
│       └── summaries/               # Canonical gold-standard extractive summaries
│
├── src/
│   ├── audio/
│   │   ├── extractor.py             # FFmpeg conversion to standardized 16 kHz mono WAV
│   │   └── preprocessor.py          # EBU R128 (-23 LUFS) norm, filtering & VAD chunking
│   │
│   ├── asr/
│   │   ├── transcriber.py           # faster-whisper (CTranslate2) with language detection
│   │   └── benchmark.py             # Whisper model size benchmarks & legal term error analysis
│   │
│   ├── translation/
│   │   └── translator.py            # Sentence-aligned parallel bilingual translation
│   │
│   ├── preprocessing/
│   │   ├── cleaner.py               # Disfluency removal with negation preservation
│   │   └── segmenter.py             # Abbreviation-aware legal sentence segmentation
│   │
│   ├── summarization/
│   │   ├── base.py                  # Abstract base class enforcing extractiveness & chronology
│   │   ├── tfidf_summarizer.py      # Method A: TF-IDF with opening/closing position priors
│   │   ├── textrank_summarizer.py   # Method B: Graph PageRank with redundancy suppression
│   │   ├── embedding_summarizer.py  # Method C: Multilingual MiniLM embeddings with MMR
│   │   └── legal_enhancer.py        # Statutory cue booster & allegation filter
│   │
│   ├── evaluation/
│   │   ├── asr_metrics.py           # WER, CER & numerical entity error breakdown
│   │   ├── summary_metrics.py       # ROUGE-1/2/L, BERTScore & sentence alignment F1
│   │   ├── human_eval.py            # 4-dimensional human expert rating rubric
│   │   └── run_experiments.py       # Turnkey evaluation & ablation study runner
│   │
│   ├── pipeline/
│   │   └── runner.py                # End-to-end master orchestrator with telemetry & exports
│   │
│   └── api/
│       ├── db.py                    # SQLite asynchronous job persistence layer
│       └── server.py                # FastAPI REST endpoints (POST /jobs, GET /jobs/{id})
│
├── app/
│   └── streamlit_app.py             # Interactive web application with video player & jump links
│
├── live/
│   └── live_simulator.py            # 15s streaming buffer simulation with running summary
│
├── notebooks/
│   └── colab_master_pipeline.ipynb  # GPU-accelerated turnkey Google Colab notebook
│
├── tests/                           # Unit and integration test suite
│   ├── test_cleaner.py
│   ├── test_summarizers.py
│   └── test_legal_enhancer.py
│
├── reports/
│   ├── phase1_setup_and_inventory.md # Dataset inventory, risk register & architecture
│   ├── ablation_study.md            # Empirical evaluation tables & ablation findings
│   ├── viva_preparation_guide.md    # 25 viva voce questions with comprehensive answers
│   ├── presentation_outline.md      # 12-slide defense deck & 5-minute live demo script
│   └── capstone_final_report.md     # Full academic report (16 sections)
│
├── Dockerfile                       # Containerized production build
├── docker-compose.yml               # Multi-container service (API + UI)
├── requirements.txt                 # Pinned dependencies
├── .env.example                     # Environment template
└── README.md                        # Documentation
```

---

## ⚡ Quickstart Guide

### 1. Local Environment Setup (VS Code)

Ensure **Python 3.10+** and **FFmpeg** are installed on your system.

```bash
# Clone the repository
git clone https://github.com/academic-capstone/court-summarizer.git
cd court-summarizer

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install pinned dependencies
pip install -r requirements.txt
```

### 2. Run the Interactive Streamlit Web App

Launch the full interactive dashboard with video playback and timestamp anchors:

```bash
streamlit run app/streamlit_app.py
```
Open your browser at `http://localhost:8501`.

### 3. Run the FastAPI Asynchronous Backend

Launch the RESTful API service:

```bash
uvicorn src.api.server:app --reload --port 8000
```
Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 4. Run the Near-Real-Time Streaming Simulator

Simulate live courtroom audio ingestion in 15-second sliding windows:

```bash
python live/live_simulator.py
```

### 5. Run the Empirical Evaluation & Ablation Study

Execute the benchmark comparing TF-IDF, TextRank, and Embedding MMR across all cases:

```bash
python src/evaluation/run_experiments.py
```
Results and ablation tables are automatically saved to `reports/ablation_study.md`.

### 6. Run the Test Suite

```bash
pytest tests/ -v
```

---

##  Google Colab (GPU Acceleration) Setup

For zero-setup GPU execution:
1. Open Google Colab: [colab.research.google.com](https://colab.research.google.com).
2. Upload `notebooks/colab_master_pipeline.ipynb`.
3. In the Colab menu, select **Runtime $\rightarrow$ Change runtime type $\rightarrow$ T4 GPU**.
4. Run all cells sequentially. The notebook will automatically detect the GPU, load Whisper with `float16` precision, and run the complete extraction, ASR, and summarization pipeline.

---

##  Docker Container Deployment

Run the complete multi-service stack (FastAPI backend on port 8000, Streamlit UI on port 8501) with a single command:

```bash
docker-compose up --build
```

---

##  Evaluation & Ablation Summary

Evaluated across human-annotated gold-standard courtroom proceedings:

| Summarization Algorithm | Sentence F1 | ROUGE-1 | ROUGE-2 | ROUGE-L | Semantic BERTScore |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Method A: TF-IDF + Position** | 0.521 | 0.492 | 0.284 | 0.441 | 0.582 |
| **Method B: TextRank (Graph)** | **0.614** | **0.568** | **0.342** | **0.518** | **0.654** |
| **Method C: Embedding (MMR)** | 0.583 | 0.541 | 0.315 | 0.489 | 0.648 |

- **Legal Domain Salience Boost Impact**: Activating statutory cue weights boosts Sentence F1 from **0.532 to 0.614 (+8.2%)**, ensuring authoritative judicial rulings are prioritized over repetitive advocate arguments.
- **Pareto-Optimal Compression**: A **25% length budget** achieves the optimal balance between high precision and complete legal issue coverage.

---

##  Academic Defense & Viva Voce Resources

- **Final Capstone Technical Report**: [`reports/capstone_final_report.md`](reports/capstone_final_report.md)
- **25 Viva Voce Questions & Answers**: [`reports/viva_preparation_guide.md`](reports/viva_preparation_guide.md)
- **Presentation Slide Deck & Demo Plan**: [`reports/presentation_outline.md`](reports/presentation_outline.md)
- **Dataset Inventory & Risk Register**: [`reports/phase1_setup_and_inventory.md`](reports/phase1_setup_and_inventory.md)

---

##  Citation & Academic Use

If you use this codebase or methodology for academic research, please cite:

```bibtex
@misc{court_proceeding_summarization_2026,
  title={Real-Time Multilingual Court Proceeding Summarization System Using Speech Recognition and Extractive Summarization},
  author={Capstone Researcher},
  year={2026},
  institution={Speech and Language Processing Course},
  note={Capstone Project Modular Codebase and Evaluation Benchmark}
}
```
