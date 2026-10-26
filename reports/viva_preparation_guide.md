# Viva Voce Examination Preparation Guide
## Capstone Project: Real-Time Multilingual Court Proceeding Summarization System
### Comprehensive 25 Viva Questions with Exhaustive Model Answers

---

### Category 1: Problem Definition, Legal Domain & Core Architecture

#### Q1: Why did you choose strictly *extractive* summarization instead of modern *abstractive* generative models (e.g., GPT-4, Llama 3)?
**Model Answer:**
"In the legal domain, linguistic fidelity is non-negotiable. Abstractive Large Language Models (LLMs) suffer from stochastic generation and unconstrained hallucination. In legal proceedings, substituting a synonym or rephrasing a conditional clause can completely invert legal meaning—for example, converting an advocate's unproven allegation into a binding judicial finding, or altering the terms of a bail order. 
Our strictly extractive approach guarantees that every sentence in the summary is a verbatim, unedited excerpt from the actual spoken record, with an exact temporal anchor `[start_time, end_time]` mapped directly to the audio recording. This ensures complete auditability, evidentiary traceability, and legal reliability."

#### Q2: How does your system address the critical risk of confusing advocate allegations with binding judicial rulings?
**Model Answer:**
"We implement a specialized legal domain rules engine (`src/summarization/legal_enhancer.py`). Court transcripts contain distinct discursive categories: advocate submissions (prosecution/defense claims) versus authoritative judicial dispositions (rulings, orders, bail decisions). 
Our engine uses a multilingual legal cue lexicon (`configs/legal_lexicon.json`) that detects markers such as *'prosecution alleges'*, *'defense contends'* and assigns them an allegation tag with an salience penalty ($0.85\times$), while definitive judicial triggers (*'held'*, *'court orders'*, *'bail granted'*, *'acquitted'*) receive a high salience boost ($2.5\times$). Furthermore, each summary sentence is explicitly tagged in the UI and report with a provenance badge (`[JUDICIAL_RULING]` vs `[ADVOCATE_ALLEGATION]`), preventing any misrepresentation."

#### Q3: Why is temporal anchoring essential for courtroom audio summaries?
**Model Answer:**
"Unlike text-based document summarization where a user can quickly skim adjacent paragraphs, audio/video recordings require sequential playback. A 3-hour trial recording cannot be easily scanned. By attaching microsecond-accurate global timestamps `[start_time, end_time]` to every extracted sentence, our system provides instantaneous random-access navigation. A lawyer or judge can click directly on an extracted admission or bail clause to verify the tone, inflection, and surrounding acoustic context in the source recording."

---

### Category 2: Audio Engineering, Preprocessing & Voice Activity Detection (VAD)

#### Q4: Why standardize audio to 16 kHz mono 16-bit PCM WAV?
**Model Answer:**
"16 kHz sampling rate corresponds to a Nyquist frequency of 8 kHz, which fully captures human vocal formants and speech sibilance (typically between 300 Hz and 7.5 kHz) while discarding redundant high-frequency spectrum. Whisper and modern transformer-based ASR acoustic front-ends compute 80-channel log-mel spectrograms from 16 kHz audio with a 25ms window and 10ms hop size. Mono conversion eliminates channel phase cancellation artifacts and halves memory consumption without losing speech intelligibility."

#### Q5: What is EBU R128 loudness normalization and why is it preferred over simple peak normalization?
**Model Answer:**
"Peak normalization scales an entire audio file based on its highest instantaneous sample value. In courtroom audio, an isolated desk thud, gavel strike, or microphone click can produce a high peak amplitude, causing peak normalization to leave quiet witness testimony severely under-amplified. 
EBU R128 (ITU-R BS.1770-4) measures Integrated Loudness using K-weighted psychoacoustic filters that model perceived human hearing loudness over time, targeting -23 LUFS (Loudness Units relative to Full Scale). This dynamically brings quiet, distant witness testimonies and loud, amplified judicial statements to a uniform perceptual level."

#### Q6: How do you guarantee that Voice Activity Detection (VAD) never accidentally discards real witness speech?
**Model Answer:**
"Aggressive VAD or extreme spectral subtraction often treats quiet, hesitant witness speech as silence or noise, clipping critical monosyllabic answers (e.g., *'no'*, *'guilty'*). We address this by:
1. Employing conservative high-pass filtering (80 Hz) and low-pass filtering (7.5 kHz) to cut non-speech HVAC hum and hiss without touching speech formants.
2. Applying Silero VAD / FFmpeg silencedetect with a conservative threshold (-35 dB) and a generous minimum silence duration (500ms).
3. Padding chunk boundaries with 200ms acoustic margins, ensuring no onset or offset plosives are truncated."

