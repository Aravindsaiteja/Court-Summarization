"""Multilingual Speech Recognition Module for Court Proceedings.

Utilizes faster-whisper (CTranslate2) with fallback to openai-whisper.
Performs automatic language detection with confidence scoring, timestamped
segmentation, and dual-track transcription / translation.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CourtTranscriber")


class CourtTranscriber:
    """Multilingual courtroom speech recognition engine."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "auto",
        beam_size: int = 5
    ):
        """Initialize the speech recognition model.

        Args:
            model_size: Model capacity ('tiny', 'base', 'small', 'medium', 'large-v3').
            device: 'cpu', 'cuda', or 'auto'.
            compute_type: 'int8', 'float16', 'int8_float16', or 'auto'.
            beam_size: Beam search width (default: 5).
        """
        self.model_size = model_size
        self.beam_size = beam_size

        if device == "auto":
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except Exception:
                self.device = "cpu"
        else:
            self.device = device

        if compute_type == "auto":
            self.compute_type = "float16" if self.device == "cuda" else "int8"
        else:
            self.compute_type = compute_type

        self.model = None
        self._load_model()

    def _load_model(self):
        """Load faster-whisper model."""
        try:
            from faster_whisper import WhisperModel
            logger.info(f"Loading faster-whisper [{self.model_size}] on {self.device} ({self.compute_type})...")
            t0 = time.time()
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info(f"Loaded faster-whisper [{self.model_size}] in {time.time()-t0:.2f}s")
            self.backend = "faster-whisper"
        except Exception as e:
            logger.warning(f"Could not load faster-whisper: {e}. Falling back to openai-whisper...")
            import whisper
            self.model = whisper.load_model(self.model_size, device=self.device)
            self.backend = "openai-whisper"

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        initial_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribe an audio file into timestamped segments with language detection.

        Args:
            audio_path: Path to 16 kHz mono WAV audio file.
            language: Optional language ISO code ('en', 'hi', 'te', 'ta'). If None, auto-detected.
            task: 'transcribe' (native language) or 'translate' (translated to English).
            initial_prompt: Optional domain prompt to bias ASR toward legal jargon.

        Returns:
            Dict containing full text, detected language, confidence, and timestamped segments.
        """
        p = Path(audio_path)
        if not p.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        default_legal_prompt = (
            "Court proceeding. Supreme Court, High Court, trial, witness testimony, "
            "cross-examination, prosecution, defense counsel, bail, Section, IPC, CrPC, "
            "verdict, objection sustained, overruled, affidavit, exhibit, forensic evidence."
        )
        prompt = initial_prompt or default_legal_prompt

        t0 = time.time()

        if self.backend == "faster-whisper":
            segments_gen, info = self.model.transcribe(
                str(p),
                language=language,
                task=task,
                beam_size=self.beam_size,
                initial_prompt=prompt,
                condition_on_previous_text=False,  # Prevents repetition loops
                vad_filter=True,                   # Uses Silero VAD to skip dead silence
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            detected_lang = info.language
            lang_prob = round(info.language_probability, 4)
            audio_duration = round(info.duration, 2)

            segments = []
            full_text_parts = []
            for s in segments_gen:
                seg_dict = {
                    "id": s.id,
                    "start": round(s.start, 2),
                    "end": round(s.end, 2),
                    "text": s.text.strip(),
                    "avg_logprob": round(s.avg_logprob, 3),
                    "no_speech_prob": round(s.no_speech_prob, 3)
                }
                segments.append(seg_dict)
                full_text_parts.append(s.text.strip())

            full_text = " ".join(full_text_parts)

        else:
            # openai-whisper fallback
            result = self.model.transcribe(
                str(p),
                language=language,
                task=task,
                initial_prompt=prompt,
                beam_size=self.beam_size,
                condition_on_previous_text=False
            )
            detected_lang = result.get("language", "unknown")
            lang_prob = 1.0  # openai-whisper doesn't return scalar prob directly
            audio_duration = 0.0

            segments = []
            for s in result.get("segments", []):
                segments.append({
                    "id": s.get("id"),
                    "start": round(s.get("start", 0.0), 2),
                    "end": round(s.get("end", 0.0), 2),
                    "text": s.get("text", "").strip(),
                    "avg_logprob": round(s.get("avg_logprob", 0.0), 3),
                    "no_speech_prob": round(s.get("no_speech_prob", 0.0), 3)
                })
            full_text = result.get("text", "").strip()

        elapsed = round(time.time() - t0, 2)
        rtf = round(elapsed / max(0.1, audio_duration), 3) if audio_duration > 0 else 0.0

        return {
            "audio_file": str(p),
            "backend": self.backend,
            "model_size": self.model_size,
            "task": task,
            "detected_language": detected_lang,
            "language_confidence": lang_prob,
            "duration_sec": audio_duration,
            "transcription_time_sec": elapsed,
            "real_time_factor": rtf,
            "full_transcript": full_text,
            "segment_count": len(segments),
            "segments": segments
        }

    def save_transcript(self, result: Dict[str, Any], output_json_path: str, output_txt_path: Optional[str] = None):
        """Export transcription results to JSON and TXT formats."""
        jp = Path(output_json_path)
        jp.parent.mkdir(parents=True, exist_ok=True)

        with open(jp, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if output_txt_path:
            tp = Path(output_txt_path)
            tp.parent.mkdir(parents=True, exist_ok=True)
            with open(tp, "w", encoding="utf-8") as f:
                f.write(f"--- COURT PROCEEDING TRANSCRIPT ---\n")
                f.write(f"File: {Path(result['audio_file']).name}\n")
                f.write(f"Language: {result['detected_language']} (Confidence: {result['language_confidence']*100:.1f}%)\n")
                f.write(f"Duration: {result['duration_sec']}s | Inference Time: {result['transcription_time_sec']}s (RTF: {result['real_time_factor']})\n")
                f.write("=" * 60 + "\n\n")
                for s in result["segments"]:
                    f.write(f"[{s['start']:06.2f}s -> {s['end']:06.2f}s]  {s['text']}\n")


if __name__ == "__main__":
    print("Testing CourtTranscriber...")
    transcriber = CourtTranscriber(model_size="base")
    sample_wav = Path("data/extracted_audio/CASE_01_5_Movie_CLIP_-_Automotive_Exp.wav")
    if sample_wav.exists():
        res = transcriber.transcribe(str(sample_wav))
        print(f"Detected: {res['detected_language']} (Conf: {res['language_confidence']})")
        print(f"Time: {res['transcription_time_sec']}s (RTF: {res['real_time_factor']})")
        print(f"Segments: {res['segment_count']}")
        print(f"Sample: {res['full_transcript'][:180]}...")
