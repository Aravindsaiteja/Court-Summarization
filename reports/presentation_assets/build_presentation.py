"""
Complete Professional PowerPoint Presentation Generator for Court Proceeding Summarizer.
Produces a 16:9 widescreen, visually rich PPTX with embedded graphics, dark theme cards,
and exhaustive slide-by-slide speaker notes.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_PPTX = "reports/Court_Proceeding_Summarization_Review.pptx"
ASSETS_DIR = "reports/presentation_assets"

# Color Palette Constants
BG_COLOR = RGBColor(15, 23, 42)        # Slate 900 #0F172A
CARD_BG = RGBColor(30, 41, 59)         # Slate 800 #1E293B
CARD_BORDER = RGBColor(51, 65, 85)     # Slate 700 #334155
BLUE_ACCENT = RGBColor(56, 189, 248)   # Sky 400 #38BDF8
GOLD_ACCENT = RGBColor(245, 158, 11)   # Amber 500 #F59E0B
GREEN_ACCENT = RGBColor(16, 185, 129)  # Emerald 500 #10B981
RED_ACCENT = RGBColor(239, 68, 68)     # Red 500 #EF4444
PURPLE_ACCENT = RGBColor(168, 85, 247) # Purple 500 #A855F7
TEXT_WHITE = RGBColor(255, 255, 255)
TEXT_MUTED = RGBColor(148, 163, 184)   # Slate 400
TEXT_LIGHT = RGBColor(226, 232, 240)   # Slate 200

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, category_text, title_text, subtitle_text=""):
        # Category Badge
        cat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(3.2), Inches(0.35))
        cat_box.fill.solid()
        cat_box.fill.fore_color.rgb = CARD_BG
        cat_box.line.color.rgb = BLUE_ACCENT
        cat_box.line.width = Pt(1.2)
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = f"• {category_text.upper()} •"
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = BLUE_ACCENT
        p_cat.alignment = PP_ALIGN.CENTER

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

        # Subtitle
        if subtitle_text:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(11.7), Inches(0.35))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle_text
            p_sub.font.size = Pt(11.5)
            p_sub.font.italic = True
            p_sub.font.color.rgb = GOLD_ACCENT

    def add_card(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    def add_speaker_notes(slide, timing, goal, script, viva_tip):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = f"⏱ [SUGGESTED TIME: {timing}]\n"
        tf.text += f"🎯 [SLIDE OBJECTIVE]: {goal}\n\n"
        tf.text += f"🗣️ [WHAT TO SAY OUT LOUD - VERBATIM SCRIPT]:\n\"{script}\"\n\n"
        tf.text += f"💡 [PROFESSOR / VIVA TIP & DEFENSE]:\n{viva_tip}"

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Accent decorative bar on top
    dec_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(2.5), Inches(0.08))
    dec_bar.fill.solid()
    dec_bar.fill.fore_color.rgb = GOLD_ACCENT
    dec_bar.line.fill.background()

    # Domain Tag
    t_tag = s1.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.5), Inches(0.4))
    p = t_tag.text_frame.paragraphs[0]
    p.text = "ACADEMIC CAPSTONE PROJECT • SPEECH AND LANGUAGE PROCESSING"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    # Main Project Title
    t_main = s1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.0))
    tf = t_main.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "Real-Time Multilingual Court Proceeding Summarization System"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p2 = tf.add_paragraph()
    p2.text = "Speech Recognition & Strictly Extractive Summarization with Temporal Anchoring"
    p2.font.size = Pt(18)
    p2.font.bold = True
    p2.font.color.rgb = GOLD_ACCENT

    # Project highlights pill row
    pills = ["Strictly Extractive (Zero Hallucination)", "Allegation vs Ruling Separation", "Microsecond Video Anchors", "Multilingual: EN, HI, TE, TA"]
    for i, pill in enumerate(pills):
        p_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 2.9), Inches(3.6), Inches(2.75), Inches(0.45))
        p_box.fill.solid()
        p_box.fill.fore_color.rgb = CARD_BG
        p_box.line.color.rgb = GREEN_ACCENT if i == 0 else (RED_ACCENT if i == 1 else BLUE_ACCENT)
        p_box.line.width = Pt(1.2)
        ptf = p_box.text_frame
        ptf.word_wrap = True
        pp = ptf.paragraphs[0]
        pp.text = pill
        pp.font.size = Pt(9.5)
        pp.font.bold = True
        pp.font.color.rgb = TEXT_LIGHT
        pp.alignment = PP_ALIGN.CENTER

    # Presenter Information Card
    info_card = add_card(s1, 0.8, 4.4, 11.7, 2.3, border_color=CARD_BORDER)
    tf_info = info_card.text_frame
    tf_info.margin_left = Inches(0.4)
    tf_info.margin_top = Inches(0.3)
    
    p = tf_info.paragraphs[0]
    p.text = "ACADEMIC DEFENSE & PROJECT REVIEW"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    p = tf_info.add_paragraph()
    p.text = "• Candidate / Presenter: Final Year Capstone Project Researcher"
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_WHITE

    p = tf_info.add_paragraph()
    p.text = "• Domain: Judicial NLP, Multilingual Speech Processing & Assistive Systems"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_LIGHT

    p = tf_info.add_paragraph()
    p.text = "• Core Stack: faster-whisper (CTranslate2 INT8) | TextRank & MMR | FastAPI | Streamlit | EBU R128"
    p.font.size = Pt(11)
    p.font.color.rgb = GOLD_ACCENT

    p = tf_info.add_paragraph()
    p.text = "• Key Performance: Real-Time Factor (RTF) = 0.049 on CPU (20x faster than real-time playback)"
    p.font.size = Pt(11)
    p.font.color.rgb = GREEN_ACCENT

    add_speaker_notes(s1, 
        timing="45 Seconds",
        goal="Set a commanding, professional tone. Introduce the project title, the high-stakes legal domain, and the core technological paradigm.",
        script="Respected members of the review panel, good morning. Today I am presenting my capstone project titled: 'Real-Time Multilingual Court Proceeding Summarization System Using Speech Recognition and Strictly Extractive Summarization'. Court proceedings across multilingual jurisdictions generate thousands of hours of audio and video that are dense, rapid, and code-switched. Our goal is to create an end-to-end assistive pipeline that automatically transcribes judicial recordings, separates advocate allegations from binding judicial rulings, and generates microsecond-anchored extractive summaries with zero hallucination. Over the next few minutes, I will walk you through the problem statement, system architecture, core algorithms, empirical evaluation, and live demonstration.",
        viva_tip="Memorize the four core pillars immediately: 1. Strictly extractive (zero hallucination); 2. Segregation of allegations vs rulings; 3. Temporal traceability to source audio; 4. Mandatory assistive review disclaimer.")

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & REAL-WORLD BOTTLENECK
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Problem Statement", "Judicial Problem Statement & Real-World Operational Bottlenecks", 
               "Why automated courtroom summarization is an urgent necessity in modern digital justice")

    cards_s2 = [
        ("1. Data Volume Explosion", 
         ["Supreme Courts & High Courts record hundreds of hours daily.",
          "Contested hearings easily span 3 to 6 hours per trial.",
          "Video recordings are unstructured: no search, index, or chapter markers."],
         RED_ACCENT, 0.8, 2.0, 3.6, 4.8),
        ("2. Operational Human Bottleneck",
         ["Law clerks and advocates spend hours scrubbing videos manually.",
          "High human transcription turnaround time (24–72 hours).",
          "Risk of missing crucial cross-examination contradictions or bail conditions."],
         GOLD_ACCENT, 4.85, 2.0, 3.6, 4.8),
        ("3. Multilingual & Acoustic Realities",
         ["Judicial proceedings feature heavy code-switching (e.g. Hindi/Telugu with English citations).",
          "Ambient acoustics: echoey halls, gavel strikes, and distant witness speech.",
          "Existing generic tools fail completely on regional legal dialects."],
         BLUE_ACCENT, 8.9, 2.0, 3.6, 4.8)
    ]

    for title, bullets, col, left, top, width, height in cards_s2:
        c = add_card(s2, left, top, width, height, border_color=col)
        tf = c.text_frame
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = TEXT_LIGHT
            pb.space_before = Pt(12)

    add_speaker_notes(s2,
        timing="60 Seconds",
        goal="Explain why this problem matters in the real world and why human transcription alone is failing.",
        script="Let us examine the operational crisis in modern courtrooms. With digital court initiatives globally, tribunals now record hundreds of hours of proceedings daily. However, reviewing a single contested 3-hour hearing requires a law clerk or junior advocate to spend 4 to 6 hours scrubbing unstructured footage back and forth. Crucial moments—such as a forensic contradiction during cross-examination, or an operative bail order—are buried within massive audio streams. Furthermore, in multilingual jurisdictions like India, counsel and witnesses constantly alternate between vernacular languages like Telugu, Tamil, or Hindi and English statutory terms like 'Section 211 IPC'. Manual transcription is slow, expensive, and error-prone. This creates an urgent need for an automated, highly reliable assistive pipeline.",
        viva_tip="Emphasize that court audio is unstructured sequential data—unlike text documents, you cannot use 'Ctrl+F' on a raw video file without timestamped speech recognition.")

    # =========================================================================
    # SLIDE 3: RESEARCH GAP - WHY NOT GENERATIVE LLMs?
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Research Gap", "The Critical Research Gap: Why NOT Generative LLMs?", 
               "Examining the catastrophic failure modes of abstractive generative AI in judicial contexts")

    # Left Column: The 3 Fatal Flaws of Abstractive LLMs
    c_flaw = add_card(s3, 0.8, 2.0, 5.7, 4.8, border_color=RED_ACCENT)
    tf = c_flaw.text_frame
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "FATAL FLAWS OF GENERATIVE LLMs (e.g. GPT-4, Llama 3)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RED_ACCENT

    flaws = [
        ("1. Hallucinatory Synthesis", "Generative LLMs invent plausible-sounding details or invert legal meaning by substituting inexact legal synonyms."),
        ("2. Catastrophic Claim Conflation", "An advocate's unproven allegation (e.g., 'The accused committed fraud') is routinely summarized as a confirmed court finding."),
        ("3. Loss of Evidentiary Traceability", "Synthesized text has no 1-to-1 anchor to the audio. A judge cannot verify the original tone, hesitation, or exact spoken words without re-listening.")
    ]
    for h, desc in flaws:
        p_h = tf.add_paragraph()
        p_h.text = f"❌ {h}"
        p_h.font.size = Pt(11.5)
        p_h.font.bold = True
        p_h.font.color.rgb = TEXT_WHITE
        p_h.space_before = Pt(10)
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_LIGHT

    # Right Column: The Proposed Strictly Extractive Paradigm
    c_sol = add_card(s3, 6.8, 2.0, 5.7, 4.8, border_color=GREEN_ACCENT)
    tf = c_sol.text_frame
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "OUR STRICTLY EXTRACTIVE PARADIGM"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT

    solutions = [
        ("1. Zero Hallucination Guarantee", "The summary consists 100% of verbatim transcript sentences. The model never invents, paraphrases, or merges words."),
        ("2. Explicit Provenance Tagging", "Advocate submissions receive an allegation tag ([ADVOCATE_ALLEGATION]), strictly separated from binding orders ([JUDICIAL_RULING])."),
        ("3. Microsecond Temporal Hyperlinks", "Every single sentence links directly to its [start_time, end_time], allowing instant one-click video audio playback verification.")
    ]
    for h, desc in solutions:
        p_h = tf.add_paragraph()
        p_h.text = f"✅ {h}"
        p_h.font.size = Pt(11.5)
        p_h.font.bold = True
        p_h.font.color.rgb = TEXT_WHITE
        p_h.space_before = Pt(10)
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s3,
        timing="60 Seconds",
        goal="Win over the evaluators on your fundamental design decision: why you chose extractive NLP instead of an abstractive LLM like ChatGPT.",
        script="A central question the panel might ask is: 'Why not simply feed the transcript into GPT-4 or Llama 3 for an abstractive summary?' In consumer applications, abstractive generation is popular. But in the judicial domain, linguistic fidelity is non-negotiable. Generative LLMs have three fatal failure modes: First, hallucinatory synthesis—modifying a conditional phrase can completely invert legal culpability. Second, and most dangerous, claim conflation: an advocate's unproven allegation is frequently summarized as an established court fact! Third, loss of evidentiary traceability: synthesized text cannot be linked back to the exact audio second. Our solution is strictly extractive: we select verbatim transcript sentences with microsecond temporal anchors, guaranteeing zero hallucination and immediate auditability.",
        viva_tip="If asked: 'Aren't extractive summaries less fluent than LLMs?' Answer: 'In court proceedings, legal accuracy and auditability supersede creative fluency. A fluent hallucination is a catastrophic legal liability; an exact verbatim excerpt with a clickable timestamp is legally admissible and verifiable.'")

    # =========================================================================
    # SLIDE 4: CORE DESIGN PRINCIPLES & SAFETY MANDATES
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "System Design", "Core Design Principles & Safety Mandates", 
               "The four non-negotiable architectural pillars governing the entire summarization pipeline")

    pillars = [
        ("Pillar 1: Strictly Extractive", 
         "Verbatim Sentence Selection", 
         "The system selects complete, real transcript sentences and NEVER invents, paraphrases, or hallucinates text. Preserves original grammar and statutory citations.",
         BLUE_ACCENT, 0.8, 2.0),
        ("Pillar 2: Allegation Segregation", 
         "Discursive Role Classification", 
         "Statements by advocates are tagged [ADVOCATE_ALLEGATION] and penalized, while authoritative bench orders are tagged [JUDICIAL_RULING] and boosted 2.5x.",
         RED_ACCENT, 3.8, 2.0),
        ("Pillar 3: Temporal Traceability", 
         "Microsecond Audio/Video Anchors", 
         "Every summary sentence is permanently anchored to its exact [start_time, end_time] timestamp, enabling instant video scrubbing and verification.",
         GREEN_ACCENT, 6.8, 2.0),
        ("Pillar 4: Assistive Disclaimer", 
         "Mandatory Human-in-the-Loop", 
         "The system functions strictly as a research and review aid; human verification against official records remains legally mandatory. Prominently badged on UI & PDF.",
         GOLD_ACCENT, 9.8, 2.0)
    ]

    for title, subtitle, desc, col, left, top in pillars:
        c = add_card(s4, left, top, 2.7, 4.8, border_color=col)
        tf = c.text_frame
        tf.margin_left = tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.3)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(10)
        p_sub.font.italic = True
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_before = Pt(4)

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(10.5)
        p_desc.font.color.rgb = TEXT_LIGHT
        p_desc.space_before = Pt(16)

    add_speaker_notes(s4,
        timing="45 Seconds",
        goal="Present the four core pillars clearly and show that safety and legal ethics were built into the architecture from day one.",
        script="To enforce legal integrity, we engineered our system around four non-negotiable architectural pillars: Pillar 1 is Strictly Extractive Verbatim Selection: we select genuine sentences from the speech stream without modifying words. Pillar 2 is Allegation Segregation: we actively distinguish between advocate arguments and judicial rulings using domain cue weights. Pillar 3 is Microsecond Temporal Traceability: every statement has a global start and end timestamp in seconds for instant evidentiary verification. And Pillar 4 is our Mandatory Assistive Disclaimer: the system is designed as an assistive research tool that keeps human legal professionals in the loop.",
        viva_tip="Point out that Pillar 2 and Pillar 3 are direct technical mitigations against the standard pitfalls of generative AI.")

    # =========================================================================
    # SLIDE 5: END-TO-END SYSTEM ARCHITECTURE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Architecture", "End-to-End System Pipeline Architecture", 
               "Comprehensive 6-stage pipeline from multimedia ingestion to synchronized report delivery")

    # Insert Architecture Diagram Asset
    arch_path = os.path.join(ASSETS_DIR, "architecture_diagram.png")
    if os.path.exists(arch_path):
        s5.shapes.add_picture(arch_path, Inches(0.8), Inches(1.9), width=Inches(11.7), height=Inches(5.0))

    add_speaker_notes(s5,
        timing="75 Seconds",
        goal="Walk the panel through the complete engineering pipeline from left to right.",
        script="This slide illustrates our end-to-end system architecture, composed of six modular stages: Stage 1 is the Acoustic Front-End: raw courtroom video is demuxed via FFmpeg to 16 kHz mono WAV, normalized to -23 LUFS integrated loudness via EBU R128, filtered between 80 Hz and 7.5 kHz, and segmented using conservative Voice Activity Detection. Stage 2 is Multilingual ASR: utilizing faster-whisper powered by CTranslate2 with INT8 quantization, automated language identification, and legal domain prompt conditioning. Stage 3 is Legal Preprocessing: disfluency cleaning with strict negation preservation, abbreviation-protected sentence splitting, and proportional timestamp interpolation. Stage 4 is the Extractive Summarization Engine: implementing three benchmarked algorithms—TF-IDF with position priors, TextRank graph centrality, and Multilingual MiniLM with MMR. Stage 5 is Domain Salience Boosting: statutory cue weighting and allegation filtering. And Stage 6 is Multi-Channel Delivery: asynchronous FastAPI backend, SQLite state queue, and interactive Streamlit UI with synchronized video playback.",
        viva_tip="Highlight modularity: each stage communicates via typed Pydantic models, allowing any ASR or summarization model to be swapped or upgraded without breaking downstream components.")

    # =========================================================================
    # SLIDE 6: ACOUSTIC INGESTION & LOUDNESS NORMALIZATION
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Audio Engineering", "Acoustic Engineering & Loudness Normalization", 
               "Solving acoustic variance, gavel spikes, and quiet witness testimonies via EBU R128")

    # Left Column: Technical Explanations
    c_ac = add_card(s6, 0.8, 1.9, 4.8, 5.0, border_color=BLUE_ACCENT)
    tf = c_ac.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "ACOUSTIC STANDARDIZATION & VAD"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    points_ac = [
        ("Standardized 16 kHz Mono WAV", "Nyquist bandwidth of 8 kHz captures all human vocal formants while halving memory consumption over 48 kHz stereo."),
        ("Why Peak Normalization Fails", "A single loud gavel strike reaches 0 dBFS peak, leaving quiet witness testimony buried in background noise."),
        ("EBU R128 (-23 LUFS) Norm", "Psychoacoustic K-weighting balances integrated loudness over time, amplifying quiet witnesses while taming loud judges."),
        ("Conservative VAD & 200ms Margin", "Bandpass (80Hz - 7.5kHz) cuts HVAC rumble. VAD (-35dB threshold) adds 200ms padding so quiet answers ('no', 'guilty') are never clipped.")
    ]
    for h, desc in points_ac:
        ph = tf.add_paragraph()
        ph.text = f"• {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = GOLD_ACCENT
        ph.space_before = Pt(8)
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_LIGHT

    # Right Column: Insert Waveform Diagram
    wave_path = os.path.join(ASSETS_DIR, "audio_processing_waveform.png")
    if os.path.exists(wave_path):
        s6.shapes.add_picture(wave_path, Inches(5.8), Inches(1.9), width=Inches(6.7), height=Inches(5.0))

    add_speaker_notes(s6,
        timing="60 Seconds",
        goal="Explain why audio preprocessing is critical for ASR accuracy in courtrooms, specifically contrasting peak normalization with EBU R128.",
        script="In courtroom recordings, audio quality varies drastically between amplified judges and soft-spoken witnesses. In traditional peak normalization, if a judge strikes the gavel or someone hits the desk, that momentary spike hits 0 dBFS. Peak normalization scales the entire audio by that peak, leaving quiet witness testimony completely inaudible to the speech recognizer. We solve this by implementing EBU R128 psychoacoustic loudness normalization targeting -23 LUFS. As seen in the right figure, EBU R128 uses K-weighted frequency filters to amplify speech formants while maintaining a -1.5 dBFS True Peak ceiling. Furthermore, our Voice Activity Detection operates conservatively at -35 dB with 200ms safety padding margins, guaranteeing that quiet monosyllabic witness answers like 'no' or 'guilty' are never accidentally truncated.",
        viva_tip="Formula for EBU R128: L_K = -0.691 + 10 log10 (1/T integral z(t)^2 dt). Emphasize K-weighting curves model human ear sensitivity (boosting formants around 2-4 kHz).")

    # =========================================================================
    # SLIDE 7: MULTILINGUAL ASR & CTRANSLATE2 OPTIMIZATION
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Speech Recognition", "Multilingual ASR & CTranslate2 INT8 Optimization", 
               "Achieving 20x real-time inference speed on commodity CPU hardware with domain conditioning")

    cards_asr = [
        ("CTranslate2 & INT8 Speedup",
         ["Standard PyTorch Whisper on CPU yields RTF ~ 0.8 - 1.2 (very slow).",
          "We use faster-whisper with CTranslate2 C++ inference.",
          "Applies INT8 weight quantization and fused matrix multiplications.",
          "Result: Real-Time Factor (RTF) of 0.049 on CPU (processes 1 min of audio in under 3 seconds!)."],
         BLUE_ACCENT, 0.8, 2.0, 3.6, 4.8),
        ("Automatic Language ID (LID)",
         ["Automatic language identification over first 30 seconds of audio.",
          "Outputs softmax confidence score (e.g., Telugu: 96.5%, English: 99.2%).",
          "Supports multilingual courtroom cases across English, Hindi, Telugu, and Tamil.",
          "Decoupled language token feeding enables bilingual translation tracks."],
         GREEN_ACCENT, 4.85, 2.0, 3.6, 4.8),
        ("Domain-Conditioned Decoding",
         ["Court speech code-switches into technical statutory terms (IPC, CrPC, Section 211).",
          "ASR initialized with legal domain initial_prompt.",
          "Biases decoder autoregressive priors toward statutory vocabulary.",
          "condition_on_previous_text=False eliminates infinite looping on background echo."],
         GOLD_ACCENT, 8.9, 2.0, 3.6, 4.8)
    ]

    for title, bullets, col, left, top, width, height in cards_asr:
        c = add_card(s7, left, top, width, height, border_color=col)
        tf = c.text_frame
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(10.5)
            pb.font.color.rgb = TEXT_LIGHT
            pb.space_before = Pt(8)

    add_speaker_notes(s7,
        timing="60 Seconds",
        goal="Highlight the engineering optimization: faster-whisper, INT8 quantization, RTF of 0.049, and legal prompt conditioning.",
        script="For speech recognition, standard PyTorch Whisper on CPU is too slow for real-time applications, with a Real-Time Factor around 1.0. We implemented faster-whisper backed by the CTranslate2 C++ inference engine with INT8 quantization. This reduced our Real-Time Factor to 0.049—meaning our system transcribes court audio 20 times faster than real-time playback on a standard CPU without needing an expensive GPU. To handle code-switching and Indian statutory terms—such as 'Section 211 IPC' or 'anticipatory bail'—we condition Whisper's decoder with a legal domain prompt. Furthermore, disabling 'condition_on_previous_text' eliminates the infamous Whisper hallucination loop when dealing with courtroom reverberation.",
        viva_tip="Definition of RTF: Real-Time Factor = Processing Time / Audio Duration. RTF = 0.049 means 100 seconds of court audio is transcribed in only 4.9 seconds!")

    # =========================================================================
    # SLIDE 8: TRANSCRIPT CLEANING & SENTENCE SEGMENTATION
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Text Processing", "Transcript Cleaning & Legal Sentence Segmentation", 
               "Preserving legal semantic truth, protecting negation tokens, and interpolating timestamps")

    # Left Card: Cleaning & Negation Guard
    c_cl = add_card(s8, 0.8, 2.0, 5.7, 4.8, border_color=GOLD_ACCENT)
    tf = c_cl.text_frame
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "DISFLUENCY CLEANING & NEGATION LOCK"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    cl_items = [
        ("Filler Removal", "Removes hesitations ('um', 'uh', 'ah') and stutter repetitions ('the the witness') without modifying vocabulary."),
        ("Strict Negation Preservation", "Negation words ('not', 'never', 'nahi', 'kaadu', 'illai') are hard-locked. Stripping or altering a negation would invert legal guilt!"),
        ("Numerical & Date Verbatim Lock", "Monetary sums, dates, and statute numbers are preserved verbatim with zero roundoff or formatting alterations."),
        ("Persistent Audit Log", "Every cleaning transformation is recorded with character offsets in an audit log for judicial verification.")
    ]
    for h, desc in cl_items:
        ph = tf.add_paragraph()
        ph.text = f"• {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = TEXT_WHITE
        ph.space_before = Pt(8)
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_LIGHT

    # Right Card: Abbreviation Boundary Splitter
    c_sg = add_card(s8, 6.8, 2.0, 5.7, 4.8, border_color=BLUE_ACCENT)
    tf = c_sg.text_frame
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "ABBREVIATION PROTECTION & TIMESTAMPS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    sg_items = [
        ("The Period (.) Problem", "Standard splitters treat every period as a sentence end. In legal text, this shreds citations like 'State v. Kumar' or 'Sec. 302 IPC' into meaningless fragments!"),
        ("Protected Legal Lexicon", "Regex-protected honorifics ('Hon.', 'Dr.') and legal citations ('v.', 'vs.', 'Sec.', 'Art.', 'No.', 'CrPC', 'IPC') are preserved."),
        ("Multi-Script Terminal Split", "Splits on genuine terminal punctuation: English ('.', '!', '?') and Indic danda ('।')."),
        ("Proportional Timestamp Interpolation", "Calculates character-length proportional start and end timestamps across segment splits, maintaining microsecond synchronization.")
    ]
    for h, desc in sg_items:
        ph = tf.add_paragraph()
        ph.text = f"• {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = TEXT_WHITE
        ph.space_before = Pt(8)
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s8,
        timing="50 Seconds",
        goal="Explain the legal nuances of text preprocessing: why standard NLP splitters break legal text and how you protected negations.",
        script="Transcript preprocessing in law requires strict semantic invariants. First, speech disfluency cleaners remove fillers like 'um' and 'uh', but we enforce a hard Negation Lock. Negation words like 'not', 'never', 'nahi', or 'kaadu' can never be removed or simplified, because dropping a single negation inverts legal liability from 'not guilty' to 'guilty'. Second, standard sentence segmentation tools treat every period as an end of sentence. In legal discourse, that disastrously fragments citations like 'Sec. 211 IPC' or 'State v. Arjun'. We engineered an abbreviation-aware boundary segmenter that protects statutory tokens, splits only on true terminal punctuation, and mathematically interpolates character-proportional timestamps for each resulting sentence.",
        viva_tip="Timestamp interpolation formula: t_start(S_i) = t_seg_start + (sum length preceding sentences / total seg length) * seg_duration.")

    # =========================================================================
    # SLIDE 9: THREE EXTRACTIVE SUMMARIZATION METHODOLOGIES
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Algorithms", "Three Extractive Summarization Methodologies", 
               "Rigorous comparison of Frequency-based, Graph-theoretic, and Semantic Vector approaches")

    cards_algo = [
        ("Method A: TF-IDF + Position",
         ["Frequency-Based Baseline",
          "Computes mean non-zero TF-IDF weight across constituent tokens.",
          "Discourse Position Prior P(i): boosts opening 15% (charges framed) and closing 15% (judicial dispositions).",
          "Applies length penalty to discard short utterances (<4 words) and run-on monologues (>50 words)."],
         BLUE_ACCENT, 0.8, 2.0, 3.6, 4.8),
        ("Method B: TextRank Graph [TOP]",
         ["Graph Centrality (LexRank)",
          "Constructs sentence affinity graph G=(V,E) where edge weights w_ij = cosine similarity of TF-IDF vectors.",
          "PageRank iteration (d=0.85) calculates eigenvector sentence centrality.",
          "Greedy Redundancy Suppression (μ=0.30) prevents repetitive advocate claims from saturating summary."],
         GREEN_ACCENT, 4.85, 2.0, 3.6, 4.8),
        ("Method C: Multilingual MiniLM MMR",
         ["Semantic Vector Embeddings",
          "Maps sentences into 384-dimensional vectors via paraphrase-multilingual-MiniLM-L12-v2.",
          "Computes proceeding centroid vector c.",
          "Maximal Marginal Relevance (MMR with λ=0.65) balances relevance to whole trial and diversity from selected sentences."],
         GOLD_ACCENT, 8.9, 2.0, 3.6, 4.8)
    ]

    for title, bullets, col, left, top, width, height in cards_algo:
        c = add_card(s9, left, top, width, height, border_color=col)
        tf = c.text_frame
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        for idx, b in enumerate(bullets):
            pb = tf.add_paragraph()
            pb.text = f"• {b}" if idx > 0 else f"[{b}]"
            pb.font.size = Pt(11) if idx == 0 else Pt(10)
            pb.font.bold = True if idx == 0 else False
            pb.font.color.rgb = GOLD_ACCENT if idx == 0 else TEXT_LIGHT
            pb.space_before = Pt(6) if idx > 0 else Pt(2)

    add_speaker_notes(s9,
        timing="75 Seconds",
        goal="Break down the math and logic of the three extractive algorithms, emphasizing why TextRank outperformed embeddings.",
        script="To find the optimal extractive mechanism, we benchmarked three distinct mathematical paradigms: Method A is TF-IDF with Judicial Position Priors. In legal proceedings, opening statements frame charges and closing statements contain rulings. We apply a positional multiplier P(i) boosting the first and last 15% of the trial. Method B is TextRank Graph Centrality: we construct an undirected affinity graph where sentences are nodes and edges represent pairwise cosine similarity. PageRank with damping factor d=0.85 computes centrality. Crucially, we add a greedy redundancy penalty mu=0.30 so repetitive advocate assertions don't crowd out diverse testimony. Method C uses 384-dimensional multilingual MiniLM sentence embeddings with Maximal Marginal Relevance (MMR, lambda=0.65) to maximize semantic coverage while penalizing similarity to already-selected points. Regardless of the algorithm, all selected sentences are re-sorted chronologically.",
        viva_tip="Why did TextRank outperform MMR? Because courtroom cross-examinations exhibit dense keyword-sharing between opposing counsel and witnesses. Graph centrality directly captures these lexical intersections.")

    # =========================================================================
    # SLIDE 10: LEGAL DOMAIN ENHANCER & ALLEGATION FILTER
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Domain Rules", "Legal Domain Salience Booster & Allegation Segregation", 
               "Integrating statutory cue weighting and formal segregation of advocate claims vs court orders")

    # Left: Lexicon Tiers
    c_lex = add_card(s10, 0.8, 2.0, 5.7, 4.8, border_color=GOLD_ACCENT)
    tf = c_lex.text_frame
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "MULTILINGUAL LEGAL LEXICON WEIGHTS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    tiers = [
        ("Judicial Dispositions (2.5x Multiplier)", "Triggers: 'held', 'ruled', 'court orders', 'bail granted', 'acquitted', 'convicted', 'faisla', 'teerpu'."),
        ("Evidentiary Testimony (1.8x Multiplier)", "Triggers: 'witness testifies', 'exhibit', 'forensic report', 'tire marks', 'confession', 'saboot', 'saakshyam'."),
        ("Statutory Codes (1.6x Multiplier)", "Triggers: 'Section', 'IPC', 'CrPC', 'Article', 'charge sheet', 'dhara'."),
        ("Advocate Allegations (0.85x Multiplier)", "Triggers: 'prosecution claims', 'defense argues', 'alleges', 'accused contends'. Receives penalty and allegation badge.")
    ]
    for h, desc in tiers:
        ph = tf.add_paragraph()
        ph.text = f"• {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = TEXT_WHITE
        ph.space_before = Pt(8)
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_LIGHT

    # Right: Real Output Case Examples
    c_ex = add_card(s10, 6.8, 2.0, 5.7, 4.8, border_color=GREEN_ACCENT)
    tf = c_ex.text_frame
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "REAL SYSTEM OUTPUT EXAMPLES"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT

    p_badge1 = tf.add_paragraph()
    p_badge1.text = "1. [JUDICIAL_RULING] • Salience: 20.87 (Boosted 2.5x)"
    p_badge1.font.size = Pt(11)
    p_badge1.font.bold = True
    p_badge1.font.color.rgb = GREEN_ACCENT
    p_badge1.space_before = Pt(10)

    p_body1 = tf.add_paragraph()
    p_body1.text = "\"The Court hereby orders a departmental and criminal inquiry under Section 211 against the investigating officers found guilty.\" (CASE_TE_02, Naandhi)"
    p_body1.font.size = Pt(10)
    p_body1.font.italic = True
    p_body1.font.color.rgb = TEXT_LIGHT

    p_badge2 = tf.add_paragraph()
    p_badge2.text = "2. [ADVOCATE_ALLEGATION] • Salience: 0.041 (Penalized 0.85x)"
    p_badge2.font.size = Pt(11)
    p_badge2.font.bold = True
    p_badge2.font.color.rgb = GOLD_ACCENT
    p_badge2.space_before = Pt(14)

    p_body2 = tf.add_paragraph()
    p_body2.text = "\"Counsel submits that the evidence was fabricated by the prosecution to falsely implicate the petitioner.\" (CASE_HI_01, Criminal Justice)"
    p_body2.font.size = Pt(10)
    p_body2.font.italic = True
    p_body2.font.color.rgb = TEXT_LIGHT

    p_badge3 = tf.add_paragraph()
    p_badge3.text = "3. Temporal Anchor Verification"
    p_badge3.font.size = Pt(11)
    p_badge3.font.bold = True
    p_badge3.font.color.rgb = BLUE_ACCENT
    p_badge3.space_before = Pt(14)

    p_body3 = tf.add_paragraph()
    p_body3.text = "Every excerpt links directly to [start_time, end_time]. Clicking the timestamp scrubs the synchronized video player to the exact evidentiary moment."
    p_body3.font.size = Pt(10)
    p_body3.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s10,
        timing="60 Seconds",
        goal="Show how the legal enhancer ensures advocate submissions cannot masquerade as judicial orders.",
        script="A key innovation of our work is the Legal Domain Salience Booster in src/summarization/legal_enhancer.py. We constructed a curated multilingual legal lexicon across English, Hindi, Telugu, and Tamil. We classify legal utterances into four tiers: First, definitive Judicial Dispositions receive a 2.5x salience boost. Second, Evidentiary Testimony receives a 1.8x boost. Third, Statutory Codes receive a 1.6x boost. And fourth, Advocate Allegations receive a 0.85x penalty. Furthermore, as shown on the right, our pipeline badges each sentence: authoritative court orders are tagged [JUDICIAL_RULING] in green, while advocate submissions are tagged [ADVOCATE_ALLEGATION] in amber. This ensures complete transparency and prevents legal misinterpretation.",
        viva_tip="Point out that the multilingual triggers cover vernacular terms like 'faisla' in Hindi, 'teerpu' in Telugu, and 'theerppu' in Tamil.")

    # =========================================================================
    # SLIDE 11: MULTILINGUAL DATASET & CORPUS INVENTORY
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Corpus & Data", "Multilingual Dataset & Procedural Inventory", 
               "Curated benchmark corpus across 10 courtroom proceedings, 4 languages, and 42+ minutes")

    # Table of Dataset
    table_shape = s11.shapes.add_table(11, 6, Inches(0.8), Inches(1.9), Inches(11.7), Inches(5.0))
    table = table_shape.table
    table.columns[0].width = Inches(1.3)
    table.columns[1].width = Inches(2.8)
    table.columns[2].width = Inches(1.5)
    table.columns[3].width = Inches(1.2)
    table.columns[4].width = Inches(3.4)
    table.columns[5].width = Inches(1.5)

    headers = ["Case ID", "Source Title", "Language", "Duration", "Acoustic Quality & Procedural Type", "Split"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 58, 138) # Dark blue
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.alignment = PP_ALIGN.CENTER

    dataset_rows = [
        ("CASE_EN_01", "My Cousin Vinny (1992)", "English (EN)", "154.0s", "Studio clean; automotive forensic cross-examination", "Dev"),
        ("CASE_TE_01", "Friendship (2022)", "Telugu (TE)", "309.1s", "Dynamic score; student trial & fast dialogue", "Test"),
        ("CASE_EN_02", "Law Abiding Citizen (2009)", "English (EN)", "180.5s", "Studio speech; bail revocation & contempt ruling", "Dev"),
        ("CASE_TA_01", "Parasakthi Classic (1952)", "Tamil (TA)", "299.0s", "Historical mono; classic Dravidian rhetoric monologue", "Dev"),
        ("CASE_HI_EN_01", "Court / State vs A Nobody", "Hindi/EN", "315.0s", "Realistic court echo; heavy legal code-switching", "Test"),
        ("CASE_EN_03", "Legally Blonde (2001)", "English (EN)", "208.6s", "Clean speech; perjury cross-examination admission", "Test"),
        ("CASE_HI_01", "Criminal Justice S3", "Hindi (HI)", "151.3s", "Studio clean; electronic alibi defense & bail", "Dev"),
        ("CASE_TA_02", "Parasakthi (480p Clip)", "Tamil (TA)", "299.0s", "Compressed historical mono; compression resilience", "Test"),
        ("CASE_TE_02", "Naandhi (2021)", "Telugu (TE)", "336.6s", "Dramatic court; Section 211 IPC police inquiry motion", "Test"),
        ("CASE_TE_03", "DJ Tillu (2022)", "Telugu (TE)", "285.2s", "Fast colloquial slang; conversational code-switching", "Dev")
    ]

    for i, row in enumerate(dataset_rows):
        for j, val in enumerate(row):
            cell = table.cell(i+1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if i % 2 == 0 else RGBColor(17, 24, 39)
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9)
            p.font.color.rgb = TEXT_LIGHT if j != 0 else BLUE_ACCENT
            if j in [0, 2, 3, 5]:
                p.alignment = PP_ALIGN.CENTER

    add_speaker_notes(s11,
        timing="50 Seconds",
        goal="Present the experimental corpus, highlighting linguistic and acoustic diversity across 10 cases.",
        script="To validate our system rigorously, we curated an empirical testbed comprising 10 diverse courtroom proceeding recordings totaling over 42 minutes across four languages: English, Hindi, Telugu, and Tamil. As shown in the table, the corpus was split into Development and Test sets. It reflects genuine real-world acoustic variance: from studio-quality cross-examinations like 'My Cousin Vinny' and 'Legally Blonde', to realistic ambient courtroom reverberation in 'Court', historical 1952 mono recordings in 'Parasakthi', and dynamic Indian regional proceedings like 'Naandhi' and 'DJ Tillu'. Each case was human-annotated according to our gold-standard protocol to produce verified reference transcripts and sentence salience scores.",
        viva_tip="Mention that the dataset includes both formal courtroom procedure and colloquial conversational legal speech to test system robustness against code-switching and noise.")

    # =========================================================================
    # SLIDE 12: EMPIRICAL BENCHMARK EVALUATION RESULTS
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Evaluation", "Empirical Evaluation & Comparative Benchmark Results", 
               "Quantitative assessment against human-annotated gold standards across 5 NLP metrics")

    # Left: Benchmark Graphic Asset
    bench_path = os.path.join(ASSETS_DIR, "benchmark_metrics_chart.png")
    if os.path.exists(bench_path):
        s12.shapes.add_picture(bench_path, Inches(0.8), Inches(1.9), width=Inches(7.2), height=Inches(5.0))

    # Right: Results Discussion Card
    c_res = add_card(s12, 8.2, 1.9, 4.3, 5.0, border_color=GREEN_ACCENT)
    tf = c_res.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "KEY EVALUATION FINDINGS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT

    res_findings = [
        ("TextRank Dominance (0.614 Sent-F1)", "TextRank graph centrality outperformed both TF-IDF (0.521) and Embedding MMR (0.583), achieving highest Sentence F1 and ROUGE-L (0.518)."),
        ("Why Graph Centrality Wins", "Court proceedings revolve around intense dialogue. Adversarial cross-examinations feature high lexical term-sharing across questions and answers, creating dense graph clusters."),
        ("Embedding MMR Nuance", "Semantic embeddings (MiniLM) capture conceptual themes well (BERTScore 0.648) but occasionally select tangential conversational remarks."),
        ("Academic Integrity Note", "Evaluated strictly against human-annotated extractive gold standards without synthetic metric fabrication.")
    ]
    for h, desc in res_findings:
        ph = tf.add_paragraph()
        ph.text = f"• {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = TEXT_WHITE
        ph.space_before = Pt(8)
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s12,
        timing="75 Seconds",
        goal="Present the core results clearly: TextRank graph centrality wins across Sentence F1, ROUGE, and BERTScore.",
        script="Now let us look at the empirical evaluation results. We evaluated all three summarization methods against our human-annotated gold-standard references at a 25% compression budget with legal boosting enabled. As shown in the comparative bar chart, Method B—TextRank Graph Centrality—achieved the highest overall performance, with a Sentence F1 of 0.614, ROUGE-1 of 0.568, and ROUGE-L of 0.518, beating both TF-IDF and Embedding MMR. The fundamental reason TextRank excels in courtrooms is discursive structure: judicial trials are adversarial dialogues where counsel and witnesses repeatedly invoke shared legal keywords and case facts. This term-sharing creates dense lexical affinity clusters in the TextRank graph, allowing PageRank to surface pivotal judicial sentences reliably.",
        viva_tip="Metrics explained: Sentence F1 measures verbatim sentence selection overlap with human judges. ROUGE-L measures longest common subsequence. BERTScore measures semantic vector similarity.")

    # =========================================================================
    # SLIDE 13: ABLATION STUDIES & ACADEMIC INSIGHTS
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "Ablation Study", "Ablation Studies: Legal Booster & Compression Trade-offs", 
               "Isolating the quantifiable impact of statutory cue weighting and length budget sensitivity")

    # Insert Ablation Charts Asset
    ablation_path = os.path.join(ASSETS_DIR, "ablation_charts.png")
    if os.path.exists(ablation_path):
        s13.shapes.add_picture(ablation_path, Inches(0.8), Inches(1.9), width=Inches(11.7), height=Inches(5.0))

    add_speaker_notes(s13,
        timing="70 Seconds",
        goal="Walk the panel through the two ablation studies, proving that your domain additions produced quantifiable gains.",
        script="To demonstrate academic rigor, we performed two critical ablation studies, illustrated on this slide. In Ablation 1 on the left, we isolated the impact of our Legal Domain Salience Booster on TextRank. When the booster was ablated or turned off, Sentence F1 dropped to 0.532. Activating our statutory cue weighting produced an immediate 8.2 percentage point gain in Sentence F1 to 0.614. Without the domain booster, high-frequency procedural banter crowded out concise, authoritative judicial orders. In Ablation 2 on the right, we evaluated compression ratio sensitivity across 15%, 25%, and 35% budgets. An ultra-concise 15% budget yields high precision (0.722) but misses key issues. A 35% budget increases recall (0.712) but introduces redundant dialogue. A 25% compression budget is Pareto-optimal, maximizing the harmonic F1 score at 0.614.",
        viva_tip="Remember the key number: '+8.2% Sentence F1 gain from Legal Domain Boosting'. This directly answers whether your custom domain heuristics actually helped.")

    # =========================================================================
    # SLIDE 14: PRODUCTION ENGINEERING & SYSTEM ARCHITECTURE
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "Engineering", "Production Engineering, API & Deployment Architecture", 
               "Scalable asynchronous processing, streaming simulation, and multi-service containerization")

    cards_eng = [
        ("FastAPI Asynchronous Backend",
         ["RESTful endpoints (POST /jobs, GET /jobs/{id}, GET /summary).",
          "Non-blocking background thread pool for heavy ASR/summarization tasks.",
          "SQLite persistence tracks job state: PENDING -> PROCESSING -> COMPLETED -> FAILED.",
          "Full OpenAPI Swagger documentation at http://localhost:8000/docs."],
         BLUE_ACCENT, 0.8, 2.0, 3.6, 4.8),
        ("Streamlit Interactive UI",
         ["Synchronized video/audio player with scrubbed temporal anchors.",
          "Side-by-side bilingual view: original vernacular transcript vs English summary.",
          "Color-coded provenance badges ([JUDICIAL_RULING] vs [ADVOCATE_ALLEGATION]).",
          "One-click multi-format exports: Plain Text (.txt), JSON (.json), and Printable PDF."],
         GREEN_ACCENT, 4.85, 2.0, 3.6, 4.8),
        ("Live Stream Simulator & Docker",
         ["Live Simulator (live_simulator.py): 15-second sliding audio buffers for live proceedings.",
          "Dynamic running summary updated with step latency under 2 seconds.",
          "Multi-service Docker Compose (FastAPI backend + Streamlit UI).",
          "Automated GitHub Actions CI quality assurance suite with pytest."],
         GOLD_ACCENT, 8.9, 2.0, 3.6, 4.8)
    ]

    for title, bullets, col, left, top, width, height in cards_eng:
        c = add_card(s14, left, top, width, height, border_color=col)
        tf = c.text_frame
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(10.5)
            pb.font.color.rgb = TEXT_LIGHT
            pb.space_before = Pt(8)

    add_speaker_notes(s14,
        timing="60 Seconds",
        goal="Showcase the full-stack engineering maturity: asynchronous API, job queue, Streamlit dashboard, live simulation, and Docker.",
        script="Moving from algorithmic design to production engineering, this project was architected as a complete multi-tier system. The backend is built with FastAPI, providing asynchronous REST endpoints for submitting court audio jobs and polling progress. A local SQLite database manages job state transitions from pending to completed. On the frontend, our interactive Streamlit web application provides synchronized video playback, side-by-side multilingual views, and one-click PDF, JSON, and TXT report downloads. For live courtroom hearings, we engineered a streaming simulator that ingests audio in 15-second sliding buffers, updating a running summary dynamically with step latency under 2 seconds. The entire stack is containerized via Docker and verified by automated GitHub Actions CI.",
        viva_tip="If asked about scalability: explain that the FastAPI asynchronous job queue decouples long-running speech transcription from the HTTP request cycle, preventing client timeouts.")

    # =========================================================================
    # SLIDE 15: INTERACTIVE UI & CASE STUDY DEMONSTRATION
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_header(s15, "Live Demonstration", "Interactive UI Walkthrough & Evidentiary Verification", 
               "Demonstrating video synchronization, provenance badges, and multi-format judicial reports")

    # Insert UI Mockup Graphic Asset
    ui_path = os.path.join(ASSETS_DIR, "ui_mockup.png")
    if os.path.exists(ui_path):
        s15.shapes.add_picture(ui_path, Inches(0.8), Inches(1.9), width=Inches(11.7), height=Inches(5.0))

    add_speaker_notes(s15,
        timing="75 Seconds",
        goal="Guide the panel through the UI, demonstrating the video player, telemetry metrics, and the green/amber badges.",
        script="This slide showcases our working Streamlit web interface during a real Telugu courtroom proceeding from our dataset—the Section 211 IPC police accountability motion in 'Naandhi'. At the top, you notice our prominent Mandatory Legal Disclaimer banner. Below it, real-time telemetry displays the detected language—Telugu with 96.5% confidence—total duration of 336 seconds, and an end-to-end processing latency of only 7.2 seconds. On the left is the synchronized video player. On the right is the key extractive summary. Notice the top card: badged in green as [JUDICIAL_RULING], showing both the Telugu original and English translation. Below it, notice the defense argument badged in amber as [ADVOCATE_ALLEGATION]. When a lawyer clicks on the timestamp [071.0s - 095.0s], the media player on the left automatically scrubs to that exact second, allowing instantaneous verification of the judge's spoken ruling.",
        viva_tip="Offer to show the running browser app right now during the review if they would like to see the live video scrub in action.")

    # =========================================================================
    # SLIDE 16: SYSTEM LIMITATIONS & ETHICAL CONSIDERATIONS
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16)
    add_header(s16, "Ethics & Limits", "System Limitations & Ethical Legal Safeguards", 
               "Addressing technical boundary conditions, low-resource regional dialects, and assistive usage")

    cards_eth = [
        ("1. Dialectal & Slang Variability",
         ["ASR accuracy degrades on heavily accented colloquial regional slang (e.g., street Telugu in DJ Tillu) compared to formal courtroom speech.",
          "Whisper word error rate increases on rapid overlapping speech.",
          "Mitigation: Legal decoding prompt conditions statutory terminology."],
         RED_ACCENT, 0.8, 2.0, 3.6, 4.8),
        ("2. Absence of Acoustic Diarization",
         ["Current system classifies speakers via lexical cue patterns rather than neural acoustic voiceprints.",
          "Overlapping multi-speaker interruptions can blend in ASR transcription.",
          "Mitigation: Proportional sentence splitting and explicit disclaimer."],
         GOLD_ACCENT, 4.85, 2.0, 3.6, 4.8),
        ("3. Ethical Mandate: Human-in-the-Loop",
         ["Strict assistive status: this software is an aid for research and review, NEVER a judge or lawyer substitute.",
          "Automated summaries cannot be entered as unverified legal evidence.",
          "Mandatory disclaimer embedded in UI, JSON exports, and printable PDFs."],
         GREEN_ACCENT, 8.9, 2.0, 3.6, 4.8)
    ]

    for title, bullets, col, left, top, width, height in cards_eth:
        c = add_card(s16, left, top, width, height, border_color=col)
        tf = c.text_frame
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(10.5)
            pb.font.color.rgb = TEXT_LIGHT
            pb.space_before = Pt(8)

    add_speaker_notes(s16,
        timing="50 Seconds",
        goal="Demonstrate intellectual honesty and academic maturity by proactively acknowledging real limitations and ethical safeguards.",
        script="An honest assessment of limitations is vital for academic integrity. We identify three boundary conditions: First, dialectal variability: while speech recognition performs exceptionally on formal court Hindi and English, word error rate increases on rapid regional slang, such as colloquial Telugu in 'DJ Tillu'. Second, the current implementation relies on lexical patterns rather than neural acoustic diarization to distinguish speakers. Third, and most importantly, our ethical mandate: this software is engineered strictly as an assistive research tool. Automated AI summaries must never replace formal judicial review. To enforce this, a legal disclaimer is permanently embedded in the UI header and all exported PDF reports.",
        viva_tip="Evaluators love when students honestly discuss limitations before being asked. It demonstrates that you understand the real-world deployment challenges of your system.")

    # =========================================================================
    # SLIDE 17: FUTURE ROADMAP & CONCLUSION
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17)
    add_header(s17, "Conclusion", "Future Trajectory & Project Conclusion", 
               "Summary of major capstone contributions and next-generation judicial AI roadmap")

    # Left: Future Work
    c_fut = add_card(s17, 0.8, 2.0, 5.7, 4.8, border_color=BLUE_ACCENT)
    tf = c_fut.text_frame
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "FUTURE RESEARCH ROADMAP"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    fut_items = [
        ("Neural Speaker Diarization (PyAnnote)", "Integrate pre-trained voice biometrics to cluster speaker embeddings, explicitly tagging [JUDGE] vs [PROSECUTOR] vs [WITNESS] directly from acoustic signals."),
        ("Real-Time Court Stenography WebSockets", "Deploy full-duplex WebSocket connections for sub-second live streaming in active digital courtrooms."),
        ("Offline Legal LLM Consistency Auditor", "Use a quantized offline SLM (e.g. Phi-3 / Gemma) to audit extractive summaries for semantic consistency without introducing hallucination risk.")
    ]
    for h, desc in fut_items:
        ph = tf.add_paragraph()
        ph.text = f"• {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = TEXT_WHITE
        ph.space_before = Pt(8)
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_LIGHT

    # Right: Summary of Deliverables
    c_sum = add_card(s17, 6.8, 2.0, 5.7, 4.8, border_color=GREEN_ACCENT)
    tf = c_sum.text_frame
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "SUMMARY OF CAPSTONE DELIVERABLES"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT

    deliv_items = [
        ("Complete End-to-End Pipeline", "Ingestion, EBU R128 normalization, faster-whisper ASR, cleaning, segmentation, summarization, and export."),
        ("Benchmarked Algorithmic Suite", "Comparative evaluation of TF-IDF, TextRank, and Embedding MMR across 10 multilingual court proceedings."),
        ("8.2% F1 Boost via Domain Booster", "Quantifiable ablation proof that statutory cue weighting and allegation separation improve summary quality."),
        ("Production Web Application & API", "FastAPI asynchronous service, SQLite queue, Streamlit interactive dashboard, live simulator, and Docker stack.")
    ]
    for h, desc in deliv_items:
        ph = tf.add_paragraph()
        ph.text = f"✅ {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = TEXT_WHITE
        ph.space_before = Pt(8)
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s17,
        timing="60 Seconds",
        goal="Deliver a confident, articulate conclusion summarizing your achievements and future roadmap.",
        script="In conclusion, this capstone project successfully demonstrates a fully functional, reproducible, and legally safe speech-to-summary system for multilingual court proceedings. By enforcing strict extractiveness, microsecond temporal anchoring, and legal domain cue weighting, we overcome the catastrophic hallucination risks of generative LLMs while maintaining high operational throughput—achieving an RTF of 0.049 on commodity CPU hardware. For future work, we plan to integrate PyAnnote neural speaker diarization for voice-based role attribution, and deploy real-time WebSocket streaming. Our complete modular codebase, evaluation benchmarks, and interactive application stand ready for real-world assistive testing. Thank you, and I look forward to your questions.",
        viva_tip="Maintain eye contact and smile warmly. Conclude promptly within your allocated time limit.")

    # =========================================================================
    # SLIDE 18: VIVA VOCE CHEAT SHEET - TOP 6 QUESTIONS & 20-SEC ANSWERS
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18)
    add_header(s18, "Defense Guide", "Review Defense & Viva Voce Q&A Cheat Sheet", 
               "Top anticipated evaluation questions and crisp 20-second model defense answers")

    viva_cards = [
        ("Q1: Why extractive instead of GPT-4?",
         "Abstractive LLMs hallucinate and can invert legal meaning or conflate an advocate's unproven allegation with a court order. Extractive summarization guarantees 100% verbatim fidelity, microsecond video anchoring, and zero hallucination.",
         RED_ACCENT, 0.8, 2.0, 5.7, 2.3),
        ("Q2: Why EBU R128 instead of peak norm?",
         "Peak normalization scales audio to instantaneous gavel spikes, leaving quiet witness testimony inaudible. EBU R128 (-23 LUFS) uses K-weighted psychoacoustic filtering to balance integrated human perceptual loudness over time.",
         BLUE_ACCENT, 6.8, 2.0, 5.7, 2.3),
        ("Q3: Why did TextRank beat MiniLM MMR?",
         "Courtroom cross-examinations revolve around shared legal keywords between counsel and witnesses. Graph centrality directly models these term-sharing affinity clusters, whereas embeddings occasionally pick tangential dialogue.",
         GREEN_ACCENT, 0.8, 4.5, 5.7, 2.3),
        ("Q4: How do you prevent Whisper repetition?",
         "We disable 'condition_on_previous_text', which prevents Whisper from getting trapped in infinite repetition loops on background courtroom reverberation and ambient echo.",
         GOLD_ACCENT, 6.8, 4.5, 5.7, 2.3)
    ]

    for q_title, answer, col, left, top, width, height in viva_cards:
        c = add_card(s18, left, top, width, height, border_color=col)
        tf = c.text_frame
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.2)
        p = tf.paragraphs[0]
        p.text = q_title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        p_ans = tf.add_paragraph()
        p_ans.text = f"Answer: {answer}"
        p_ans.font.size = Pt(10)
        p_ans.font.color.rgb = TEXT_LIGHT
        p_ans.space_before = Pt(6)

    add_speaker_notes(s18,
        timing="As needed during Q&A",
        goal="Give yourself instant reference during the defense review if professors challenge your technical choices.",
        script="This slide serves as an immediate reference for the panel's technical inquiries, covering our core justifications: Extractive fidelity vs LLM hallucination, EBU R128 psychoacoustic normalization vs peak normalization, TextRank graph centrality dynamics, and Whisper repetition suppression.",
        viva_tip="If asked any of these questions, keep your answer under 30 seconds. State the exact engineering reason with confidence.")

    # Save presentation
    os.makedirs(os.path.dirname(OUTPUT_PPTX), exist_ok=True)
    prs.save(OUTPUT_PPTX)
    print(f"Presentation successfully created at: {OUTPUT_PPTX}")

if __name__ == '__main__':
    create_presentation()