---

### Category 3: Speech Recognition (ASR), Multilingual Code-Switching & Error Propagation

#### Q7: Why use `faster-whisper` backed by CTranslate2 instead of standard PyTorch Whisper?
**Model Answer:**
"Standard PyTorch Whisper on CPU suffers from significant computational overhead and memory bandwidth saturation, yielding a Real-Time Factor (RTF) close to 0.8–1.2 (almost real-time or slower). `faster-whisper` re-implements Whisper using CTranslate2, a dedicated C++ inference engine that applies weight quantization (INT8), fused matrix multiplications, and custom memory management. On our CPU testbed, this reduced the Real-Time Factor to 0.049 (approx. 20x faster than real-time), cutting inference latency from minutes to seconds with zero loss in word error rate."

#### Q8: How does the system handle code-switching between regional languages (Telugu/Hindi/Tamil) and English legal jargon?
**Model Answer:**
"Code-switching is ubiquitous in Indian courtrooms: advocates speak Telugu or Hindi while citing English statutory sections like *'Section 211 IPC'* or *'anticipatory bail'*. 
We configure Whisper with a legal domain prompt (`initial_prompt`) containing judicial lexicon and statutory terminology. This conditions the decoder autoregressive prior toward legal vocabulary. Furthermore, our sentence cleaner preserves English script tokens within regional Unicode sequences, and our summarization engine utilizes multilingual embeddings (`paraphrase-multilingual-MiniLM-L12-v2`) mapped into a shared vector space, allowing cross-lingual semantic comparison."

#### Q9: What is ASR Error Propagation, and how does your pipeline mitigate it?
**Model Answer:**
"ASR error propagation occurs when speech recognition mistakes (e.g., misrecognizing *'acquitted'* as *'committed'*, or dropping a negation token *'not'*) cascade into downstream summarization, distorting the final summary. We mitigate this through:
1. Domain-specific decoding prompts that reduce ASR substitution errors on statutory terminology.
2. Disabling `condition_on_previous_text` to prevent Whisper hallucination loops.
3. Sentence-level length and density validation in the cleaner to discard gibberish.
4. Preserving verbatim original audio links so every extracted sentence can be immediately verified by the human operator."

---

### Category 4: Extractive Summarization Algorithms & Graph Theory

#### Q10: Walk through the mathematical formulation of Method A: TF-IDF with Position Priors.
**Model Answer:**
"Given a transcript $D = \{S_1, S_2, \dots, S_N\}$, we compute the term frequency-inverse document frequency $\text{TF-IDF}(w, S_i)$ for each word $w \in S_i$. The base sentence score is the mean non-zero weight:
$$\text{BaseScore}(S_i) = \frac{1}{|S_i|} \sum_{w \in S_i} \text{TF-IDF}(w, S_i)$$
To account for judicial proceeding discourse structure, we apply a positional multiplier $P(i)$:
$$P(i) = \begin{cases} 1 + \lambda_{pos} \cdot \left(1 - \frac{i}{0.15N}\right) & \text{if } \frac{i}{N} \le 0.15 \text{ (Opening Charges)} \\ 1 + \lambda_{pos} \cdot \left(\frac{i/N - 0.85}{0.15}\right) & \text{if } \frac{i}{N} \ge 0.85 \text{ (Closing Dispositions)} \\ 1.0 & \text{otherwise} \end{cases}$$
The final score is $\text{Score}(S_i) = \text{BaseScore}(S_i) \times P(i) \times \text{LengthPenalty}(S_i)$."

#### Q11: Explain how Method B (TextRank / LexRank) constructs the affinity graph and calculates PageRank.
**Model Answer:**
"TextRank models the courtroom proceeding as an undirected graph $G = (V, E)$, where each vertex $v_i \in V$ represents a transcript sentence $S_i$. Edge weights $w_{ij}$ represent pairwise lexical similarity (cosine similarity of sentence TF-IDF vectors):
$$w_{ij} = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\| \|\mathbf{v}_j\|}$$
To eliminate noisy spurious connections, edges below threshold $\theta = 0.10$ are set to zero. 
We then compute sentence centrality using the PageRank recurrence:
$$PR(S_i) = \frac{1 - d}{N} + d \sum_{S_j \in \text{Adj}(S_i)} \frac{w_{ji}}{\sum_{S_k \in \text{Adj}(S_j)} w_{jk}} PR(S_j)$$
where $d = 0.85$ is the damping factor. Sentences that share dense semantic overlap with multiple other arguments receive high centrality scores."

