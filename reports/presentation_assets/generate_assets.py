"""
Script to generate high-resolution professional figures for the presentation.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs('reports/presentation_assets', exist_ok=True)

# Set high DPI and aesthetic styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# -------------------------------------------------------------
# 1. ARCHITECTURE DIAGRAM
# -------------------------------------------------------------
def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
    fig.patch.set_facecolor('#0B132B')
    ax.set_facecolor('#0B132B')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Title
    ax.text(50, 96, "END-TO-END COURTROOM SUMMARIZATION ARCHITECTURE", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#FFFFFF')
    ax.text(50, 92, "Strictly Extractive • Temporally Anchored • Multilingual • Legal-Domain Reinforced", 
            ha='center', va='center', fontsize=11, color='#48CAE4', style='italic')

    # Stages definition
    stages = [
        {
            "num": "01", "name": "ACOUSTIC FRONT-END", "color": "#1C2541", "border": "#3A86FF",
            "items": ["16 kHz Mono WAV Demuxing", "EBU R128 Norm (-23 LUFS)", "Bandpass (80 Hz - 7.5 kHz)", "Conservative VAD (-35 dB)"],
            "x": 3, "w": 17
        },
        {
            "num": "02", "name": "MULTILINGUAL ASR", "color": "#1C2541", "border": "#00B4D8",
            "items": ["faster-whisper (CTranslate2)", "INT8 Quantized Inference", "Automatic Language ID (LID)", "Legal Prompt Conditioning"],
            "x": 22.5, "w": 17
        },
        {
            "num": "03", "name": "LEGAL PREPROCESSING", "color": "#1C2541", "border": "#06D6A0",
            "items": ["Disfluency Normalization", "Negation Safety Lock", "Abbrev Protection (Sec., v.)", "Proportional Timestamps"],
            "x": 42, "w": 17
        },
        {
            "num": "04", "name": "EXTRACTIVE ENGINES", "color": "#1C2541", "border": "#FFD166",
            "items": ["Method A: TF-IDF + Position", "Method B: TextRank Graph", "Method C: MiniLM MMR", "Chronological Ordering"],
            "x": 61.5, "w": 17
        },
        {
            "num": "05", "name": "LEGAL ENHANCER & DELIVERY", "color": "#1C2541", "border": "#EF476F",
            "items": ["Statutory Cue Booster (2.5x)", "Allegation Segregator", "FastAPI + SQLite Queue", "Streamlit UI & PDF/JSON"],
            "x": 81, "w": 16.5
        }
    ]

    for stage in stages:
        # Container box
        box = patches.FancyBboxPatch((stage["x"], 16), stage["w"], 68, 
                                     boxstyle="round,pad=0.8,rounding_size=2",
                                     facecolor=stage["color"], edgecolor=stage["border"], linewidth=2.5)
        ax.add_patch(box)

        # Header badge
        badge = patches.FancyBboxPatch((stage["x"] + 1, 74), stage["w"] - 2, 7.5,
                                      boxstyle="round,pad=0.3,rounding_size=1",
                                      facecolor=stage["border"], edgecolor='none')
        ax.add_patch(badge)
        ax.text(stage["x"] + stage["w"]/2, 79, f"STAGE {stage['num']}", ha='center', va='center', 
                fontsize=8.5, fontweight='bold', color='#0B132B')
        ax.text(stage["x"] + stage["w"]/2, 76, stage["name"], ha='center', va='center', 
                fontsize=8.5, fontweight='bold', color='#FFFFFF')

        # Sub items
        y_pos = 65
        for item in stage["items"]:
            # bullet icon
            ax.plot(stage["x"] + 2, y_pos, marker='s', markersize=4, color=stage["border"])
            ax.text(stage["x"] + 3.8, y_pos, item, ha='left', va='center', 
                    fontsize=8.5, color='#E0E6ED', fontweight='medium')
            y_pos -= 12

    # Draw arrows between stages
    for i in range(len(stages) - 1):
        x_start = stages[i]["x"] + stages[i]["w"] + 0.4
        x_end = stages[i+1]["x"] - 0.4
        ax.annotate("", xy=(x_end, 50), xytext=(x_start, 50),
                    arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", 
                                    lw=2.5, color='#48CAE4', mutation_scale=15))

    # Bottom Safeguards Banner
    safe_box = patches.FancyBboxPatch((3, 3), 94.5, 9, 
                                     boxstyle="round,pad=0.5,rounding_size=1.5",
                                     facecolor='#03071E', edgecolor='#FFB703', linewidth=1.5)
    ax.add_patch(safe_box)
    ax.text(50, 8.5, "CORE SAFETY GUARENTEES: ZERO HALLUCINATION • VERBATIM EXTRACTION • TEMPORAL ANCHORS", 
            ha='center', va='center', fontsize=10, fontweight='bold', color='#FFB703')
    ax.text(50, 5, "[JUDICIAL_RULING] Prioritized (2.5x) | [ADVOCATE_ALLEGATION] Penalized & Badged | Mandatory Legal Review Disclaimer", 
            ha='center', va='center', fontsize=8.5, color='#D8E2DC')

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/architecture_diagram.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Created architecture_diagram.png")


# -------------------------------------------------------------
# 2. AUDIO PREPROCESSING & LOUDNESS NORMALIZATION WAVEFORM
# -------------------------------------------------------------
def create_waveform_diagram():
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 7.5), dpi=300, facecolor='#0D1B2A')
    
    t = np.linspace(0, 10, 2000)
    
    # 1. Raw Court Audio with gavel strikes and quiet witness
    np.random.seed(42)
    quiet_witness = 0.08 * np.sin(2 * np.pi * 3.5 * t) * (t < 4) + 0.04 * np.random.randn(len(t))
    gavel_strike = 0.95 * np.exp(-((t - 4.5)/0.15)**2) * np.sin(2 * np.pi * 40 * t)
    advocate_loud = 0.65 * np.sin(2 * np.pi * 4 * t) * (t > 5.5) + 0.05 * np.random.randn(len(t))
    raw_signal = quiet_witness + gavel_strike + advocate_loud
    
    ax1.set_facecolor('#1B263B')
    ax1.plot(t, raw_signal, color='#E63946', lw=1.2)
    ax1.set_title("1. Raw Court Audio: Gavel Strike Peak (0 dBFS) Buries Quiet Witness Speech", color='#FFFFFF', fontsize=11, fontweight='bold', loc='left')
    ax1.axhline(0, color='#415A77', lw=0.8, linestyle='--')
    ax1.text(2, 0.4, "Quiet Witness Testimony\n(~ -38 dBFS)", color='#A8DADC', fontsize=9, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#0D1B2A', edgecolor='#457B9D'))
    ax1.text(4.5, 0.75, "Gavel Strike Spike\n(Peak Clamping)", color='#E63946', fontsize=9, ha='center', fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#0D1B2A', edgecolor='#E63946'))
    ax1.text(8, 0.4, "Loud Advocate Argument\n(~ -12 dBFS)", color='#F1FAEE', fontsize=9, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#0D1B2A', edgecolor='#457B9D'))
    ax1.set_ylim(-1.1, 1.1)
    ax1.tick_params(colors='#A8DADC')
    ax1.grid(True, color='#415A77', alpha=0.3)

    # 2. EBU R128 (-23 LUFS) Normalized
    norm_witness = 0.38 * np.sin(2 * np.pi * 3.5 * t) * (t < 4) + 0.02 * np.random.randn(len(t))
    norm_gavel = 0.55 * np.exp(-((t - 4.5)/0.15)**2) * np.sin(2 * np.pi * 40 * t)
    norm_advocate = 0.45 * np.sin(2 * np.pi * 4 * t) * (t > 5.5) + 0.03 * np.random.randn(len(t))
    norm_signal = norm_witness + norm_gavel + norm_advocate

    ax2.set_facecolor('#1B263B')
    ax2.plot(t, norm_signal, color='#00B4D8', lw=1.2)
    ax2.set_title("2. EBU R128 Psychoacoustic Normalization (-23 LUFS): Uniform Speech Intelligibility", color='#FFFFFF', fontsize=11, fontweight='bold', loc='left')
    ax2.axhline(0, color='#415A77', lw=0.8, linestyle='--')
    ax2.axhline(0.5, color='#FFD166', lw=0.8, linestyle=':', label='True Peak Ceiling (-1.5 dBFS)')
    ax2.axhline(-0.5, color='#FFD166', lw=0.8, linestyle=':')
    ax2.text(2, 0.65, "Witness Formants Amplified\n& Intelligible", color='#00B4D8', fontsize=9, ha='center', fontweight='bold')
    ax2.text(7.5, 0.65, "Dynamic Range Balanced\nAcross All Speakers", color='#90E0EF', fontsize=9, ha='center')
    ax2.set_ylim(-1.1, 1.1)
    ax2.tick_params(colors='#A8DADC')
    ax2.grid(True, color='#415A77', alpha=0.3)
    ax2.legend(loc='lower right', facecolor='#0D1B2A', edgecolor='#415A77', labelcolor='#FFFFFF')

    # 3. VAD Speech Segmentation with Safety Margins
    ax3.set_facecolor('#1B263B')
    ax3.plot(t, norm_signal, color='#6C757D', alpha=0.5, lw=1)
    # Speech chunks highlights
    ax3.axvspan(0.2, 3.9, color='#06D6A0', alpha=0.35, label='Speech Chunk 1 (Witness Testimony)')
    ax3.axvspan(5.3, 9.8, color='#3A86FF', alpha=0.35, label='Speech Chunk 2 (Advocate Dialogue)')
    # Margins
    ax3.axvspan(0.0, 0.2, color='#FFD166', alpha=0.5, label='200ms Acoustic Margin')
    ax3.axvspan(3.9, 4.1, color='#FFD166', alpha=0.5)
    ax3.axvspan(5.1, 5.3, color='#FFD166', alpha=0.5)
    ax3.axvspan(9.8, 10.0, color='#FFD166', alpha=0.5)
    
    ax3.set_title("3. Conservative VAD & 200ms Margin Padding: Zero Truncation of Quiet Speech", color='#FFFFFF', fontsize=11, fontweight='bold', loc='left')
    ax3.set_xlabel("Time (Seconds)", color='#A8DADC', fontsize=10)
    ax3.set_ylim(-1.1, 1.1)
    ax3.tick_params(colors='#A8DADC')
    ax3.grid(True, color='#415A77', alpha=0.3)
    ax3.legend(loc='lower right', facecolor='#0D1B2A', edgecolor='#415A77', labelcolor='#FFFFFF', fontsize=8.5)

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/audio_processing_waveform.png', dpi=300, facecolor='#0D1B2A', edgecolor='none')
    plt.close()
    print("Created audio_processing_waveform.png")


# -------------------------------------------------------------
# 3. BENCHMARK COMPARISON CHART
# -------------------------------------------------------------
def create_benchmark_chart():
    fig, ax = plt.subplots(figsize=(12, 6.8), dpi=300, facecolor='#0F172A')
    ax.set_facecolor('#1E293B')

    metrics = ['Sentence F1', 'ROUGE-1 F1', 'ROUGE-2 F1', 'ROUGE-L F1', 'BERTScore F1']
    
    # Values from Capstone Report Table 11.1
    tfidf = [0.521, 0.492, 0.284, 0.441, 0.582]
    textrank = [0.614, 0.568, 0.342, 0.518, 0.654]
    embedding = [0.583, 0.541, 0.315, 0.489, 0.648]

    x = np.arange(len(metrics))
    width = 0.26

    rects1 = ax.bar(x - width, tfidf, width, label='Method A: TF-IDF + Position Prior', color='#38BDF8', edgecolor='#0284C7', linewidth=1.2)
    rects2 = ax.bar(x, textrank, width, label='Method B: TextRank (Graph Centrality) [TOP]', color='#10B981', edgecolor='#059669', linewidth=1.5)
    rects3 = ax.bar(x + width, embedding, width, label='Method C: Embedding (MiniLM + MMR)', color='#F59E0B', edgecolor='#D97706', linewidth=1.2)

    # Add values on top of bars
    for rects, color in [(rects1, '#E0F2FE'), (rects2, '#D1FAE5'), (rects3, '#FEF3C7')]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.3f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=color)

    ax.set_title('COMPARATIVE EVALUATION ACROSS EXTRACTIVE SUMMARIZATION ALGORITHMS', 
                 fontsize=14, fontweight='bold', color='#FFFFFF', pad=20)
    ax.set_subtitle = ax.text(0.5, 1.02, 'Evaluated on Gold-Standard Legal Datasets (25% Budget, Legal Booster Active)', 
                              transform=ax.transAxes, ha='center', fontsize=10, color='#94A3B8', style='italic')

    ax.set_ylabel('Score (0.0 to 1.0)', color='#E2E8F0', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, color='#F8FAFC', fontsize=11, fontweight='bold')
    ax.set_ylim(0, 0.78)
    ax.tick_params(colors='#CBD5E1')
    ax.grid(axis='y', color='#334155', linestyle='--', alpha=0.7)

    # Highlight box for TextRank
    ax.annotate('Highest Sent-F1 (0.614) & ROUGE-L (0.518)\nOptimal on Dialogue Term-Sharing', 
                xy=(1, 0.62), xytext=(1.2, 0.71),
                arrowprops=dict(facecolor='#10B981', shrink=0.08, width=1.5, headwidth=6),
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#064E3B', edgecolor='#10B981', linewidth=1.5),
                color='#ECFDF5', fontsize=9.5, fontweight='bold')

    ax.legend(facecolor='#0F172A', edgecolor='#475569', labelcolor='#FFFFFF', loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/benchmark_metrics_chart.png', dpi=300, facecolor='#0F172A', edgecolor='none')
    plt.close()
    print("Created benchmark_metrics_chart.png")


# -------------------------------------------------------------
# 4. ABLATION STUDIES (LEGAL BOOST + COMPRESSION SENSITIVITY)
# -------------------------------------------------------------
def create_ablation_charts():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5), dpi=300, facecolor='#0B132B')
    
    # ---------------- Subplot 1: Legal Domain Booster Impact ----------------
    ax1.set_facecolor('#1C2541')
    categories = ['Sentence F1', 'ROUGE-1', 'ROUGE-2', 'ROUGE-L']
    boost_off = [0.532, 0.495, 0.276, 0.448]
    boost_on  = [0.614, 0.568, 0.342, 0.518]
    
    x1 = np.arange(len(categories))
    w = 0.32
    
    r1 = ax1.bar(x1 - w/2, boost_off, w, label='Legal Boost OFF (Ablated Baseline)', color='#64748B', edgecolor='#475569')
    r2 = ax1.bar(x1 + w/2, boost_on, w, label='Legal Boost ON (+8.2% F1 Gain)', color='#06D6A0', edgecolor='#059669', linewidth=1.5)
    
    for r in r1:
        ax1.annotate(f"{r.get_height():.3f}", xy=(r.get_x() + r.get_width()/2, r.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', fontsize=8, color='#CBD5E1')
    for r in r2:
        ax1.annotate(f"{r.get_height():.3f}", xy=(r.get_x() + r.get_width()/2, r.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', fontsize=8, fontweight='bold', color='#A7F3D0')

    ax1.annotate('+8.2% Gain\nIn Sentence F1', xy=(0.16, 0.62), xytext=(0.4, 0.68),
                 arrowprops=dict(facecolor='#06D6A0', shrink=0.05, width=1.5, headwidth=6),
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#022C22', edgecolor='#06D6A0'),
                 color='#A7F3D0', fontsize=9, fontweight='bold')

    ax1.set_title('Ablation 1: Impact of Legal Domain Booster\n(TextRank @ 25% Compression)', 
                  fontsize=12, fontweight='bold', color='#FFFFFF', pad=12)
    ax1.set_xticks(x1)
    ax1.set_xticklabels(categories, color='#F8FAFC', fontsize=10, fontweight='bold')
    ax1.set_ylim(0, 0.76)
    ax1.tick_params(colors='#CBD5E1')
    ax1.grid(axis='y', color='#334155', linestyle='--', alpha=0.5)
    ax1.legend(facecolor='#0B132B', edgecolor='#475569', labelcolor='#FFFFFF', loc='upper left', fontsize=9)

    # ---------------- Subplot 2: Compression Ratio Sensitivity ----------------
    ax2.set_facecolor('#1C2541')
    ratios = ['15% (Ultra-Concise)', '25% (Balanced Default)', '35% (Comprehensive)']
    prec = [0.722, 0.635, 0.514]
    rec  = [0.481, 0.598, 0.712]
    f1   = [0.577, 0.614, 0.597]

    x2 = np.arange(len(ratios))
    
    ax2.plot(x2, prec, marker='o', markersize=8, color='#38BDF8', lw=2.5, label='Sentence Precision')
    ax2.plot(x2, rec, marker='s', markersize=8, color='#F59E0B', lw=2.5, label='Sentence Recall')
    ax2.plot(x2, f1, marker='^', markersize=10, color='#10B981', lw=3, label='Sentence F1 (Harmonic Mean)')

    for i in range(len(ratios)):
        ax2.annotate(f"{prec[i]:.3f}", (x2[i], prec[i] + 0.02), ha='center', fontsize=8.5, color='#BAE6FD', fontweight='bold')
        ax2.annotate(f"{rec[i]:.3f}", (x2[i], rec[i] - 0.035), ha='center', fontsize=8.5, color='#FDE68A', fontweight='bold')
        ax2.annotate(f"{f1[i]:.3f}", (x2[i], f1[i] + 0.025), ha='center', fontsize=9.5, color='#A7F3D0', fontweight='bold')

    # Highlight 25% sweet spot
    ax2.axvspan(0.7, 1.3, color='#10B981', alpha=0.15, linestyle=':', linewidth=1.5)
    ax2.annotate('Pareto Optimal Budget (25%)\nMaximizes F1 (0.614)', xy=(1, 0.62), xytext=(0.4, 0.74),
                 arrowprops=dict(facecolor='#10B981', shrink=0.08, width=1.5, headwidth=6),
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#064E3B', edgecolor='#10B981'),
                 color='#ECFDF5', fontsize=9.5, fontweight='bold')

    ax2.set_title('Ablation 2: Compression Ratio Sensitivity\n(Trade-off between Precision and Recall)', 
                  fontsize=12, fontweight='bold', color='#FFFFFF', pad=12)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(ratios, color='#F8FAFC', fontsize=9.5, fontweight='bold')
    ax2.set_ylim(0.40, 0.82)
    ax2.tick_params(colors='#CBD5E1')
    ax2.grid(True, color='#334155', linestyle='--', alpha=0.5)
    ax2.legend(facecolor='#0B132B', edgecolor='#475569', labelcolor='#FFFFFF', loc='lower right', fontsize=9)

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/ablation_charts.png', dpi=300, facecolor='#0B132B', edgecolor='none')
    plt.close()
    print("Created ablation_charts.png")


# -------------------------------------------------------------
# 5. UI INTERFACE & DEMO VISUALIZATION
# -------------------------------------------------------------
def create_ui_mockup():
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Top App Bar
    app_bar = patches.FancyBboxPatch((2, 91), 96, 7.5, boxstyle="round,pad=0.3,rounding_size=1",
                                    facecolor='#1E293B', edgecolor='#334155', linewidth=1.5)
    ax.add_patch(app_bar)
    ax.text(5, 94.8, "[COURT PROCEEDING SUMMARIZER]", fontsize=13, fontweight='bold', color='#F8FAFC')
    ax.text(62, 94.8, "Speech & Language Processing Capstone • Production UI", fontsize=9.5, color='#94A3B8')

    # Mandatory Legal Banner
    banner = patches.FancyBboxPatch((2, 84.5), 96, 5.2, boxstyle="round,pad=0.2,rounding_size=0.8",
                                   facecolor='#450A0A', edgecolor='#DC2626', linewidth=1.2)
    ax.add_patch(banner)
    ax.text(50, 87.1, "[MANDATORY LEGAL DISCLAIMER] Strictly an assistive reference tool. Human verification required.",
            ha='center', va='center', fontsize=9, fontweight='bold', color='#FCA5A5')

    # Telemetry Row
    metrics_data = [
        ("Detected Language", "Telugu (TE)", "96.5% Confidence", "#38BDF8"),
        ("Audio Duration", "336.6 Seconds", "16 kHz Mono WAV", "#34D399"),
        ("Processing Latency", "7.2 Seconds", "RTF = 0.049 (20x Realtime)", "#FBBF24"),
        ("Summarization Method", "TextRank Graph", "25% Budget + Domain Boost", "#A78BFA")
    ]
    for idx, (title, val, sub, col) in enumerate(metrics_data):
        x_m = 2 + idx * 24.5
        m_box = patches.FancyBboxPatch((x_m, 73.5), 22.5, 9.5, boxstyle="round,pad=0.3,rounding_size=1",
                                      facecolor='#111827', edgecolor='#1F2937', linewidth=1.2)
        ax.add_patch(m_box)
        ax.text(x_m + 11.2, 80.5, title.upper(), ha='center', fontsize=7.5, fontweight='bold', color='#9CA3AF')
        ax.text(x_m + 11.2, 77.2, val, ha='center', fontsize=11, fontweight='bold', color=col)
        ax.text(x_m + 11.2, 74.8, sub, ha='center', fontsize=7.5, color='#6B7280')

    # Left Column: Video Player Simulation
    vid_box = patches.FancyBboxPatch((2, 11), 46, 60.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                                    facecolor='#1E293B', edgecolor='#334155', linewidth=1.5)
    ax.add_patch(vid_box)
    ax.text(5, 68.5, "SOURCE COURT MEDIA PLAYER (SYNCHRONIZED)", fontsize=10, fontweight='bold', color='#38BDF8')

    # Video screen placeholder
    screen = patches.FancyBboxPatch((4, 25), 42, 40, boxstyle="round,pad=0.2,rounding_size=1",
                                   facecolor='#030712', edgecolor='#1F2937')
    ax.add_patch(screen)
    ax.text(25, 47, "▶ [COURT PROCEEDING VIDEO]", ha='center', fontsize=13, fontweight='bold', color='#6B7280')
    ax.text(25, 41, "Case: CASE_TE_02 (Naandhi Section 211 Motion)", ha='center', fontsize=9.5, color='#9CA3AF')
    ax.text(25, 36, "Active Timestamp: 01:11 / 05:36 (Scrubbed to Ruling)", ha='center', fontsize=9, color='#10B981', fontweight='bold')

    # Video playback controls bar
    ctrl_bar = patches.FancyBboxPatch((4, 14), 42, 8.5, boxstyle="round,pad=0.2,rounding_size=0.8",
                                     facecolor='#0F172A', edgecolor='#334155')
    ax.add_patch(ctrl_bar)
    ax.text(7, 18.2, "> 01:11", fontsize=9, color='#FFFFFF', fontweight='bold')
    # scrubber line
    ax.plot([14, 38], [18.2, 18.2], color='#334155', lw=4)
    ax.plot([14, 22], [18.2, 18.2], color='#38BDF8', lw=4)
    ax.plot(22, 18.2, marker='o', markersize=7, color='#FFFFFF')
    ax.text(42, 18.2, "05:36", ha='right', fontsize=9, color='#FFFFFF')

    # Right Column: Extractive Summary Panel with Badges
    sum_box = patches.FancyBboxPatch((50, 11), 48, 60.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                                    facecolor='#1E293B', edgecolor='#334155', linewidth=1.5)
    ax.add_patch(sum_box)
    ax.text(53, 68.5, "KEY EXTRACTIVE SUMMARY (VERBATIM & ANCHORED)", fontsize=10, fontweight='bold', color='#10B981')

    # Card 1: Judicial Ruling (Green badge)
    c1 = patches.FancyBboxPatch((52, 43), 44, 23, boxstyle="round,pad=0.4,rounding_size=1",
                               facecolor='#064E3B', edgecolor='#059669', linewidth=1.8)
    ax.add_patch(c1)
    # Badge
    b1 = patches.FancyBboxPatch((54, 60.5), 18, 4, boxstyle="round,pad=0.2,rounding_size=0.5",
                                facecolor='#10B981', edgecolor='none')
    ax.add_patch(b1)
    ax.text(63, 62.5, "[JUDICIAL_RULING]", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#022C22')
    ax.text(82, 62.5, "[071.0s - 095.0s]", ha='center', va='center', fontsize=8, fontweight='bold', color='#A7F3D0')
    
    ax.text(54, 55, "Summary (Bilingual English Translation):", fontsize=8, color='#D1FAE5', fontweight='bold')
    ax.text(54, 51.5, "\"The Court hereby orders a departmental and criminal inquiry", fontsize=8.5, color='#FFFFFF', style='italic')
    ax.text(54, 48.5, "under Section 211 against the investigating officers found guilty.\"", fontsize=8.5, color='#FFFFFF', style='italic', fontweight='bold')
    ax.text(54, 45, "Original Audio (Telugu): Verified Section 211 Statutory Order", fontsize=8, color='#6EE7B7')

    # Card 2: Advocate Allegation (Amber/Red badge)
    c2 = patches.FancyBboxPatch((52, 17), 44, 23, boxstyle="round,pad=0.4,rounding_size=1",
                               facecolor='#451A03', edgecolor='#D97706', linewidth=1.5)
    ax.add_patch(c2)
    b2 = patches.FancyBboxPatch((54, 34.5), 21, 4, boxstyle="round,pad=0.2,rounding_size=0.5",
                                facecolor='#F59E0B', edgecolor='none')
    ax.add_patch(b2)
    ax.text(64.5, 36.5, "[ADVOCATE_ALLEGATION]", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#451A03')
    ax.text(82, 36.5, "[112.4s - 128.0s]", ha='center', va='center', fontsize=8, fontweight='bold', color='#FDE68A')

    ax.text(54, 29, "Submission (Defense Argument - Non Binding):", fontsize=8, color='#FEF3C7', fontweight='bold')
    ax.text(54, 25.5, "\"Counsel submits that the evidence was fabricated by the", fontsize=8.5, color='#FFFFFF', style='italic')
    ax.text(54, 22.5, "prosecution to falsely implicate the petitioner under false charges.\"", fontsize=8.5, color='#FFFFFF', style='italic')
    ax.text(54, 19, "Salience Score: 0.0412 (Advocate Penalty 0.85x Applied)", fontsize=8, color='#FCD34D')

    # Bottom Export Buttons
    export_box = patches.FancyBboxPatch((2, 2.5), 96, 6.5, boxstyle="round,pad=0.3,rounding_size=1",
                                       facecolor='#1E293B', edgecolor='#334155', linewidth=1.2)
    ax.add_patch(export_box)
    ax.text(5, 5.7, "Court-Ready Multi-Format Exports:", fontsize=9.5, fontweight='bold', color='#94A3B8')

    buttons = [
        ("Download Plain Text (.txt)", 32, "#38BDF8"),
        ("Download Structured JSON (.json)", 55, "#34D399"),
        ("Download Printable PDF (.pdf)", 80, "#F43F5E")
    ]
    for b_title, b_x, b_col in buttons:
        btn = patches.FancyBboxPatch((b_x, 3.7), 21, 4.2, boxstyle="round,pad=0.2,rounding_size=0.6",
                                     facecolor='#0F172A', edgecolor=b_col, linewidth=1.2)
        ax.add_patch(btn)
        ax.text(b_x + 10.5, 5.8, b_title, ha='center', va='center', fontsize=8, fontweight='bold', color=b_col)

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/ui_mockup.png', dpi=300, facecolor='#0B0F19', edgecolor='none')
    plt.close()
    print("Created ui_mockup.png")

if __name__ == '__main__':
    create_architecture_diagram()
    create_waveform_diagram()
    create_benchmark_chart()
    create_ablation_charts()
    create_ui_mockup()
    print("All assets successfully generated!")
