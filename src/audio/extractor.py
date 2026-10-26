"""Audio Extraction Module for Court Video Assets.

Converts arbitrary video formats (MP4, MKV, AVI, MOV) into standardized
16 kHz mono uncompressed WAV (PCM 16-bit) using FFmpeg, with strict validation
and corrupt-file error handling.
"""

import os
import sys
import json
import logging
import subprocess
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, List

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AudioExtractor")


def extract_audio(
    video_path: str,
    output_wav_path: str,
    sample_rate: int = 16000,
    channels: int = 1
) -> Dict[str, Any]:
    """Extract standard mono WAV audio stream from a court video file via FFmpeg.

    Args:
        video_path: Path to input video file.
        output_wav_path: Target path for the extracted .wav file.
        sample_rate: Desired sampling rate in Hz (default: 16000 for Whisper ASR).
        channels: Desired audio channels (default: 1 for mono).

    Returns:
        Dict containing extraction status, output path, duration, file size, and metrics.
    """
    vpath = Path(video_path)
    out_path = Path(output_wav_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not vpath.exists():
        return {
            "status": "failed",
            "error": f"Input video file not found: {video_path}",
            "file": str(vpath)
        }

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(vpath),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", str(channels),
        str(out_path)
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
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg extraction failed for {video_path}: {e.stderr[:200]}")
        return {
            "status": "failed",
            "error": f"FFmpeg extraction error: {e.stderr[:200]}",
            "file": str(vpath)
        }

    validation = validate_audio_file(str(out_path), expected_sr=sample_rate, expected_ch=channels)
    return {
        "status": "success" if validation["is_valid"] else "failed",
        "input_video": str(vpath),
        "output_wav": str(out_path),
        "duration_sec": validation["duration_sec"],
        "size_kb": validation["size_kb"],
        "sample_rate_hz": validation["sample_rate_hz"],
        "channels": validation["channels"],
        "rms_db": validation["rms_db"],
        "peak_db": validation["peak_db"],
        "is_silent": validation["is_silent"],
        "validation_details": validation
    }


def validate_audio_file(
    wav_path: str,
    expected_sr: int = 16000,
    expected_ch: int = 1,
    silence_threshold_db: float = -60.0
) -> Dict[str, Any]:
    """Validate extracted WAV audio using soundfile and exact mathematical signal statistics."""
    p = Path(wav_path)
    if not p.exists() or p.stat().st_size == 0:
        return {
            "is_valid": False,
            "error": "File does not exist or has zero size",
            "duration_sec": 0.0,
            "size_kb": 0.0,
            "sample_rate_hz": 0,
            "channels": 0,
            "rms_db": -100.0,
            "peak_db": -100.0,
            "is_silent": True
        }

    size_kb = round(p.stat().st_size / 1024, 2)

    try:
        # Read audio waveform directly with soundfile
        data, sr = sf.read(str(p), dtype="float32")
        ch = 1 if data.ndim == 1 else data.shape[1]
        num_frames = len(data) if data.ndim == 1 else data.shape[0]
        duration_sec = round(num_frames / sr, 2)

        # Compute Signal Statistics
        if data.size == 0:
            return {
                "is_valid": False,
                "error": "Empty audio buffer",
                "duration_sec": 0.0,
                "size_kb": size_kb,
                "sample_rate_hz": sr,
                "channels": ch,
                "rms_db": -100.0,
                "peak_db": -100.0,
                "is_silent": True
            }

        rms = np.sqrt(np.mean(np.square(data)))
        peak = np.max(np.abs(data))

        rms_db = round(float(20 * np.log10(rms + 1e-9)), 2)
        peak_db = round(float(20 * np.log10(peak + 1e-9)), 2)

        is_silent = (rms_db < silence_threshold_db)
        is_valid = (sr == expected_sr and ch == expected_ch and duration_sec > 0.5 and not is_silent)

        return {
            "is_valid": is_valid,
            "duration_sec": duration_sec,
            "size_kb": size_kb,
            "sample_rate_hz": sr,
            "channels": ch,
            "rms_db": rms_db,
            "peak_db": peak_db,
            "is_silent": is_silent
        }
    except Exception as e:
        logger.error(f"Validation exception on {wav_path}: {e}")
        return {
            "is_valid": False,
            "error": str(e),
            "duration_sec": 0.0,
            "size_kb": size_kb,
            "sample_rate_hz": 0,
            "channels": 0,
            "rms_db": -100.0,
            "peak_db": -100.0,
            "is_silent": True
        }


def batch_extract_dataset(
    video_dir: str = "Dataset",
    output_dir: str = "data/extracted_audio"
) -> List[Dict[str, Any]]:
    """Extract WAV audio from all video files in directory and generate validation report."""
    vdir = Path(video_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    supported_extensions = {".mp4", ".mkv", ".avi", ".mov", ".webm"}

    for idx, f in enumerate(sorted(vdir.iterdir()), 1):
        if f.suffix.lower() in supported_extensions:
            # Map to clean case-indexed name while keeping original stem
            safe_name = f"CASE_{idx:02d}_{f.stem[:30].strip()}".replace(" ", "_").replace("(", "").replace(")", "").replace("@", "")
            safe_wav_name = f"{safe_name}.wav"
            out_wav = out_dir / safe_wav_name
            logger.info(f"Extracting [{idx}/10]: {f.name[:35]}... -> {safe_wav_name}")
            res = extract_audio(str(f), str(out_wav))
            results.append(res)

    report_path = out_dir / "extraction_validation_report.json"
    with open(report_path, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)

    logger.info(f"Batch extraction complete. Validation report saved to {report_path}")
    return results


if __name__ == "__main__":
    print("Executing Phase 2: Video-to-Audio Extraction...")
    results = batch_extract_dataset()
    print("\n" + "=" * 80)
    print("EXTRACTION AND AUDIO QUALITY VALIDATION SUMMARY")
    print("=" * 80)
    for r in results:
        status_sym = "[OK]" if r["status"] == "success" else "[FAIL]"
        base_name = Path(r['output_wav']).name
        print(f"{status_sym} {base_name:<42} | Dur: {r['duration_sec']:>6.1f}s | RMS: {r['rms_db']:>6.1f} dB | Peak: {r['peak_db']:>5.1f} dB")
    print("=" * 80)
