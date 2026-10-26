# Gold-Standard Annotation Protocol & Guidelines
## Capstone Project: Real-Time Multilingual Court Proceeding Summarization System

---

### 1. Overview & Annotation Purpose
Because raw courtroom audio lacks human-verified ground-truth transcripts and reference summaries, this guide defines the rigorous standard for curating a **Gold-Standard Evaluation Set** across the 10 court videos (English, Hindi, Telugu, Tamil).

Ground-truth annotations serve two critical purposes:
1. **Speech Recognition Evaluation**: Measuring Word Error Rate (WER) and Character Error Rate (CER) per language.
2. **Extractive Summarization Evaluation**: Calculating sentence-level Precision/Recall/F1, ROUGE (ROUGE-1, ROUGE-2, ROUGE-L), and semantic BERTScore.

---

### 2. Core Legal Annotation Principles

1. **Strict Verbatim Accuracy**:
   - Transcripts must capture verbatim spoken utterances. Do not substitute synonyms or normalize colloquial dialect into textbook grammar.
   - For code-switched phrases (e.g., Telugu mixed with English legal terms like *"Section 211 IPC"* or *"anticipatory bail"*), transcribe the English term in Latin script and regional words in Telugu script.

2. **Strictly Extractive Reference Summaries**:
   - The reference summary **must consist solely of complete sentences selected directly from the transcript**.
   - **Never rewrite, paraphrase, or merge partial sentences** into new synthetic formulations.

3. **Separation of Allegations vs. Judicial Findings**:
   - Statements made by prosecution or defense advocates must be tagged as `ARGUMENT` or `ALLEGATION`.
   - Authoritative orders, rulings, or sustained objections delivered by the presiding judge must be tagged as `RULING` or `DISPOSITION`.
   - **Failure Rule**: An extractive summary that presents a defense or prosecution assertion as an established court fact is considered legally flawed.

---

### 3. Sentence-Level Salience Scoring Scale (0 to 3)

Each sentence in the reference transcript is assigned a salience score:

| Score | Label | Description & Inclusion Criteria |
| :---: | :--- | :--- |
| **3** | **Critical (Must Include)** | Decisive judicial rulings, formal charges framed, pivotal cross-examination admissions (e.g., witness contradicting physical evidence), bail grant/denial orders. |
| **2** | **Important (High Priority)** | Substantive legal arguments referencing statutory sections, evidentiary exhibits presented (CCTV, tire marks, call logs), sworn witness affirmations. |
| **1** | **Contextual (Supplementary)** | Procedural remarks, courtroom identification of parties, standard introductory declarations. |
| **0** | **Irrelevant (Exclude)** | Pleasantries, requests for water, microphone adjustments, repetitions, sustained administrative interruptions. |

> **Gold-Standard Extraction Rule**: A reference extractive summary consists of all sentences with a Salience Score of **3**, plus top-ranked Score **2** sentences until the compression budget (typically 20% to 25% of the total transcript length) is satisfied.

---

### 4. Canonical Annotation JSON Schema

Reference files must be saved under `data/gold_standard/transcripts/<Case_ID>.json`:

```json
{
  "case_id": "CASE_EN_02",
  "source_title": "Law Abiding Citizen (2009)",
  "language": "en",
  "annotator_id": "ANNOTATOR_01",
  "verification_status": "double_checked",
  "sentences": [
    {
      "sentence_id": 1,
      "speaker": "Judge Laura Burch",
      "speaker_role": "Judge",
      "start_time": 12.4,
      "end_time": 17.8,
      "text": "Mr. Shelton, you are charged with two counts of first-degree murder.",
      "salience_score": 3,
      "category": "CHARGES_FRAMED",
      "in_gold_summary": true
    },
    {
      "sentence_id": 2,
      "speaker": "Prosecutor",
      "speaker_role": "Prosecution",
      "start_time": 18.2,
      "end_time": 22.0,
      "text": "The State vehemently opposes bail due to the heinous nature of these killings.",
      "salience_score": 2,
      "category": "ARGUMENT",
      "in_gold_summary": true
    },
    {
      "sentence_id": 3,
      "speaker": "Clyde Shelton",
      "speaker_role": "Defendant",
      "start_time": 23.5,
      "end_time": 25.1,
      "text": "I understand your honor.",
      "salience_score": 0,
      "category": "PROCEDURAL",
      "in_gold_summary": false
    }
  ]
}
```

---

### 5. Multi-Annotator Inter-Rater Reliability (Cohen's Kappa)

When multiple human raters annotate salience:
- Annotate at least 2 common videos independently.
- Calculate Cohen's Kappa ($\kappa$) on binary sentence inclusion ($1 = \text{in gold summary}, 0 = \text{excluded}$):
  $$\kappa = \frac{p_o - p_e}{1 - p_e}$$
- Aim for $\kappa \ge 0.72$, indicating substantial inter-annotator agreement.
