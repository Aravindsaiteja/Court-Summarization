"""Dataset Inventory and Validation Module for Court Proceeding Summarization System.

Performs static analysis of multimedia assets, metadata extraction,
and dev/test partitioning.
"""

import os
import sys
import json
import csv
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Ensure UTF-8 output encoding across platforms
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def inspect_media_file(fpath: Path) -> Dict[str, Any]:
    """Run ffprobe to extract audio and video stream metadata."""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(fpath)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        info = json.loads(res.stdout)
        dur = round(float(info.get('format', {}).get('duration', 0)), 2)
        v_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), None)
        a_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'audio'), None)

        width = v_stream.get('width', 0) if v_stream else 0
        height = v_stream.get('height', 0) if v_stream else 0
        v_codec = v_stream.get('codec_name', 'none') if v_stream else 'none'
        a_codec = a_stream.get('codec_name', 'none') if a_stream else 'none'
        sr = a_stream.get('sample_rate', '0') if a_stream else '0'
        channels = a_stream.get('channels', 0) if a_stream else 0
        return {
            'duration_sec': dur,
            'resolution': f"{width}x{height}",
            'video_codec': v_codec,
            'audio_codec': a_codec,
            'sample_rate_hz': int(sr),
            'channels': int(channels),
            'is_valid': (dur > 0 and a_stream is not None)
        }
    except Exception as e:
        return {
            'duration_sec': 0.0,
            'resolution': '0x0',
            'video_codec': 'error',
            'audio_codec': 'error',
            'sample_rate_hz': 0,
            'channels': 0,
            'is_valid': False,
            'error': str(e)
        }


