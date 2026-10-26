"""
Generate specialized assets for the 16-slide Review 1 presentation:
1. vit_logo.png - Professional VIT Chennai emblem badge
2. architecture_clean.png - Clean horizontal architecture matching slide 8 specification
3. timeline_gantt.png - Week-by-week timeline with Review 1, 2, and 3
4. sample_input_output.png - Sample input transcript with highlighted extractive summary & timestamps
5. tools_grid.png - Clean visual tech stack grid
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs('reports/presentation_assets', exist_ok=True)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# -------------------------------------------------------------
# 1. VIT CHENNAI EMBLEM BADGE
# -------------------------------------------------------------
def create_vit_logo():
    fig, ax = plt.subplots(figsize=(4.5, 1.6), dpi=300)
    fig.patch.set_facecolor('#0B132B')
    ax.set_facecolor('#0B132B')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background card
    card = patches.FancyBboxPatch((2, 5), 96, 90, boxstyle="round,pad=0.5,rounding_size=3",
                                 facecolor='#1C2541', edgecolor='#3A86FF', linewidth=1.8)
    ax.add_patch(card)

    # VIT text block
    ax.text(22, 52, "VIT", ha='center', va='center', fontsize=26, fontweight='bold', color='#38BDF8')
    ax.plot([40, 40], [20, 80], color='#475569', lw=1.5)

    # Details
    ax.text(45, 68, "VELLORE INSTITUTE OF TECHNOLOGY", fontsize=8.5, fontweight='bold', color='#FFFFFF')
    ax.text(45, 50, "CHENNAI CAMPUS", fontsize=8, fontweight='bold', color='#F59E0B')
    ax.text(45, 32, "School of Computer Science & Engineering (AI & ML)", fontsize=7, color='#94A3B8')

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/vit_logo.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Created vit_logo.png")

# -------------------------------------------------------------
# 2. CLEAN SYSTEM ARCHITECTURE (SLIDE 8 SPEC)
# Video → Audio extraction → Preprocessing → Whisper ASR (language detection) 
# → Optional translation → Cleaning & sentence segmentation 
# → 3 summarizers + legal boost → Summary with timestamps → UI
# -------------------------------------------------------------
def create_clean_architecture():
    fig, ax = plt.subplots(figsize=(15, 6.2), dpi=300)
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    ax.text(50, 93, "END-TO-END COURTROOM SUMMARIZATION ARCHITECTURE", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#FFFFFF')

    steps = [
        {"name": "Court Video", "sub": "MP4 / MKV Input", "x": 1.5, "w": 9.5, "col": "#38BDF8"},
        {"name": "Audio Extr.", "sub": "16kHz Mono WAV", "x": 12.5, "w": 9.5, "col": "#38BDF8"},
        {"name": "Preprocess", "sub": "EBU R128 + VAD", "x": 23.5, "w": 9.5, "col": "#00B4D8"},
        {"name": "Whisper ASR", "sub": "Lang ID + Tokens", "x": 34.5, "w": 10.5, "col": "#06D6A0"},
        {"name": "Translation", "sub": "Optional Track", "x": 46.5, "w": 10.0, "col": "#10B981"},
        {"name": "Segmentation", "sub": "Clean & Sec. Split", "x": 58.0, "w": 11.5, "col": "#F59E0B"},
        {"name": "3 Summarizers", "sub": "TF-IDF / Graph / MMR", "x": 71.0, "w": 12.5, "col": "#EF4444"},
        {"name": "Delivery & UI", "sub": "Streamlit + PDF/TXT", "x": 85.0, "w": 13.5, "col": "#A855F7"}
    ]

    for s in steps:
        box = patches.FancyBboxPatch((s["x"], 32), s["w"], 40, boxstyle="round,pad=0.3,rounding_size=1.5",
                                     facecolor='#1E293B', edgecolor=s["col"], linewidth=2.0)
        ax.add_patch(box)
        ax.text(s["x"] + s["w"]/2, 57, s["name"], ha='center', va='center', fontsize=8.5, fontweight='bold', color='#FFFFFF')
        ax.text(s["x"] + s["w"]/2, 43, s["sub"], ha='center', va='center', fontsize=7.5, color=s["col"], fontweight='bold')

    # Draw arrows
    for i in range(len(steps) - 1):
        x1 = steps[i]["x"] + steps[i]["w"] + 0.3
        x2 = steps[i+1]["x"] - 0.3
        ax.annotate("", xy=(x2, 52), xytext=(x1, 52),
                    arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.4", lw=2, color='#94A3B8'))

    # Sub-box for legal boost novelty
    boost_box = patches.FancyBboxPatch((69.5, 12), 15.5, 14, boxstyle="round,pad=0.3,rounding_size=1",
                                      facecolor='#451A03', edgecolor='#F59E0B', linewidth=1.5)
    ax.add_patch(boost_box)
    ax.text(77.2, 21, "+ Legal Cue Boost", ha='center', va='center', fontsize=8, fontweight='bold', color='#F59E0B')
    ax.text(77.2, 16, "(2.5x Ruling / 0.85x Alleg.)", ha='center', va='center', fontsize=7, color='#FEF3C7')
    ax.annotate("", xy=(77.2, 32), xytext=(77.2, 26),
                arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.3", lw=1.5, color='#F59E0B'))

    # Bottom feature ribbon
    ax.text(50, 4, "Key Innovations: Verbatim Extractive • Microsecond Timestamps • Allegation Segregation • Real-Time Factor 0.049",
            ha='center', va='center', fontsize=8.5, color='#CBD5E1', style='italic')

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/architecture_clean.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Created architecture_clean.png")

# -------------------------------------------------------------
# 3. WORK PLAN & TIMELINE GANTT (SLIDE 13)
# -------------------------------------------------------------
def create_timeline_gantt():
    fig, ax = plt.subplots(figsize=(14, 5.8), dpi=300)
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#1E293B')

    phases = [
        "1. Problem Formulation & Setup",
        "2. Multilingual Dataset Collection",
        "3. Audio Extraction & Normalization",
        "4. Whisper ASR & Language ID",
        "5. Extractive Summarizers (3 Methods)",
        "6. Legal Domain Booster & Lexicon",
        "7. Evaluation & Ablation Experiments",
        "8. Web App, Live Demo & Final Report"
    ]

    # Weeks 1 to 12
    start_weeks = [1, 2, 3, 4, 6, 7, 9, 10]
    durations   = [2, 3, 2, 3, 3, 2, 2, 2]
    status      = ["DONE", "DONE", "DONE", "DONE", "CURRENT", "NEXT", "NEXT", "NEXT"]

    y_pos = np.arange(len(phases))

    for i, (p, s, d, stat) in enumerate(zip(phases, start_weeks, durations, status)):
        color = '#10B981' if stat == 'DONE' else ('#38BDF8' if stat == 'CURRENT' else '#475569')
        rect = ax.barh(i, d, left=s, height=0.55, align='center', color=color, edgecolor='#0F172A', linewidth=1.5)
        ax.text(s + d/2, i, stat, ha='center', va='center', color='#FFFFFF', fontsize=7.5, fontweight='bold')

    # Milestones Review 1, 2, 3
    ax.axvline(x=4.5, color='#F59E0B', linestyle='--', linewidth=2.5)
    ax.text(4.5, len(phases) - 0.2, "REVIEW 1\n(Weeks 1-4: Current)", ha='center', va='bottom', 
            fontsize=8.5, fontweight='bold', color='#F59E0B',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0F172A', edgecolor='#F59E0B'))

    ax.axvline(x=8.5, color='#38BDF8', linestyle=':', linewidth=2)
    ax.text(8.5, len(phases) - 0.2, "REVIEW 2\n(Weeks 5-8: Benchmarks)", ha='center', va='bottom', 
            fontsize=8, fontweight='bold', color='#38BDF8',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0F172A', edgecolor='#38BDF8'))

    ax.axvline(x=12.2, color='#A855F7', linestyle=':', linewidth=2)
    ax.text(12.2, len(phases) - 0.2, "REVIEW 3\n(Weeks 9-12: Final Demo)", ha='center', va='bottom', 
            fontsize=8, fontweight='bold', color='#A855F7',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0F172A', edgecolor='#A855F7'))

    ax.set_yticks(y_pos)
    ax.set_yticklabels(phases, color='#FFFFFF', fontsize=9, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlim(0.5, 14.5)
    ax.set_xlabel("Project Timeline (Weeks)", color='#94A3B8', fontsize=10, fontweight='bold')
    ax.set_xticks(range(1, 14))
    ax.set_xticklabels([f"W{w}" for w in range(1, 14)], color='#CBD5E1', fontsize=9)
    ax.tick_params(colors='#CBD5E1')
    ax.grid(axis='x', color='#334155', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/timeline_gantt.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Created timeline_gantt.png")

# -------------------------------------------------------------
# 4. SAMPLE INPUT / OUTPUT MOCKUP (BONUS REVIEW ITEM)
# -------------------------------------------------------------
def create_sample_input_output():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.8), dpi=300, facecolor='#0F172A')
    
    # Left: Input transcript with conversational density
    ax1.set_facecolor('#1E293B')
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax1.axis('off')
    
    # Container
    c1 = patches.FancyBboxPatch((2, 2), 96, 96, boxstyle="round,pad=0.4,rounding_size=1.5",
                                facecolor='#1E293B', edgecolor='#475569', linewidth=1.5)
    ax1.add_patch(c1)
    ax1.text(6, 90, "INPUT: RAW COURT TRANSCRIPT WITH TIMESTAMPS", fontsize=10.5, fontweight='bold', color='#38BDF8')
    ax1.text(6, 84, "Case: CASE_TE_02 (Naandhi Section 211 Court Scene, 336s)", fontsize=8, color='#94A3B8')

    lines_input = [
        ("[010.2s - 024.5s]", "Advocate submits the petition before the bench.", False),
        ("[025.1s - 045.0s]", "The petitioner contends illegal detention and torture.", False),
        ("[046.2s - 070.8s]", "Prosecution raises objections citing procedural rules.", False),
        ("[071.0s - 095.0s]", "Court orders departmental and criminal inquiry under Section 211 IPC.", True), # Selected
        ("[096.2s - 112.0s]", "Counsel explains procedural details of the inquiry.", False),
        ("[112.4s - 128.0s]", "Defense alleges evidence was fabricated by investigating officers.", True), # Selected
        ("[129.1s - 150.4s]", "Court records submission and directs compliance within 30 days.", True) # Selected
    ]
    
    y = 74
    for t_stamp, text, is_sel in lines_input:
        bg_col = '#064E3B' if is_sel else '#0F172A'
        border_col = '#10B981' if is_sel else '#334155'
        box = patches.FancyBboxPatch((5, y-2), 90, 8, boxstyle="round,pad=0.2,rounding_size=0.8",
                                     facecolor=bg_col, edgecolor=border_col, linewidth=1.2)
        ax1.add_patch(box)
        ax1.text(7, y+2, t_stamp, fontsize=7.5, fontweight='bold', color='#F59E0B' if is_sel else '#64748B')
        ax1.text(28, y+2, text[:48] + "...", fontsize=7.5, color='#FFFFFF' if is_sel else '#94A3B8')
        y -= 10.5

    # Right: Extractive Output with Badges & Jump Links
    ax2.set_facecolor('#1E293B')
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.axis('off')

    c2 = patches.FancyBboxPatch((2, 2), 96, 96, boxstyle="round,pad=0.4,rounding_size=1.5",
                                facecolor='#1E293B', edgecolor='#10B981', linewidth=1.8)
    ax2.add_patch(c2)
    ax2.text(6, 90, "OUTPUT: VERBATIM EXTRACTIVE SUMMARY (TOP 25%)", fontsize=10.5, fontweight='bold', color='#10B981')
    ax2.text(6, 84, "3 Highlighted Sentences • 100% Traceable • Zero Hallucination", fontsize=8, color='#A7F3D0')

    cards_out = [
        ("[071.0s - 095.0s]", "[JUDICIAL_RULING]", "#064E3B", "#10B981", 
         "\"The Court hereby orders a departmental and criminal inquiry under Section 211 against the investigating officers found guilty.\"", 62),
        ("[112.4s - 128.0s]", "[ADVOCATE_ALLEGATION]", "#451A03", "#F59E0B",
         "\"Defense counsel alleges evidence was fabricated by prosecution to falsely implicate the petitioner under false charges.\"", 38),
        ("[129.1s - 150.4s]", "[JUDICIAL_DIRECTION]", "#1E3A8A", "#38BDF8",
         "\"The High Court directs the Home Department to complete proceedings within 30 days and submit compliance report.\"", 14)
    ]

    for t_stamp, badge, bg, col, sent, y_box in cards_out:
        b_box = patches.FancyBboxPatch((5, y_box), 90, 20, boxstyle="round,pad=0.3,rounding_size=1",
                                      facecolor=bg, edgecolor=col, linewidth=1.5)
        ax2.add_patch(b_box)
        ax2.text(8, y_box + 14.5, badge, fontsize=7.5, fontweight='bold', color=col)
        ax2.text(45, y_box + 14.5, t_stamp + " [Jump to Video]", fontsize=7.5, fontweight='bold', color='#FFFFFF')
        ax2.text(8, y_box + 6.5, sent[:68], fontsize=7, color='#E2E8F0', style='italic')
        ax2.text(8, y_box + 2.0, sent[68:140], fontsize=7, color='#E2E8F0', style='italic')

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/sample_input_output.png', dpi=300, facecolor='#0F172A', edgecolor='none')
    plt.close()
    print("Created sample_input_output.png")

# -------------------------------------------------------------
# 5. TOOLS & TECHNOLOGIES GRID (SLIDE 11)
# -------------------------------------------------------------
def create_tools_grid():
    fig, ax = plt.subplots(figsize=(14, 5.8), dpi=300)
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    ax.text(50, 93, "TOOLS, FRAMEWORKS & SYSTEM TECHNOLOGIES", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#FFFFFF')

    tools = [
        ("Python 3.10+", "Core Language", "Type annotations, dataclasses, asyncio", "#38BDF8", 3, 50),
        ("FFmpeg", "Audio Demuxing", "16 kHz mono WAV conversion, EBU norm", "#00B4D8", 27.5, 50),
        ("faster-whisper", "Multilingual ASR", "CTranslate2 INT8, RTF = 0.049", "#06D6A0", 52, 50),
        ("sentence-transformers", "Vector Embeddings", "paraphrase-multilingual-MiniLM", "#10B981", 76.5, 50),
        
        ("scikit-learn & NetworkX", "Extractive NLP", "TF-IDF matrix & PageRank graphs", "#F59E0B", 3, 10),
        ("FastAPI", "Async Backend", "RESTful job queues & SQLite DB", "#EF4444", 27.5, 10),
        ("Streamlit", "Interactive UI", "Synchronized video & jump links", "#EC4899", 52, 10),
        ("Git & Google Colab", "Dev & Cloud GPU", "Turnkey GPU T4 testing & CI", "#A855F7", 76.5, 10),
    ]

    for title, role, desc, col, x, y in tools:
        box = patches.FancyBboxPatch((x, y), 20.5, 34, boxstyle="round,pad=0.4,rounding_size=1.5",
                                     facecolor='#1E293B', edgecolor=col, linewidth=1.8)
        ax.add_patch(box)
        ax.text(x + 10.2, y + 26, title, ha='center', va='center', fontsize=9, fontweight='bold', color='#FFFFFF')
        ax.text(x + 10.2, y + 17, role, ha='center', va='center', fontsize=7.5, fontweight='bold', color=col)
        ax.text(x + 10.2, y + 8, desc, ha='center', va='center', fontsize=6.8, color='#94A3B8')

    plt.tight_layout()
    plt.savefig('reports/presentation_assets/tools_grid.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Created tools_grid.png")

if __name__ == '__main__':
    create_vit_logo()
    create_clean_architecture()
    create_timeline_gantt()
    create_sample_input_output()
    create_tools_grid()
    print("All review assets generated successfully!")
