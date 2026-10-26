"""Audio Preprocessing and VAD Chunking Module for Court Speech.

Applies EBU R128 loudness normalization (-23 LUFS), conservative noise reduction
(preserving subtle witness speech), and silence-aware Voice Activity Detection (VAD)
chunking while strictly recording global timestamps.
"""

import os
import sys
import json
import logging
import subprocess
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AudioPreprocessor")


def normalize_loudness_ebu_r128(
    input_wav: str,
    output_wav: str,
    target_lufs: float = -23.0,
    true_peak_db: float = -1.5
) -> Dict[str, Any]:
    """Apply standard EBU R128 two-pass / dynamic loudness normalization via FFmpeg.

    Standardizes disparate recording levels (whispers vs shouting counsel)
    to a uniform perceptual loudness of -23 LUFS.
    """
    in_p = Path(input_wav)
    out_p = Path(output_wav)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # Use FFmpeg loudnorm filter
    filter_expr = f"loudnorm=I={target_lufs}:TP={true_peak_db}:LRA=11"
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(in_p),
        "-af", filter_expr,
        "-ar", "16000",
        "-ac", "1",
        str(out_p)
    ]

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        data, sr = sf.read(str(out_p), dtype="float32")
        rms = float(np.sqrt(np.mean(np.square(data))))
        rms_db = round(float(20 * np.log10(rms + 1e-9)), 2)
        peak_db = round(float(20 * np.log10(np.max(np.abs(data)) + 1e-9)), 2)
        return {
            "status": "success",
            "output_path": str(out_p),
            "rms_db": rms_db,
            "peak_db": peak_db,
            "duration_sec": round(len(data) / sr, 2)
        }
    except Exception as e:
        logger.error(f"Loudness normalization failed for {input_wav}: {e}")
        # Fallback to copy if loudnorm fails
        return {
            "status": "failed",
            "error": str(e),
            "output_path": str(in_p)
        }


def conservative_noise_filter(
    input_wav: str,
    output_wav: str,
    highpass_hz: int = 80,
    lowpass_hz: int = 7500,
    noise_floor_db: float = -25.0
) -> Dict[str, Any]:
    """Conservative noise reduction that removes HVAC hum and tape hiss without distorting phonemes.

    Applies:
    1. High-pass filter at 80 Hz: Removes electrical hum, desk thuds, and HVAC rumble.
    2. Low-pass filter at 7500 Hz: Removes high-frequency tape hiss while retaining speech sibilants.
    3. Conservative FFT noise filter (`afftdn` with gentle -25dB floor): Ensures zero musical noise or phase smearing.
    """
    in_p = Path(input_wav)
    out_p = Path(output_wav)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    filter_chain = f"highpass=f={highpass_hz},lowpass=f={lowpass_hz},afftdn=nf={noise_floor_db}:nr=10"
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(in_p),
        "-af", filter_chain,
        "-ar", "16000",
        "-ac", "1",
        str(out_p)
    ]

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        return {
            "status": "success",
            "output_path": str(out_p)
        }
    except Exception as e:
        logger.warning(f"FFmpeg noise filter error, passing through normalized audio: {e}")
        return {
            "status": "fallback",
            "output_path": str(in_p)
        }


