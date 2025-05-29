from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from fpdf import FPDF
import io
import logging

from web.utils.response import success_response, error_response

logger = logging.getLogger(__name__)

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "user_log.jsonl"

router = APIRouter()

@router.post("/export/logs")
async def export_logs(request: Request):
    data = await request.json()
    folder_path = Path(data.get("folder_path"))

    if not folder_path.exists() or not folder_path.is_dir():
        logger.warning("Invalid folder path: %s", folder_path)
        return error_response("Invalid folder path", status_code=400)

    if not LOG_PATH.exists():
        logger.warning("Source log file not found: %s", LOG_PATH)
        return error_response("Source log file not found", status_code=404)

    destination = folder_path / "exported_user_log.jsonl"
    shutil.copy2(LOG_PATH, destination)
    logger.info("Logs exported to: %s", destination)

    return success_response({"status": "exported", "destination": str(destination)})

from fastapi.responses import StreamingResponse
import csv
import json

@router.get("/export/logs.csv")
async def export_logs_csv():
    if not LOG_PATH.exists():
        logger.warning("Source log file not found: %s", LOG_PATH)
        return error_response("Source log file not found", status_code=404)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "user", "text", "status"])

    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                writer.writerow([
                    entry.get("timestamp", ""),
                    entry.get("user", {}).get("name", ""),
                    entry.get("text", ""),
                    entry.get("status", "")
                ])
            except Exception:
                continue

    output.seek(0)
    logger.info("CSV export completed with %d entries", output.tell())
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=user_log.csv"})

@router.get("/export/logs.json")
async def export_logs_json():
    if not LOG_PATH.exists():
        logger.warning("Source log file not found: %s", LOG_PATH)
        return error_response("Source log file not found", status_code=404)

    with LOG_PATH.open("r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]
    logger.info("Exported %d JSON log entries", len(entries))

    return success_response(entries)

@router.get("/export/logs.pdf")
async def export_logs_pdf():
    if not LOG_PATH.exists():
        logger.warning("Source log file not found: %s", LOG_PATH)
        return JSONResponse(status_code=404, content={"error": "Source log file not found"})

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                text = f"{entry.get('timestamp', '')} | {entry.get('user', {}).get('name', '')} | {entry.get('text', '')}\n"
                pdf.multi_cell(0, 10, text)
            except Exception:
                continue

    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    logger.info("PDF export completed")

    return StreamingResponse(output, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=user_log.pdf"})
