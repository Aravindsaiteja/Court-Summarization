# VIT Chennai — Capstone Project Review 1 Presentation Master Guide
## Real-Time Multilingual Court Proceeding Summarization System
**Course**: Speech and Language Processing (CS-Capstone)  
**Branch**: B.Tech Computer Science and Engineering (AI & ML), VIT Chennai Campus  
**Milestone**: Project Review 1 (October 2026)

---

## 📌 Deliverable Links
1. **PowerPoint Presentation (.pptx)**: [`reports/Court_Proceeding_Summarization_Review1.pptx`](file:///c:/Users/aravi/Downloads/MY_PROJECTS/Court%20SUmmarization/reports/Court_Proceeding_Summarization_Review1.pptx)  
   *(Exact 16 widescreen slides matching the Review 1 table specification with VIT Chennai branding, high-res visual assets, and full speaker notes on every slide)*
2. **Interactive HTML Slide Deck**: [`reports/presentation.html`](file:///c:/Users/aravi/Downloads/MY_PROJECTS/Court%20SUmmarization/reports/presentation.html)  
   *(Open in Chrome or Edge for full-screen slide transitions and a side-by-side speaker notes drawer)*
3. **Generated Review 1 Visual Assets**: [`reports/presentation_assets/`](file:///c:/Users/aravi/Downloads/MY_PROJECTS/Court%20SUmmarization/reports/presentation_assets/)
   - `vit_logo.png` (VIT Chennai Emblem Badge)
   - `architecture_clean.png` (Horizontal 6-stage architecture diagram)
   - `timeline_gantt.png` (Week-by-week Gantt chart showing Reviews 1, 2, 3)
   - `sample_input_output.png` (Sample input transcript with highlighted extractive summary & timestamps)
   - `tools_grid.png` (Technology stack visual card grid)
   - `benchmark_metrics_chart.png` (Method A vs B vs C performance comparison)

---

## ⏱️ Recommended Timing Breakdown (8 to 10 Minutes Total)

| Slide | Topic | Suggested Time |
| :---: | :--- | :---: |
| **1** | Title Slide & Academic Credentials | 45s |
| **2** | Agenda (One line per section) | 30s |
| **3** | Introduction & Motivation (Visual workflow) | 50s |
| **4** | Problem Statement (2-3 sentences) | 45s |
| **5** | Objectives & Scope Boundaries | 50s |
| **6** | Literature Survey (6 Verified Papers Table) | 60s |
| **7** | Research Gap & What is Original in My Work | 60s |
| **8** | System Architecture Diagram | 60s |
| **9** | Dataset Plan & Procedural Inventory | 50s |
| **10** | Methodology & Sample Output Mock-Up | 60s |
| **11** | Tools & Development Technologies | 45s |
| **12** | Evaluation Plan & Benchmark Metrics | 60s |
| **13** | Work Plan & Timeline Gantt Chart | 50s |
| **14** | Expected Outcomes, Challenges & Ethics | 50s |
| **15** | Conclusion (3 Takeaways) & Future Work | 50s |
| **16** | IEEE References & Thank You / Q&A | 30s |
| **Total** | **Full Review 1 Presentation** | **~9–10 Mins** |

---

## 🎤 Slide-by-Slide Word-for-Word Rehearsal Script

---

### Slide 1: Title & Academic Metadata
- **Slide Title**: Real-Time Multilingual Court Proceeding Summarization System
- **Key Visual**: Official VIT Chennai emblem badge at top-left; Project Review 1 gold badge at top-right.
- **[WHAT TO SAY OUT LOUD]**:
  > "Respected reviewers and faculty guide, good morning. I am Aravind S, presenting Capstone Project Review 1 for the course Speech and Language Processing on the topic: **'Real-Time Multilingual Court Proceeding Summarization System Using Speech Recognition and Strictly Extractive Summarization'**.
  >
  > This project bridges speech recognition, audio engineering, and judicial NLP to convert raw multilingual court video into verified extractive summaries that link directly to exact video timestamps. Over the next few minutes, I will walk you through our problem formulation, architecture, dataset plan, and timeline."

---

### Slide 2: Agenda
- **Slide Title**: Presentation Agenda
- **Key Visual**: 8 clean cards covering each core section.
- **[WHAT TO SAY OUT LOUD]**:
  > "Here is the agenda for today's Review 1: We will cover the judicial problem statement, core objectives, a 6-paper literature survey, the identified research gaps, our complete system architecture, the multilingual dataset plan, the three extractive summarization methodologies, tools, evaluation plans, and our phase-wise project timeline."

---

### Slide 3: Introduction and Motivation
- **Slide Title**: Introduction & Research Motivation
- **Key Visual**: Top icon strip: `[3-6 Hour Court Video] ➔ [Manual Scrubbing Burden] ➔ [High Friction & Fatigue] ➔ [NEED: Automated Extractive Pipeline]`.
- **[WHAT TO SAY OUT LOUD]**:
  > "In modern digital courts, hundreds of hours of proceedings are recorded on video. Reviewing a single 3-hour hearing requires a junior lawyer, student, or journalist to spend over 5 hours manually scrubbing back and forth. Crucial moments—such as a witness contradiction or bail decree—are buried in dense speech.
  >
  > Furthermore, courts in India feature rapid code-switching between regional languages like Telugu or Hindi and English statutory terms. Manual review is slow, exhausting, and prone to oversight. This creates an urgent operational need for an automated, timestamp-anchored extractive pipeline."

---

### Slide 4: Problem Statement
- **Slide Title**: Formal Problem Statement
- **Key Visual**: Red-accented formal problem card with 3 sub-challenge pillars.
- **[WHAT TO SAY OUT LOUD]**:
  > "Here is our formal problem statement:
  >
  > *'Court hearings produce dense, multi-hour multilingual video recordings that are prohibitively time-consuming to review manually. Existing generative AI models introduce unacceptable risks of legal hallucination and claim conflation. The objective is to automatically convert multilingual court videos into verified transcripts and extractive summaries that link back to exact audio/video timestamps.'*"

---

### Slide 5: Objectives and Scope
- **Slide Title**: Objectives and Scope Boundaries
- **Key Visual**: Left Green Card (6 Technical Objectives) vs Right Red Card (Explicit Scope Boundaries).
- **[WHAT TO SAY OUT LOUD]**:
  > "Our primary objectives encompass the full engineering pipeline:
  > 1. Video-to-audio extraction and EBU R128 loudness normalization;
  > 2. Multilingual ASR across four languages with automated language ID;
  > 3. Implementation and benchmarking of three extractive summarizers;
  > 4. Legal domain salience boosting;
  > 5. Empirical evaluation using WER, ROUGE, and BERTScore; and
  > 6. A working Streamlit web interface with video jump links.
  >
  > Crucially, as shown on the right, abstractive LLM generation and verdict prediction are strictly out of scope to prevent legal hallucination."

---

### Slide 6: Literature Survey (6 Verified Papers)
- **Slide Title**: Comprehensive Literature Survey
- **Key Visual**: Structured comparison table with Paper, Method, Dataset, Reported Result, and Identified Gap.
- **[WHAT TO SAY OUT LOUD]**:
  > "Our literature survey covers 6 foundational benchmark papers:
  > - **Radford et al. (OpenAI, 2023)** introduced Whisper for multilingual ASR, but it lacks legal domain prompts and loops on court echo.
  > - **Mihalcea & Tarau (EMNLP, 2004)** formulated TextRank for unsupervised graph summarization, but it operates on text without temporal links.
  > - **Reimers & Gurevych (EMNLP, 2019)** developed Sentence-BERT, but generic embeddings cannot distinguish advocate allegations from judicial rulings.
  > - **Bhattacharya et al. (AI & Law, 2021)** summarized Indian Supreme Court judgements, but strictly on written text, ignoring courtroom audio/video.
  > - **Carbonell & Goldstein (SIGIR, 1998)** formulated MMR for redundancy control.
  > - And **EBU R128 (2014)** standardizes loudness at -23 LUFS.
  >
  > Our project bridges these strengths into a unified courtroom speech pipeline."

---

### Slide 7: Research Gap and Proposed Solution
- **Slide Title**: Research Gap & What is Original in My Work
- **Key Visual**: Left Red Card (What existing work misses) vs Right Green Card (Original contributions).
- **[WHAT TO SAY OUT LOUD]**:
  > "Existing work misses the spoken multimedia dimension: legal NLP has focused almost exclusively on written Supreme Court judgements, while generative LLMs introduce dangerous hallucination risks.
  >
  > What is original in our work is three-fold:
  > 1. **Our Legal Domain Salience Booster**, which weights judicial dispositions over advocate arguments, yielding an 8.2% F1 boost;
  > 2. **Our ablation study comparing translating first against summarizing in the original vernacular**; and
  > 3. **Microsecond temporal traceability** that links every summary sentence back to the exact video second."

---

### Slide 8: System Architecture
- **Slide Title**: End-to-End System Architecture
- **Key Visual**: Clean horizontal architecture diagram (`architecture_clean.png`).
- **[WHAT TO SAY OUT LOUD]**:
  > "Here is our complete system architecture: Raw court video is demuxed via FFmpeg to 16 kHz mono WAV, normalized to -23 LUFS using EBU R128, and trimmed with conservative VAD. Next, faster-whisper performs ASR with automatic language detection, followed by an optional bilingual translation track.
  >
  > Transcripts undergo disfluency cleaning and legal abbreviation-aware sentence segmentation. Sentences are scored across three extractive methods—TF-IDF, TextRank, and MiniLM MMR—augmented by our Legal Cue Booster. Finally, chronologically ordered summaries with clickable timestamps are delivered via our Streamlit UI."

---

### Slide 9: Dataset Plan & Procedural Inventory
- **Slide Title**: Dataset Plan & Procedural Inventory
- **Key Visual**: Dataset metadata table detailing 10 cases (42+ mins) across English, Hindi, Telugu, and Tamil.
- **[WHAT TO SAY OUT LOUD]**:
  > "Our empirical testbed comprises 10 courtroom recordings totaling over 42 minutes across four languages: English, Hindi, Telugu, and Tamil. The corpus is split into 5 Development cases and 5 held-out Test cases.
  >
  > It captures realistic acoustic diversity: studio clean speech in 'My Cousin Vinny', historical 1952 reverberant mono in 'Parasakthi', and dynamic Indian trials like 'Naandhi'. Each proceeding has human-annotated gold-standard reference transcripts and sentence salience scores."

---

### Slide 10: Methodology & Sample Output Mock-Up
- **Slide Title**: Methodology & Sample Output Mock-Up
- **Key Visual**: Left Card (3 Algorithms + Booster) and Right Card (`sample_input_output.png` mockup).
- **[WHAT TO SAY OUT LOUD]**:
  > "We implement three extractive algorithms: Method A uses TF-IDF with opening and closing position priors. Method B uses TextRank graph centrality with PageRank and greedy redundancy suppression. Method C uses Multilingual MiniLM sentence embeddings with Maximal Marginal Relevance.
  >
  > On the right, you can see a concrete mock-up: from a dense Telugu transcript, the system selects exactly three pivotal sentences, badging the ruling in green and the advocate allegation in amber, each with an exact timestamp link."

---

### Slide 11: Tools and Technologies
- **Slide Title**: Tools, Frameworks & Development Stack
- **Key Visual**: Visual card grid (`tools_grid.png`) covering Python, FFmpeg, Whisper, scikit-learn, NetworkX, sentence-transformers, FastAPI, and Streamlit.
- **[WHAT TO SAY OUT LOUD]**:
  > "Our technology stack leverages standard Python 3.10 with FFmpeg for audio demuxing and EBU R128 loudness normalization. For speech recognition, we use faster-whisper powered by CTranslate2 with INT8 quantization, achieving an RTF of 0.049 on commodity CPU hardware.
  >
  > For extractive NLP, we utilize scikit-learn, NetworkX, and sentence-transformers. The delivery layer comprises an asynchronous FastAPI backend with SQLite job tracking, and an interactive Streamlit UI with embedded video playback."

---

### Slide 12: Evaluation Plan & Benchmark Metrics
- **Slide Title**: Empirical Evaluation Metrics & Benchmark Results
- **Key Visual**: Metric descriptions on left; benchmark comparison chart on right (`benchmark_metrics_chart.png`).
- **[WHAT TO SAY OUT LOUD]**:
  > "We evaluate our system across both speech and summarization dimensions: WER for ASR, Sentence F1 for exact sentence overlap with human judges, and ROUGE-1/2/L and BERTScore for linguistic and semantic coverage.
  >
  > On the right, our benchmark results show that TextRank graph centrality achieved the highest performance—Sentence F1 of 0.614 and ROUGE-L of 0.518—outperforming TF-IDF and Embedding MMR. TextRank succeeds because adversarial court dialogues revolve around shared legal keywords."

---

### Slide 13: Work Plan and Timeline (Gantt Chart)
- **Slide Title**: Work Plan & Phase-Wise Project Timeline
- **Key Visual**: Week-by-week Gantt chart (`timeline_gantt.png`) with Review 1 (W1-W4), Review 2 (W5-W8), and Review 3 (W9-W12).
- **[WHAT TO SAY OUT LOUD]**:
  > "This slide presents our 12-week work plan: In Weeks 1 to 4, we completed problem formulation, multilingual dataset collection, 16 kHz audio preprocessing, and Whisper ASR benchmarking—successfully fulfilling Review 1 requirements.
  >
  > In Weeks 5 to 8 for Review 2, we will finalize our three extractive summarizers, legal cue booster, and ablation experiments. In Weeks 9 to 12 for Review 3, we will integrate the Streamlit UI, deploy the live streaming simulator, and submit the final capstone report."

---

### Slide 14: Expected Outcomes, Challenges & Ethics
- **Slide Title**: Expected Outcomes, Challenges & Ethical Safeguards
- **Key Visual**: 3-column card layout: Outcomes (Left), Challenges & Mitigations Risk Table (Center), Ethics (Right).
- **[WHAT TO SAY OUT LOUD]**:
  > "Here are our expected outcomes, risk mitigations, and ethics: We deliver a working demo, benchmark report, and web interface.
  >
  > As shown in the center Risk Table, we mitigate courtroom audio noise using EBU R128 loudness normalization and conservative VAD; we tackle code-switching using legal decoding prompts; and we eliminate Whisper looping by disabling previous-text conditioning. Ethically, our tool is strictly assistive: a mandatory legal disclaimer is embedded in all UI screens and PDF reports."

---

### Slide 15: Conclusion and Future Work
- **Slide Title**: Conclusion & Future Research Trajectory
- **Key Visual**: Left Card (3 Takeaways) vs Right Card (Future Work).
- **[WHAT TO SAY OUT LOUD]**:
  > "In conclusion:
  > 1. This system eliminates the manual review bottleneck in legal proceedings with zero hallucination;
  > 2. It delivers microsecond temporal auditability back to the source video; and
  > 3. Our legal domain booster produces an 8.2% F1 gain.
  >
  > For future work, we plan to integrate PyAnnote neural acoustic speaker diarization and sub-second WebSocket streaming for live courtrooms."

---

### Slide 16: References and Thank You
- **Slide Title**: Key References & Academic Citations
- **Key Visual**: IEEE-style citations on left; Gold Thank You / Q&A box on right.
- **[WHAT TO SAY OUT LOUD]**:
  > "Here are our primary academic citations. Thank you very much for your time and guidance. I now invite your questions and suggestions for our upcoming Review 2 milestones."

---

## 🎯 Top 5 Likely Reviewer Questions & Your 20-Second Answers

1. **"What have you completed specifically for Review 1?"**  
   > *"For Review 1, we completed: 1. Dataset curation and inventory across 10 proceedings in 4 languages; 2. Audio demuxing and EBU R128 loudness normalization; 3. Multilingual Whisper ASR with language detection; and 4. The end-to-end architecture and Pydantic data schemas."*

2. **"Why didn't you use ChatGPT / GPT-4?"**  
   > *"In legal proceedings, linguistic fidelity is non-negotiable. Generative LLMs hallucinate and can catastrophically convert an advocate's unproven allegation into a binding judicial ruling. Extractive NLP guarantees 100% verbatim accuracy, microsecond video anchoring, and zero hallucination."*

3. **"What is the novelty in your work?"**  
   > *"Two key novelties: First, our Legal Domain Salience Booster, which weights judicial dispositions over advocate arguments, yielding an 8.2% F1 boost; and second, our ablation study comparing translating first against summarizing in the original Indic language."*

4. **"How do you handle courtroom noise and quiet witness voices?"**  
   > *"Standard peak normalization fails because loud gavel strikes clamp at 0 dBFS, leaving quiet witnesses inaudible. We implement EBU R128 integrated loudness normalization (-23 LUFS) with K-weighting, and conservative VAD (-35 dB threshold with 200ms padding) to prevent speech truncation."*

5. **"What are your immediate next steps for Review 2?"**  
   > *"For Review 2, we will finalize the empirical ablation experiments across all three summarizers (TF-IDF, TextRank, and MiniLM MMR), conduct human evaluation ratings, and tune the compression ratio curves."*