#### Q12: How does TextRank prevent repetitive advocate arguments from dominating the summary?
**Model Answer:**
"In courtroom trials, advocates frequently repeat the same core argument across multiple sentences. Standard PageRank would rank all these repetitive sentences highly. To solve this, we implement a greedy redundancy penalty during top-$k$ selection:
$$\text{Score}_{\text{penalized}}(S_i) = PR(S_i) - \mu \cdot \max_{S_j \in \text{Selected}} \text{Sim}(S_i, S_j)$$
where $\mu = 0.30$. Once a sentence covering a legal point is selected, all subsequent sentences with high cosine similarity to it are penalized, forcing the summarizer to diversify across different testimony milestones."

#### Q13: Explain Method C: Multilingual Sentence Embeddings and Maximal Marginal Relevance (MMR).
**Model Answer:**
"Method C embeds each sentence into a dense 384-dimensional semantic space using a multilingual transformer: $\mathbf{e}_i = \text{Embed}(S_i)$. 
We compute the global proceeding centroid:
$$\mathbf{c} = \frac{1}{N} \sum_{i=1}^N \mathbf{e}_i$$
MMR selects sentences iteratively by balancing semantic relevance to the overall trial with semantic diversity from already selected sentences:
$$\text{MMR}(S_i) = \lambda \cdot \cos(\mathbf{e}_i, \mathbf{c}) - (1 - \lambda) \max_{S_j \in \text{Selected}} \cos(\mathbf{e}_i, \mathbf{e}_j)$$
where $\lambda = 0.65$. This ensures the summary comprehensively covers the whole proceeding while eliminating semantic redundancies."

---

### Category 5: Evaluation, Metrics & Ablations

#### Q14: What metrics did you use to evaluate speech recognition accuracy?
**Model Answer:**
"We evaluated ASR using Word Error Rate (WER):
$$\text{WER} = \frac{S + D + I}{N_{\text{ref}}} = \frac{\text{Substitutions} + \text{Deletions} + \text{Insertions}}{\text{Total Reference Words}}$$
In addition to macro WER, we conducted targeted legal entity error analysis, computing separate accuracy on statutory keywords (e.g., *bail*, *Section*, *IPC*, *murder*), numerical quantities (dates, bond amounts, section numbers), and proper nouns."

#### Q15: How do ROUGE-1, ROUGE-2, and ROUGE-L differ, and what do they measure in extractive summarization?
**Model Answer:**
"ROUGE evaluates n-gram overlap between system summaries and human gold standards:
- **ROUGE-1**: Unigram overlap, measuring broad legal topical vocabulary recall.
- **ROUGE-2**: Bigram overlap, measuring phrase-level fluency and preservation of compound legal terms (e.g., *'direct contempt'*, *'first-degree murder'*).
- **ROUGE-L**: Longest Common Subsequence (LCS), measuring structural sentence ordering and consecutive word flow without requiring fixed contiguous n-grams."

#### Q16: Why are automatic metrics like ROUGE insufficient on their own for legal summarization?
**Model Answer:**
"ROUGE evaluates purely lexical surface overlap. A summary could omit a single word—such as the negation token *'not'*—which changes *'defendant was not guilty'* to *'defendant was guilty'*. ROUGE-1 would score this with a 75% overlap, despite being a catastrophic 100% legal failure. 
Therefore, automatic metrics cannot guarantee legal accuracy. We complement ROUGE with exact sentence-level alignment F1, semantic BERTScore, and a structured 4-dimensional human evaluation rubric."

#### Q17: What was the primary finding of your Legal Domain Boost ablation study?
**Model Answer:**
"In our empirical ablation experiments across the gold-standard corpus, toggling the Legal Domain Salience Boost ON increased Sentence-level F1 and ROUGE-L compared to the unassisted baseline. 
Without the domain boost, graph centrality favored repetitive advocate dialogue because advocates repeated claims more often than the judge spoke. Activating statutory cue weights corrected this imbalance, prioritizing the judge's concise, high-salience rulings."

---

### Category 6: System Design, Live Mode & Security