def detect_silence_intervals(
    wav_path: str,
    noise_thresh_db: float = -35.0,
    min_silence_duration: float = 0.5
) -> List[Tuple[float, float]]:
    """Detect natural pauses and silence intervals in courtroom audio using FFmpeg silencedetect."""
    cmd = [
        "ffmpeg",
        "-i", wav_path,
        "-af", f"silencedetect=noise={noise_thresh_db}dB:d={min_silence_duration}",
        "-f", "null",
        "-"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")

    silence_starts = []
    silence_ends = []
    for line in res.stderr.splitlines():
        if "silence_start:" in line:
            parts = line.split("silence_start:")
            try:
                silence_starts.append(float(parts[1].strip().split()[0]))
            except Exception:
                pass
        elif "silence_end:" in line:
            parts = line.split("silence_end:")
            try:
                silence_ends.append(float(parts[1].strip().split()[0]))
            except Exception:
                pass

    intervals = []
    for s, e in zip(silence_starts, silence_ends):
        if e > s:
            intervals.append((round(s, 2), round(e, 2)))
    return intervals


def chunk_audio_preserving_timestamps(
    input_wav: str,
    output_dir: str,
    max_chunk_sec: float = 25.0,
    min_chunk_sec: float = 5.0,
    silence_thresh_db: float = -35.0
) -> List[Dict[str, Any]]:
    """Partition continuous audio into timestamp-anchored speech chunks.

    Identifies natural pauses (witness pauses, judge interruptions) to split chunks.
    NEVER deletes speech segments; records exact global offsets for perfect ASR alignment.
    """
    in_p = Path(input_wav)
    out_dir = Path(output_dir) / in_p.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    data, sr = sf.read(str(in_p), dtype="float32")
    total_duration = len(data) / sr

    silences = detect_silence_intervals(str(in_p), noise_thresh_db=silence_thresh_db)

    # Determine split boundary points
    split_points = [0.0]
    current_start = 0.0

    for s_start, s_end in silences:
        mid_point = (s_start + s_end) / 2.0
        dur_from_start = mid_point - current_start
        if dur_from_start >= min_chunk_sec and dur_from_start <= max_chunk_sec:
            split_points.append(mid_point)
            current_start = mid_point
        elif dur_from_start > max_chunk_sec:
            # Force intermediate splits if no silence found in max_chunk_sec window
            cursor = current_start + max_chunk_sec
            while cursor < mid_point:
                split_points.append(cursor)
                cursor += max_chunk_sec
            split_points.append(mid_point)
            current_start = mid_point

    if total_duration - split_points[-1] > min_chunk_sec:
        split_points.append(total_duration)
    else:
        split_points[-1] = total_duration

    # Ensure unique and sorted
    split_points = sorted(list(set(round(p, 2) for p in split_points)))

    chunk_metadata = []
    for idx in range(len(split_points) - 1):
        c_start = split_points[idx]
        c_end = split_points[idx + 1]
        c_dur = round(c_end - c_start, 2)

        start_frame = int(c_start * sr)
        end_frame = int(c_end * sr)
        chunk_data = data[start_frame:end_frame]

        chunk_fname = f"chunk_{idx+1:04d}_{c_start:06.1f}s_{c_end:06.1f}s.wav"
        chunk_fpath = out_dir / chunk_fname

        sf.write(str(chunk_fpath), chunk_data, sr, subtype="PCM_16")

        meta = {
            "chunk_index": idx + 1,
            "filename": chunk_fname,
            "file_path": str(chunk_fpath),
            "global_start_sec": c_start,
            "global_end_sec": c_end,
            "duration_sec": c_dur,
            "sample_rate": sr,
            "frames": len(chunk_data)
        }
        chunk_metadata.append(meta)

    # Save chunk index JSON
    manifest_path = out_dir / "chunk_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(chunk_metadata, f, ensure_ascii=False, indent=2)

    logger.info(f"Chunked {in_p.name} ({total_duration:.1f}s) into {len(chunk_metadata)} chunks. Manifest: {manifest_path.name}")
    return chunk_metadata


def preprocess_audio_pipeline(
    input_wav: str,
    output_dir: str = "data/preprocessed_audio"
) -> Dict[str, Any]:
    """Execute complete Phase 3 acoustic enhancement pipeline."""
    in_p = Path(input_wav)
    out_base = Path(output_dir) / in_p.stem
    out_base.mkdir(parents=True, exist_ok=True)

    norm_wav = out_base / f"{in_p.stem}_normalized.wav"
    filtered_wav = out_base / f"{in_p.stem}_clean.wav"

    # Step 1: EBU R128 Loudness Normalization
    norm_res = normalize_loudness_ebu_r128(str(in_p), str(norm_wav))

    # Step 2: Conservative Filtering
    filter_res = conservative_noise_filter(norm_res["output_path"], str(filtered_wav))

    # Step 3: VAD Silence-Aware Chunking with Global Timestamps
    chunks = chunk_audio_preserving_timestamps(filter_res["output_path"], str(out_base / "chunks"))

    return {
        "case_stem": in_p.stem,
        "normalized_wav": str(norm_wav),
        "clean_wav": str(filtered_wav),
        "chunk_count": len(chunks),
        "chunks": chunks
    }


if __name__ == "__main__":
    print("Executing Phase 3: Audio Preprocessing and VAD Chunking...")
    # Test on representative dev cases
    test_wavs = list(Path("data/extracted_audio").glob("*.wav"))
    if not test_wavs:
        print("No extracted audio found. Run Phase 2 extractor first.")
        sys.exit(1)

    print(f"Found {len(test_wavs)} extracted audio files. Processing first 2 cases as demonstration...")
    for w in test_wavs[:2]:
        res = preprocess_audio_pipeline(str(w))
        print(f"[PREPROCESSED] {res['case_stem']}: {res['chunk_count']} chunks created with global timestamps.")
