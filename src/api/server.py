"""Phase 10: FastAPI Backend Service for Asynchronous Court Proceeding Summarization.

Provides RESTful endpoints:
- POST /jobs                : Enqueue court video/audio for background processing
- GET  /jobs                : List all recent jobs with status
- GET  /jobs/{id}           : Job status and telemetry
- GET  /jobs/{id}/transcript: Full timestamped transcript JSON
- GET  /jobs/{id}/summary   : Extractive summary sentences and metadata
- GET  /jobs/{id}/export/{format} : Download TXT, JSON, or PDF reports
- GET  /health              : System readiness, hardware status, and versioning
"""

import os
import sys
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CourtFastAPI")

from src.api.db import init_db, create_job, update_job_status, get_job, list_jobs
from src.pipeline.runner import CourtProceedingSummarizationPipeline

# Initialize FastAPI App
app = FastAPI(
    title="Real-Time Multilingual Court Proceeding Summarization API",
    description="Speech recognition and strictly extractive summarization for judicial recordings.",
    version="1.0.0"
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure DB is ready
init_db()

# Lazy pipeline singleton
_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = CourtProceedingSummarizationPipeline(asr_model_size="tiny", legal_boost_enabled=True)
    return _pipeline


def process_court_job_background(job_id: str, file_path: str, method: str, ratio: float, enable_trans: bool):
    """Background task executing the end-to-end summarization pipeline."""
    update_job_status(job_id, "processing")
    pipeline = get_pipeline()
    try:
        result = pipeline.run(
            media_path=file_path,
            method=method,
            summary_ratio=ratio,
            enable_translation=enable_trans,
            case_id=job_id
        )
        update_job_status(job_id, "completed", result=result)
        logger.info(f"Background Job {job_id} successfully completed.")
    except Exception as e:
        logger.error(f"Background Job {job_id} failed: {e}")
        update_job_status(job_id, "failed", error=str(e))


@app.get("/", include_in_schema=False)
def root():
    """Redirect root path to interactive Swagger documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    """Health check and compute environment inspection."""
    import torch
    return {
        "status": "healthy",
        "service": "Court Proceeding Summarization API",
        "version": "1.0.0",
        "cuda_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }


@app.post("/jobs")
async def submit_court_job(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    method: str = Form("textrank"),
    summary_ratio: float = Form(0.25),
    enable_translation: bool = Form(True)
):
    """Submit a court recording for asynchronous transcription and summarization."""
    job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
    upload_dir = Path("outputs/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    if file:
        dest_path = upload_dir / f"{job_id}_{file.filename}"
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        final_path = str(dest_path)
        orig_name = file.filename
    elif file_path:
        p = Path(file_path)
        if not p.exists():
            raise HTTPException(status_code=400, detail=f"Specified file path does not exist: {file_path}")
        final_path = str(p)
        orig_name = p.name
    else:
        raise HTTPException(status_code=400, detail="Must provide either an uploaded file or file_path.")

    create_job(job_id, orig_name, final_path, method, summary_ratio)
    background_tasks.add_task(
        process_court_job_background,
        job_id, final_path, method, summary_ratio, enable_translation
    )

    return {
        "job_id": job_id,
        "filename": orig_name,
        "status": "queued",
        "method": method,
        "summary_ratio": summary_ratio,
        "poll_url": f"/jobs/{job_id}"
    }


@app.get("/jobs")
def get_all_jobs():
    """List recent court summarization jobs."""
    return {"jobs": list_jobs()}


@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Get single job status and metadata."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/jobs/{job_id}/transcript")
def get_job_transcript(job_id: str):
    """Retrieve full timestamped sentence transcript."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed" or not job.get("result"):
        raise HTTPException(status_code=400, detail=f"Job status is {job['status']}, transcript not ready.")
    return {
        "job_id": job_id,
        "detected_language": job["result"]["detected_language"],
        "sentences": job["result"]["full_transcript_sentences"]
    }


@app.get("/jobs/{job_id}/summary")
def get_job_summary(job_id: str):
    """Retrieve timestamped extractive summary."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed" or not job.get("result"):
        raise HTTPException(status_code=400, detail=f"Job status is {job['status']}, summary not ready.")
    return {
        "job_id": job_id,
        "method": job["result"]["summarization_method"],
        "summary_sentences": job["result"]["extractive_summary_sentences"]
    }


@app.get("/jobs/{job_id}/export/{format_type}")
def export_job_report(job_id: str, format_type: str):
    """Download summary report in TXT, JSON, or PDF format."""
    fmt = format_type.lower()
    case_dir = Path("outputs") / job_id
    if fmt == "json":
        fpath = case_dir / f"{job_id}_summary.json"
        media_type = "application/json"
    elif fmt == "txt":
        fpath = case_dir / f"{job_id}_summary.txt"
        media_type = "text/plain"
    elif fmt == "pdf":
        fpath = case_dir / f"{job_id}_summary.pdf"
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: json, txt, pdf")

    if not fpath.exists():
        raise HTTPException(status_code=404, detail=f"Report file not found: {fpath.name}")

    return FileResponse(str(fpath), media_type=media_type, filename=fpath.name)


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server on http://localhost:8000...")
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=False)