#### Q18: How does the live/streaming simulation work, and what is the latency vs. accuracy trade-off?
**Model Answer:**
"In `live/live_simulator.py`, audio is consumed in sliding buffers of 15 seconds. Each buffer is transcribed via `faster-whisper`, timestamps are adjusted by global offsets, sentences are cleaned, and the running TextRank graph is incrementally updated. 
**The Trade-off**: Shorter windows (e.g., 5s) reduce visual latency to ~1s but result in severed incomplete sentences and higher ASR WER due to lack of acoustic context. Longer windows (20–25s) yield superior transcription accuracy and complete syntactic sentences, but introduce a 20s display lag. Our 15s window represents the Pareto-optimal compromise."

#### Q19: How does the FastAPI asynchronous job architecture handle concurrency and prevent blocking?
**Model Answer:**
"FastAPI runs an asynchronous event loop (`async def`). Heavy CPU-bound tasks (FFmpeg audio extraction, Whisper transcription, PageRank) are dispatched to FastAPI's `BackgroundTasks` worker thread pool. 
When a user uploads a video via `POST /jobs`, the endpoint immediately generates a unique `job_id`, records it as `queued` in the SQLite database, and returns HTTP 202 with a polling URL. The client polls `GET /jobs/{id}` for real-time stage progress without freezing the server."

#### Q20: What privacy and security mechanisms are built into the pipeline?
**Model Answer:**
"Court recordings often contain sensitive judicial data. Our security posture includes:
1. Safe filename sanitization using UUID prefixes and path-traversal prevention.
2. Local ephemeral chunk processing with automated deletion of intermediate audio buffers.
3. Client-side isolated deployments via Docker containers that do not leak telemetry to external third-party cloud APIs.
4. Clear database record management with status tracking in local SQLite."

---

### Category 7: Practical Challenges, Limitations & Future Work

#### Q21: What was the most difficult challenge when handling multilingual court audio from movies and real trials?
**Model Answer:**
"Acoustic heterogeneity and character encoding. Several recordings featured background orchestral score, reverberant courtroom echo (e.g., *Parasakthi* from 1952), and colloquial slang mixed with fast-paced English legal terms (*DJ Tillu*). 
On the systems level, Windows CP1252 default console encoding threw unicode errors on Indic file names, requiring explicit `sys.stdout.reconfigure(encoding='utf-8')` and soundfile float32 array processing instead of fragile string parsing."

#### Q22: What happens if Whisper transcribes speech in a regional language but makes grammatical errors—how does that affect the summary?
**Model Answer:**
"Because our summarization is strictly extractive, it extracts the exact sentences transcribed by ASR. If ASR misrecognizes a phoneme, that typographical error appears in the summary. However, because our summarizers operate on TF-IDF or multilingual sentence embeddings, semantic centrality is largely resilient to isolated single-word spelling errors. Most importantly, because our system embeds direct timestamp links to the exact second in the video, the user can verify the audio with a single click."

#### Q23: Why sort extracted summary sentences in chronological order rather than importance order?
**Model Answer:**
"Trial proceedings follow strict chronological legal logic: preliminary motions $\rightarrow$ prosecution charges $\rightarrow$ defense cross-examination $\rightarrow$ witness admissions $\rightarrow$ judicial verdict. 
Presenting sentences ranked solely by score would scramble cause and effect (e.g., showing the verdict before the witness confession). Sorting the selected top-$k$ sentences chronologically preserves narrative and procedural coherence."

#### Q24: How would you scale this architecture to a multi-court judicial enterprise with thousands of daily hearings?
**Model Answer:**
"To scale to enterprise production:
1. Decouple ingestion and inference using a message queue (RabbitMQ / Apache Kafka) and worker pool (Celery / Ray).
2. Deploy faster-whisper instances on GPU worker nodes (NVIDIA T4 / A10) with dynamic batching.
3. Migrate the SQLite job store to PostgreSQL with Redis for caching.
4. Store transcripts and extracted audio in S3-compatible object storage (MinIO / AWS S3) with lifecycle auto-expiration policies."

#### Q25: If you had 6 more months, what feature would you add to this project?
**Model Answer:**
"I would implement neural speaker diarization (using PyAnnote.audio) to automatically label speakers as `[JUDGE]`, `[PROSECUTOR]`, `[DEFENSE]`, and `[WITNESS]` directly from acoustic embeddings, combined with a legal LLM acting solely as a factual consistency auditor to cross-check extractive summary coherence without generating text."
