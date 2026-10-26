"""Master Pipeline Orchestrator for Real-Time Multilingual Court Proceeding Summarizer.

Executes end-to-end pipeline:
Video -> 16kHz WAV -> Preprocessing -> Whisper ASR -> Legal Cleaning ->
Sentence Segmentation -> (Optional Translation) -> Extractive Summarizer ->
Legal Domain Salience Booster -> Multi-format Traceable Export (TXT / JSON / PDF).
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CourtPipeline")

from src.audio.extractor import extract_audio
from src.audio.preprocessor import normalize_loudness_ebu_r128, conservative_noise_filter
from src.asr.transcriber import CourtTranscriber
from src.preprocessing.cleaner import TranscriptCleaner
from src.preprocessing.segmenter import LegalSentenceSegmenter
from src.translation.translator import CourtTranslator
from src.summarization.base import BaseSummarizer
from src.summarization.tfidf_summarizer import TfidfCourtSummarizer
from src.summarization.textrank_summarizer import TextRankCourtSummarizer
from src.summarization.embedding_summarizer import MultilingualEmbeddingSummarizer
from src.summarization.legal_enhancer import LegalDomainEnhancer


class CourtProceedingSummarizationPipeline:
    """Turnkey end-to-end pipeline for multilingual courtroom speech summarization."""

    def __init__(
        self,
        asr_model_size: str = "tiny",
        default_summarizer: str = "textrank",
        legal_boost_enabled: bool = True,
        output_dir: str = "outputs"
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.legal_boost_enabled = legal_boost_enabled
        self.default_summarizer_name = default_summarizer

        # Initialize core components
        logger.info(f"Initializing pipeline components (ASR Model: {asr_model_size})...")
        self.transcriber = CourtTranscriber(model_size=asr_model_size)
        self.cleaner = TranscriptCleaner()
        self.segmenter = LegalSentenceSegmenter(cleaner=self.cleaner)
        self.translator = CourtTranslator()
        self.enhancer = LegalDomainEnhancer()

        # Initialize summarizer algorithms
        self.summarizers = {
            "tfidf": TfidfCourtSummarizer(),
            "textrank": TextRankCourtSummarizer(),
            "embedding": MultilingualEmbeddingSummarizer()
        }

    def run(
        self,
        media_path: str,
        method: Optional[str] = None,
        summary_ratio: float = 0.25,
        enable_translation: bool = True,
        case_id: Optional[str] = None,
        judicial_only: bool = True
    ) -> Dict[str, Any]:
        """Execute the complete pipeline on a single court recording.

        Args:
            media_path: Path to video (.mp4, .mkv) or audio (.wav) file.
            method: 'tfidf', 'textrank', or 'embedding'.
            summary_ratio: Extractive compression ratio (0.15 to 0.50).
            enable_translation: Whether to generate parallel English translation.
            case_id: Optional tracking identifier.
            judicial_only: Whether to strictly prioritize post-hearing judicial rulings & judgments.

        Returns:
            Dict containing complete structured transcript, extractive summary, and execution metrics.
        """
        start_total = time.time()
        stage_timings = {}
        input_p = Path(media_path)
        stem = case_id or input_p.stem

        logger.info(f"=== Starting Pipeline for [{stem}] ===")

        # --- Stage 1: Audio Extraction ---
        t0 = time.time()
        if input_p.suffix.lower() == ".wav":
            working_wav = str(input_p)
            stage_timings["audio_extraction_ms"] = 0
        else:
            extracted_wav = self.output_dir / "temp_audio" / f"{stem}_16k.wav"
            extracted_wav.parent.mkdir(parents=True, exist_ok=True)
            res_ext = extract_audio(str(input_p), str(extracted_wav))
            if res_ext["status"] != "success":
                raise RuntimeError(f"Audio extraction failed: {res_ext.get('error')}")
            working_wav = str(extracted_wav)
            stage_timings["audio_extraction_ms"] = round((time.time() - t0) * 1000, 2)

        # --- Stage 2: Acoustic Normalization & Filtering ---
        t0 = time.time()
        norm_wav = self.output_dir / "temp_audio" / f"{stem}_norm.wav"
        clean_wav = self.output_dir / "temp_audio" / f"{stem}_clean.wav"
        normalize_loudness_ebu_r128(working_wav, str(norm_wav))
        conservative_noise_filter(str(norm_wav), str(clean_wav))
        stage_timings["acoustic_preprocessing_ms"] = round((time.time() - t0) * 1000, 2)

        # --- Stage 3: Multilingual ASR ---
        t0 = time.time()
        asr_result = self.transcriber.transcribe(str(clean_wav), task="transcribe")
        stage_timings["asr_transcription_ms"] = round((time.time() - t0) * 1000, 2)
        detected_lang = asr_result["detected_language"]
        lang_conf = asr_result["language_confidence"]

        # --- Stage 4: Cleaning & Boundary-Aware Segmentation ---
        t0 = time.time()
        raw_segments = asr_result["segments"]
        sentences = self.segmenter.segment_transcript(raw_segments)
        stage_timings["cleaning_and_segmentation_ms"] = round((time.time() - t0) * 1000, 2)

        # --- Stage 5: Optional Sentence-Aligned Translation ---
        t0 = time.time()
        if enable_translation and detected_lang != "en":
            # Direct Whisper translation pass
            trans_result = self.transcriber.transcribe(str(clean_wav), task="translate")
            aligned_sentences = self.translator.align_and_translate_sentences(
                sentences,
                source_lang=detected_lang,
                whisper_translated_segments=trans_result["segments"]
            )
        else:
            aligned_sentences = self.translator.align_and_translate_sentences(
                sentences,
                source_lang=detected_lang
            )
        stage_timings["translation_alignment_ms"] = round((time.time() - t0) * 1000, 2)

        # --- Stage 6: Extractive Summarization & Legal Boosting ---
        t0 = time.time()
        chosen_method = (method or self.default_summarizer_name).lower()
        summarizer = self.summarizers.get(chosen_method, self.summarizers["textrank"])

        # Compute base algorithmic scores
        base_scores = summarizer.score_sentences(aligned_sentences)

        # Apply Legal Salience Enhancement
        if self.legal_boost_enabled:
            boosted_scores, enriched_sentences = self.enhancer.boost_sentence_scores(
                aligned_sentences,
                base_scores,
                language=detected_lang
            )
            final_scores = boosted_scores
            candidate_sentences = enriched_sentences
        else:
            final_scores = base_scores
            candidate_sentences = aligned_sentences

        # Select Top-K with judicial ruling focus and non-repetition
        total_s = len(candidate_sentences)
        min_k = 1 if judicial_only else 3
        k = max(min_k, int(round(total_s * summary_ratio)))
        k = min(k, 8, total_s)

        summary_sentences = BaseSummarizer.select_extractive_summary(
            candidate_sentences,
            final_scores,
            k=k,
            diversity_threshold=0.45,
            judicial_only=judicial_only
        )

        stage_timings["summarization_ms"] = round((time.time() - t0) * 1000, 2)
        total_time_ms = round((time.time() - start_total) * 1000, 2)

        # Assemble Master Result
        final_output = {
            "case_id": stem,
            "media_path": str(input_p),
            "media_type": input_p.suffix.lower(),
            "detected_language": detected_lang,
            "language_confidence": lang_conf,
            "audio_duration_sec": asr_result["duration_sec"],
            "total_transcript_sentences": len(candidate_sentences),
            "summary_sentence_count": len(summary_sentences),
            "summarization_method": summarizer.name,
            "legal_boost_applied": self.legal_boost_enabled,
            "stage_timings_ms": stage_timings,
            "total_pipeline_time_ms": total_time_ms,
            "full_transcript_sentences": candidate_sentences,
            "extractive_summary_sentences": summary_sentences
        }

        # Export multi-format reports (JSON, TXT, PDF)
        self.export_results(final_output, stem)

        logger.info(f"=== Pipeline Completed for [{stem}] in {total_time_ms/1000:.2f}s ===")
        return final_output

    def re_summarize(
        self,
        full_transcript_sentences: List[Dict[str, Any]],
        method: Optional[str] = "textrank",
        summary_ratio: float = 0.25,
        judicial_only: bool = True,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Fast on-the-fly extractive summarization from existing transcript."""
        chosen_method = (method or self.default_summarizer_name).lower()
        summarizer = self.summarizers.get(chosen_method, self.summarizers["textrank"])
        base_scores = summarizer.score_sentences(full_transcript_sentences)

        if self.legal_boost_enabled:
            boosted_scores, enriched_sentences = self.enhancer.boost_sentence_scores(
                full_transcript_sentences,
                base_scores,
                language=language
            )
            final_scores = boosted_scores
            candidates = enriched_sentences
        else:
            final_scores = base_scores
            candidates = full_transcript_sentences

        total_s = len(candidates)
        min_k = 1 if judicial_only else 3
        k = max(min_k, int(round(total_s * summary_ratio)))
        k = min(k, 8, total_s)

        return BaseSummarizer.select_extractive_summary(
            candidates,
            final_scores,
            k=k,
            diversity_threshold=0.45,
            judicial_only=judicial_only
        )

    def export_results(self, result: Dict[str, Any], stem: str):
        """Export results to structured JSON, readable TXT, and printable PDF."""
        case_dir = self.output_dir / stem
        case_dir.mkdir(parents=True, exist_ok=True)

        # 1. JSON Export
        json_path = case_dir / f"{stem}_summary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 2. TXT Export
        txt_path = case_dir / f"{stem}_summary.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=" * 75 + "\n")
            f.write(f"COURT PROCEEDING EXTRACTIVE SUMMARY REPORT\n")
            f.write(f"Case / Recording: {stem}\n")
            f.write(f"Detected Language: {result['detected_language'].upper()} ({result['language_confidence']*100:.1f}% confidence)\n")
            f.write(f"Duration: {result['audio_duration_sec']}s | Method: {result['summarization_method']}\n")
            f.write("DISCLAIMER: This extractive summary is an assistive reference tool for academic and\n")
            f.write("research purposes only. Verify all statements against the original video recordings.\n")
            f.write("=" * 75 + "\n\n")

            f.write("--- KEY CHRONOLOGICAL COURT MOMENTS ---\n\n")
            for idx, s in enumerate(result["extractive_summary_sentences"], 1):
                badge = f"[{s.get('legal_type', 'PROCEEDING')}]"
                f.write(f"{idx}. [{s['start_time']:05.1f}s - {s['end_time']:05.1f}s] {badge}\n")
                summary_en = s.get("translated_text") or s.get("text", "")
                f.write(f"   Summary (English): {summary_en}\n")
                if s.get("original_text") and s.get("original_language") != "en":
                    f.write(f"   Original ({s.get('original_language', 'src').upper()}):  {s.get('original_text', s['text'])}\n")
                f.write(f"   Salience Score: {s.get('final_salience_score', 0.0)}\n\n")

        # 3. PDF Export via ReportLab
        self._export_pdf(result, str(case_dir / f"{stem}_summary.pdf"))

    def _export_pdf(self, result: Dict[str, Any], pdf_path: str):
        """Generate formatted PDF summary report using ReportLab."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors

            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter

            # Title Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Court Proceeding Extractive Summary Report")
            c.setFont("Helvetica-Oblique", 9)
            c.setFillColor(colors.darkgray)
            c.drawString(50, height - 65, "Strict Extractive Assistive Pipeline - Academic Capstone")

            # Metadata Box
            c.setStrokeColor(colors.gray)
            c.setFillColor(colors.whitesmoke)
            c.rect(50, height - 120, width - 100, 45, fill=1)

            c.setFillColor(colors.black)
            c.setFont("Helvetica", 9)
            c.drawString(60, height - 90, f"Case ID: {result['case_id']}")
            c.drawString(60, height - 105, f"Language: {result['detected_language']} ({result['language_confidence']*100:.1f}%)")
            c.drawString(250, height - 90, f"Duration: {result['audio_duration_sec']}s")
            c.drawString(250, height - 105, f"Method: {result['summarization_method']}")
            c.drawString(420, height - 90, f"Sentences: {result['summary_sentence_count']}")
            c.drawString(420, height - 105, f"Time: {result['total_pipeline_time_ms']/1000:.2f}s")

            # Disclaimer
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.red)
            c.drawString(50, height - 135, "LEGAL DISCLAIMER: Strictly extractive transcription. Verify all statements against original media.")

            # Summary Body
            y = height - 165
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Key Judicial Moments & Testimonies (Chronological)")
            y -= 20

            for idx, s in enumerate(result["extractive_summary_sentences"], 1):
                if y < 80:
                    c.showPage()
                    y = height - 50

                c.setFont("Helvetica-Bold", 9)
                badge = f"[{s.get('legal_type', 'STATEMENT')}]"
                c.drawString(50, y, f"{idx}. [{s['start_time']:05.1f}s - {s['end_time']:05.1f}s] {badge}")
                y -= 14

                c.setFont("Helvetica", 9)
                # Word wrap sentence text
                text = s.get("translated_text", s["text"])
                chars_per_line = 85
                for i in range(0, len(text), chars_per_line):
                    line = text[i:i + chars_per_line]
                    c.drawString(65, y, line)
                    y -= 12
                y -= 8

            c.save()
        except Exception as e:
            logger.warning(f"Could not generate PDF: {e}")


if __name__ == "__main__":
    print("Testing CourtProceedingSummarizationPipeline...")
    pipeline = CourtProceedingSummarizationPipeline(asr_model_size="tiny", default_summarizer="textrank")
    sample_wav = "data/extracted_audio/CASE_01_5_Movie_CLIP_-_Automotive_Exp.wav"
    if Path(sample_wav).exists():
        res = pipeline.run(sample_wav, method="textrank", summary_ratio=0.25)
        print(f"Summary extracted {res['summary_sentence_count']} sentences in {res['total_pipeline_time_ms']/1000:.2f}s")
        print("\n" + res["extractive_summary_sentences"][0]["text"])
