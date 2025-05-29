from fastapi import APIRouter, Form, Request, Query
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from web.utils.response import success_response, error_response
router = APIRouter()
import tiktoken
from starlette.responses import Response
from pathlib import Path
import json
from datetime import datetime

def get_session_context(session_id, top_k=5):
    path = Path(__file__).resolve().parents[2] / "logs" / "user_log.jsonl"
    if not path.exists():
        return []
    lines = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("session_id") == session_id and "text" in obj:
                    lines.append(obj["text"])
            except Exception as e:
                print(f"Log read error: {e}")
                continue
    return lines[-top_k:]


# Stream response dynamically from selected model/service with context injection
@router.post("/ui/stream")
async def stream_response(
    prompt: str = Form(...),
    session_id: str = Form("default"),
    model: str = Form("gpt-4"),
    service: str = Form("openai"),
    use_memory_flag: bool = Form(True)
):
    token_counter = {"count": 0}
    full_prompt = prompt

    encoding = tiktoken.encoding_for_model(model)

    if use_memory_flag:
        past_logs = get_session_context(session_id, top_k=5)
        if past_logs:
            context = "\n".join(past_logs)
            full_prompt = f"{context}\n\n{prompt}"

    async def stream_openai():
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )
            async for chunk in response:
                if "choices" in chunk:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        text = delta["content"]
                        token_counter["count"] += len(encoding.encode(text))
                        yield text
        except Exception as e:
            yield f"\n[ERROR] {str(e)}"

    async def stream_gemini():
        try:
            for chunk in stream_gemini_response(full_prompt):
                token_counter["count"] += len(encoding.encode(chunk))
                yield chunk
        except Exception as e:
            yield f"\n[ERROR] {str(e)}"

    stream_fn = stream_openai if service == "openai" else stream_gemini

    print(f"Streaming using model: {model}, service: {service}, memory: {use_memory_flag}")

    return StreamingResponse(
        stream_fn(),
        media_type="text/plain",
        headers={"X-Token-Usage": str(token_counter["count"])}
    )


# --- Feedback endpoint ---

@router.post("/feedback")
async def capture_feedback(request: Request):
    feedback_log = Path(__file__).resolve().parents[2] / "logs" / "feedback_log.jsonl"
    data = await request.json()
    data["timestamp"] = datetime.utcnow().isoformat() + "Z"

    feedback_log.parent.mkdir(parents=True, exist_ok=True)
    with feedback_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")

    return success_response({"status": "recorded"})


@router.get("/history/search")
async def search_history(session_id: str = Query(...), keyword: str = Query(None)):
    log_path = Path(__file__).resolve().parents[2] / "logs" / "user_log.jsonl"
    if not log_path.exists():
        return error_response("Log file not found", status_code=404)

    results = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("session_id") == session_id and "text" in entry:
                    if keyword is None or keyword.lower() in entry["text"].lower():
                        results.append(entry)
            except Exception as e:
                print(f"Log read error: {e}")
                continue

    return success_response({"logs": results})

import csv
import io

@router.get("/history/export.csv")
async def export_history_csv(session_id: str = Query(...), keyword: str = Query(None)):
    log_path = Path(__file__).resolve().parents[2] / "logs" / "user_log.jsonl"
    if not log_path.exists():
        return error_response("Log file not found", status_code=404)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "session_id", "text"])

    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("session_id") == session_id and "text" in entry:
                    if keyword is None or keyword.lower() in entry["text"].lower():
                        writer.writerow([entry.get("timestamp", ""), entry["session_id"], entry["text"]])
            except Exception as e:
                print(f"Log read error: {e}")
                continue

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=history_export.csv"
    })


# --- Export history as JSON and PDF ---
from fpdf import FPDF

@router.get("/history/export.json")
async def export_history_json(session_id: str = Query(...), keyword: str = Query(None)):
    log_path = Path(__file__).resolve().parents[2] / "logs" / "user_log.jsonl"
    if not log_path.exists():
        return error_response("Log file not found", status_code=404)

    filtered = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("session_id") == session_id and "text" in entry:
                    if keyword is None or keyword.lower() in entry["text"].lower():
                        filtered.append(entry)
            except Exception as e:
                print(f"Log read error: {e}")
                continue

    json_path = Path(__file__).resolve().parents[2] / "logs" / "history_export.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2)

    return FileResponse(path=json_path, media_type="application/json", filename="session_history.json")


@router.get("/history/export.pdf")
async def export_history_pdf(session_id: str = Query(...), keyword: str = Query(None)):
    log_path = Path(__file__).resolve().parents[2] / "logs" / "user_log.jsonl"
    if not log_path.exists():
        return error_response("Log file not found", status_code=404)

    filtered = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("session_id") == session_id and "text" in entry:
                    if keyword is None or keyword.lower() in entry["text"].lower():
                        filtered.append(entry)
            except Exception as e:
                print(f"Log read error: {e}")
                continue

    pdf_path = Path(__file__).resolve().parents[2] / "logs" / "history_export.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    for entry in filtered:
        pdf.multi_cell(0, 10, f"[{entry.get('timestamp', '')}] {entry['text']}")

    pdf.output(str(pdf_path))

    return FileResponse(path=pdf_path, media_type="application/pdf", filename="session_history.pdf")

@router.get("/history/archive")
async def archive_history(session_id: str = Query(...), keyword: str = Query(None)):
    log_path = Path(__file__).resolve().parents[2] / "logs" / "user_log.jsonl"
    archive_dir = Path(__file__).resolve().parents[2] / "logs" / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)

    if not log_path.exists():
        return error_response("Log file not found", status_code=404)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    archive_file = archive_dir / f"{session_id}_{timestamp}.jsonl"

    filtered = []
    with log_path.open("r", encoding="utf-8") as src, archive_file.open("w", encoding="utf-8") as dest:
        for line in src:
            try:
                entry = json.loads(line.strip())
                if entry.get("session_id") == session_id and "text" in entry:
                    if keyword is None or keyword.lower() in entry["text"].lower():
                        dest.write(json.dumps(entry) + "\n")
                        filtered.append(entry)
            except Exception as e:
                print(f"Log read error: {e}")
                continue

    print(f"Archived {len(filtered)} entries to {archive_file}")

    return success_response({"status": "archived", "file": str(archive_file)})