def build_inventory(dataset_dir: str = 'Dataset', output_csv: str = 'data/dataset_inventory.csv') -> List[Dict[str, Any]]:
    """Scan dataset directory, extract stream metadata, and generate inventory CSV."""
    dpath = Path(dataset_dir)
    if not dpath.exists():
        raise FileNotFoundError(f"Dataset directory '{dataset_dir}' not found.")

    files = sorted(os.listdir(dpath))
    records = []

    for idx, fname in enumerate(files, 1):
        fpath = dpath / fname
        if not fpath.is_file():
            continue

        sz_mb = round(os.path.getsize(fpath) / (1024 * 1024), 2)
        meta = inspect_media_file(fpath)

        lower_name = fname.lower()
        if 'automotive expert' in lower_name:
            case_id = 'CASE_EN_01'
            lang = 'English'
            source = 'My Cousin Vinny (1992)'
            speakers = 'Defense Lawyer, Expert Witness, Judge, Prosecutor'
            quality = 'Clean Studio Speech'
            code_switch = 'No'
            split = 'Dev'
        elif 'friendship' in lower_name:
            case_id = 'CASE_TE_01'
            lang = 'Telugu'
            source = 'Friendship (2022)'
            speakers = 'Defense Counsel, Judge, Accused, Public'
            quality = 'Moderate BG Score, High Dynamism'
            code_switch = 'Yes (Telugu-English Legal Terms)'
            split = 'Test'
        elif 'law abiding citizen' in lower_name:
            case_id = 'CASE_EN_02'
            lang = 'English'
            source = 'Law Abiding Citizen (2009)'
            speakers = 'Judge Laura Burch, Defendant Clyde Shelton, Prosecutor'
            quality = 'Clean Studio Speech'
            code_switch = 'No'
            split = 'Dev'
        elif 'parasakthi' in lower_name and '480p' not in lower_name:
            case_id = 'CASE_TA_01'
            lang = 'Tamil'
            source = 'Parasakthi (1952 Classic Court Monologue)'
            speakers = 'Gunasekaran (Defendant), Judge'
            quality = 'Historical Audio (Reverberant Mono)'
            code_switch = 'No (Pure Dravidian Tamil Rhetoric)'
            split = 'Dev'
        elif 'this-cross-examination-flipped' in lower_name or 'state-vs-a-nobody' in lower_name:
            case_id = 'CASE_HI_EN_01'
            lang = 'Hindi / English'
            source = 'Court / Legal Drama (State vs A Nobody)'
            speakers = 'Prosecutor, Defense Counsel, Judge, Witness'
            quality = 'Realistic Courtroom Acoustics'
            code_switch = 'High (Hindi with English Legal Terminology)'
            split = 'Test'
        elif 'legally-blonde' in lower_name:
            case_id = 'CASE_EN_03'
            lang = 'English'
            source = 'Legally Blonde (2001)'
            speakers = 'Elle Woods (Counsel), Witness Chutney, Judge'
            quality = 'Clean Studio Speech'
            code_switch = 'No'
            split = 'Test'
        elif 'madhav-mishra' in lower_name:
            case_id = 'CASE_HI_01'
            lang = 'Hindi'
            source = 'Criminal Justice S3 (Madhav Mishra)'
            speakers = 'Advocate Madhav Mishra, Opposing Counsel, Judge'
            quality = 'Clean Studio Speech'
            code_switch = 'Moderate (Hindi-English Legal Jargon)'
            split = 'Dev'
        elif 'parasakthi' in lower_name and '480p' in lower_name:
            case_id = 'CASE_TA_02'
            lang = 'Tamil'
            source = 'Parasakthi (1952 Alternate Resolution 480p)'
            speakers = 'Gunasekaran (Defendant), Judge'
            quality = 'Compressed Historical Mono'
            code_switch = 'No'
            split = 'Test'
        elif 'naandhi' in lower_name:
            case_id = 'CASE_TE_02'
            lang = 'Telugu'
            source = 'Naandhi (2021 Section 211 IPC Case)'
            speakers = 'Advocate Aadhya, Police Officer, Judge'
            quality = 'Dramatic Background Score, Clear Speech'
            code_switch = 'Moderate (Telugu + IPC Provisions)'
            split = 'Test'
        elif 'dj tillu' in lower_name or 'ఈ court scene' in lower_name:
            case_id = 'CASE_TE_03'
            lang = 'Telugu'
            source = 'DJ Tillu (2022 Court Scene)'
            speakers = 'DJ Tillu, Public Prosecutor, Judge'
            quality = 'Conversational, Fast Speech, Slang'
            code_switch = 'High (Telugu Dialect + English Terms)'
            split = 'Dev'
        else:
            case_id = f'CASE_UNK_{idx:02d}'
            lang = 'Multilingual'
            source = fname
            speakers = 'Court Participants'
            quality = 'Unknown'
            code_switch = 'Unknown'
            split = 'Dev'

        record = {
            'Case_ID': case_id,
            'Original_Filename': fname,
            'Source_Title': source,
            'Primary_Language': lang,
            'Duration_Sec': meta['duration_sec'],
            'Size_MB': sz_mb,
            'Video_Resolution': meta['resolution'],
            'Audio_Codec': meta['audio_codec'],
            'Sample_Rate_Hz': meta['sample_rate_hz'],
            'Audio_Channels': meta['channels'],
            'Audio_Quality': quality,
            'Code_Switching': code_switch,
            'Speakers': speakers,
            'Split': split,
            'Is_Valid': meta['is_valid']
        }
        records.append(record)

    out_p = Path(output_csv)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    return records


if __name__ == '__main__':
    print("=" * 70)
    print("PHASE 1: DATASET INVENTORY AND MULTIMEDIA VALIDATION")
    print("=" * 70)
    records = build_inventory()
    print(f"Total files cataloged: {len(records)}\n")
    for r in records:
        print(f"[{r['Case_ID']}] {r['Primary_Language']:<16} | {r['Duration_Sec']:>6.1f}s | {r['Split']:<4} | {r['Source_Title']}")
    print("=" * 70)
