# Phase 1: Setup, Architectural Planning, Dataset Inventory & Risk Register
## Capstone Project: Real-Time Multilingual Court Proceeding Summarization System

---

### 1. Problem Statement & Research Motivation
Court hearings across multilingual judicial jurisdictions (e.g., Supreme Court and High Courts of India, federal and state appellate courts) produce extensive audio/video recordings. Proceedings frequently involve multiple official and regional languages (English, Hindi, Telugu, Tamil) alongside rapid code-switching, complex legal jargon, and evidentiary cross-examinations.

Legal professionals, judicial clerks, law students, investigative journalists, and citizens face extreme friction:
1. **Temporal Burden**: Reviewing multi-hour recordings to isolate critical rulings, witness contradictions, or bail orders requires prohibitive manual labor.
2. **Linguistic Heterogeneity**: Testimonies often occur in regional vernaculars while legal statutes and case law citations are presented in English.
3. **Risk of Hallucination**: Generative abstractive summarization models (e.g., standard LLMs) suffer from stochastic confabulation, often transforming mere advocate allegations into authoritative judicial findings.

**Proposed Solution**: A strictly **extractive**, timestamp-traceable multilingual speech-to-summary pipeline. The system transcribes spoken courtroom audio, segments utterances into clean timestamped units, and applies graph-theoretic, semantic, and domain-informed extractive algorithms. Every summary sentence is an exact, unedited excerpt mapped directly to its temporal offset in the original media.

---

### 2. Capstone Project Objectives & Scope Boundaries

#### Primary Objectives:
- **High-Fidelity Audio Extraction & Preprocessing**: Normalize diverse acoustic dynamics (-23 LUFS) and eliminate non-speech silence while strictly retaining quiet witness testimony.
- **Robust Multilingual ASR**: Transcribe English, Hindi, Telugu, and Tamil speech with automated language identification and confidence scoring using Whisper / faster-whisper.
- **Verbatim Extractive Summarization**: Implement and empirically benchmark three distinct extractive methods:
  - **Method A**: Frequency-based (TF-IDF with position/length priors).
  - **Method B**: Graph-centrality (TextRank / LexRank with cosine similarity and MMR redundancy control).
  - **Method C**: Semantic Embedding (Multilingual Sentence-BERT / MiniLM with clustering & Maximal Marginal Relevance).
- **Legal-Domain Enhancement**: Apply a multilingual statutory and evidentiary cue lexicon, enforce negation preservation, and distinctively segregate advocate arguments from binding judicial rulings.
- **Traceable Temporal Navigation**: Provide exact `[start_time, end_time]` anchors for every summary sentence, enabling instant playback verification.

#### Scope Boundaries & Safety Disclaimers:
- **Assistive Tool Only**: The system does not generate legal advice, predict judicial outcomes, or synthesize new statutory interpretations.
- **Strict Human-in-the-Loop**: All outputs must be audited against original audio/video before formal filing.

---

### 3. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph Ingestion ["Phase 2 & 3: Audio Ingestion & Acoustic Preprocessing"]
        V[Court Video (.mp4 / .mkv / .avi)] -->|FFmpeg Extraction| WAV[16 kHz Mono WAV]
        WAV --> NORM[Loudness Normalization -23 LUFS]
        NORM --> VAD[Conservative VAD / Silence Trimming]
        VAD --> CHUNKS[Timestamped Audio Chunks]
    end

    subgraph ASR_Trans ["Phase 4 & 5: Multilingual ASR & Optional Translation"]
        CHUNKS --> WHISPER[faster-whisper Multilingual ASR]
        WHISPER --> LANG[Language Detection & Confidence]
        WHISPER --> RAW_TX[Raw Timestamped Transcript JSON]
        RAW_TX -->|Optional| TRANSLATE[Cross-Lingual Sentence Alignment]
    end

    subgraph Preproc ["Phase 6: Legal Cleaning & Sentence Segmentation"]
        RAW_TX --> CLEAN[Hesitation Normalizer & Entity Preserver]
        CLEAN --> SEG[Boundary-Aware Sentence Segmentation]
        SEG --> SENT_TBL[Indexed Sentence Table with Timestamps]
    end

    subgraph Extractive_Engine ["Phase 7 & 8: Extractive Summarization & Legal Boosting"]
        SENT_TBL --> M_TFIDF[Method A: TF-IDF + Position]
        SENT_TBL --> M_TRANK[Method B: TextRank / LexRank]
        SENT_TBL --> M_EMBED[Method C: Multilingual MiniLM + MMR]
        
        LEX[configs/legal_lexicon.json] --> BOOST[Legal Domain Salience Booster]
        NEG[Negation & Allegation Filter] --> BOOST
        
        M_TFIDF --> BOOST
        M_TRANK --> BOOST
        M_EMBED --> BOOST
        
        BOOST --> TOP_K[Salience Ranking & Constraint Budgeting]
        TOP_K --> FINAL_SUM[Chronologically Ordered Extractive Summary]
    end

    subgraph Evaluation_Delivery ["Phase 9 - 11: Evaluation, API & UI"]
        FINAL_SUM --> EVAL[WER, ROUGE-1/2/L, BERTScore & Human Rubric]
        FINAL_SUM --> API[FastAPI Backend + SQLite Storage]
        FINAL_SUM --> UI[Streamlit Interactive Video-Synchronized UI]
        FINAL_SUM --> EXPORT[Export JSON / TXT / PDF Reports]
    end
```

---

### 4. Comprehensive Risk Register & Mitigation Strategy

| Risk ID | Risk Description | Severity | Probability | Impact Area | Concrete Mitigation Strategy |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **R-01** | **Degraded Acoustic Quality & Reverberation** (historic mono recordings, loud courtroom ambient noise) | High | High | ASR WER | Apply conservative two-pass loudness normalization (`ffmpeg loudnorm`) and band-pass filtering (80Hz - 7500Hz). Avoid aggressive noise spectral subtraction that distorts low-amplitude consonants. |
| **R-02** | **Regional Language ASR Degradation & Code-Switching** (Whisper hallucinating during rapid Telugu/Hindi to English transitions) | High | Medium | Transcript Fidelity | Disable `condition_on_previous_text` to avoid repetitive hallucination loops; set `beam_size=5`; transcribe in native script and use multilingual semantic embeddings (`paraphrase-multilingual-MiniLM-L12-v2`). |
| **R-03** | **Legal Misrepresentation & Hallucination** (an allegation portrayed as a judicial finding) | Critical | Low (Strict) | Legal Reliability | **Architectural Guarantee**: Strictly extractive pipeline. Implement rule-based allegation tagging (e.g., *"prosecution contends"*) to prevent advocate submissions from masquerading as binding court orders. |
| **R-04** | **Compute & GPU Resource Bottlenecks** (inference latency on long courtroom recordings) | Medium | Medium | System Throughput | Use `faster-whisper` backed by CTranslate2 with INT8 quantization for CPU execution and FP16 for Colab CUDA. Employ VAD chunking to process speech segments in parallel. |
| **R-05** | **Data Privacy & Fair Use Compliance** (sensitive trial recordings, biometric audio data) | High | Low | Legal Ethics | Store media locally in designated directories; provide automated ephemeral file cleanup; sanitize personal phone numbers and identifiers; include permanent verification disclaimers. |

---

### 5. Dataset Inventory Summary

The active testbed contains **10 court proceeding video files** totaling **42 minutes and 38 seconds** across 4 languages:

- **English (3 cases)**:
  - `CASE_EN_01`: *My Cousin Vinny* (154.0s) - Expert witness cross-examination on automotive forensics.
  - `CASE_EN_02`: *Law Abiding Citizen* (180.5s) - Pretrial bail hearing confrontation and contempt ruling.
  - `CASE_EN_03`: *Legally Blonde* (208.6s) - High-stakes witness perjury breakdown.
- **Hindi & Code-Switched (2 cases)**:
  - `CASE_HI_01`: *Criminal Justice S3* (151.3s) - Defense arguments on electronic alibi and conditional bail.
  - `CASE_HI_EN_01`: *Court / State vs A Nobody* (315.0s) - Procedural criminal trial dialogue with heavy English-Hindi legal terminology.
- **Telugu (3 cases)**:
  - `CASE_TE_01`: *Friendship* (309.1s) - High-energy defense speech against institutional corruption.
  - `CASE_TE_02`: *Naandhi* (336.6s) - Section 211 IPC prosecution against unlawful confinement.
  - `CASE_TE_03`: *DJ Tillu* (285.2s) - Colloquial courtroom examination with modern slang and legal terms.
- **Tamil (2 cases)**:
  - `CASE_TA_01`: *Parasakthi* (299.0s) - Classic theatrical courtroom defense speech.
  - `CASE_TA_02`: *Parasakthi 480p* (299.0s) - Alternate resolution duplicate test clip for compression resilience.
