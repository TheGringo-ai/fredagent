
# --- Auto Fix Agent Route ---
from fastapi import APIRouter, Request, Body
from fastapi.responses import JSONResponse, HTMLResponse
from web.utils.response import success_response, error_response
from fastapi.testclient import TestClient
from web.memory.summarizer_engine import Summarizer

router = APIRouter()

from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request as FastAPIRequest
from web.routes.agent import load_from_library
from fastapi.datastructures import FormData
from starlette.requests import Request as StarletteRequest
from starlette.datastructures import FormData as StarletteFormData
from web.routes.agent import apply_library_file

@router.post("/agent/auto_fix", response_class=JSONResponse)
async def agent_auto_fix(request: Request, payload: dict = Body(...)):
    error_log = payload.get("traceback", "")
    session_id = request.client.host

    if not error_log:
        return error_response("Missing traceback", status_code=400)

    try:
        # 1. Summarize the traceback
        summarizer = Summarizer()
        summary = summarizer.summarize(error_log)

        # 2. Try to match existing fix from dev_library
        query = {"prompt": error_log}
        match_resp = await load_from_library(prompt=query)
        if (
            hasattr(match_resp, "status_code")
            and getattr(match_resp, "status_code", 200) == 200
            and isinstance(match_resp, dict)
            and "file" in match_resp
        ) or (
            isinstance(match_resp, dict) and "file" in match_resp
        ):
            filename = match_resp["file"] if isinstance(match_resp, dict) else match_resp.json()["file"]

            class DummyRequest:
                def __init__(self):
                    self._form = StarletteFormData({"file": filename})
                async def form(self):
                    return self._form

            dummy_request = DummyRequest()
            apply_resp = await apply_library_file(request=dummy_request, file=filename)
            return success_response({
                "status": "Applied from library",
                "file": filename,
                "summary": summary,
                "result": apply_resp if isinstance(apply_resp, dict) else apply_resp.json()
            })

        # 3. No match → Use GPT to generate patch suggestion
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Analyze and fix this Python error:\n{error_log}"}],
            temperature=0.3
        )
        fix_suggestion = response['choices'][0]['message']['content']

        return success_response({
            "status": "No library match",
            "summary": summary,
            "suggested_fix": fix_suggestion,
            "action": "manual review required"
        })

    except Exception as e:
        return error_response(str(e), status_code=500)

from fastapi import Form
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
from typing import Optional
import json
import openai

BASE_DIR = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(directory=str(BASE_DIR / "web" / "templates"))

# TEMPORARY MOCK: Replace with the real import when available
# from web.memory.agents.dev_assistant import DevAssistantAgent
class DevAssistantAgent:
    def process(self, instruction):
        return f"[MOCK] Processed instruction: {instruction}"

class AgentRequest(BaseModel):
    instruction: str

@router.get("/agent", response_class=HTMLResponse)
async def agent_ui(request: Request):
    return templates.TemplateResponse("agent.html", {
        "request": request,
        "title": "Smart Agent Assistant",
        "description": "Use natural language to command and modify your project in real-time."
    })


agent = DevAssistantAgent()

@router.post("/agent/update", response_class=JSONResponse)
async def run_instruction(request: Request, payload: AgentRequest):
    try:
        instruction = payload.instruction

        # Use DevAssistantAgent for actual response
        result = agent.process(instruction)

        # Store in memory
        memory.store_log_entry({
            "text": instruction,
            "response": result
        })

        # Log the interaction
        log_entry = {
            "instruction": instruction,
            "result": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ip": request.client.host,
        }
        log_path = BASE_DIR / "logs" / "agent_log.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        return success_response({"response": result})
    except Exception as e:
        error_log = {
            "error": str(e),
            "instruction": instruction if 'instruction' in locals() else None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ip": request.client.host
        }
        log_path = BASE_DIR / "logs" / "agent_log.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(error_log) + "\n")
        return error_response(str(e), status_code=500)

# Simple in-memory session context (can replace with persistent store later)
DEV_SESSIONS = {}

@router.get("/dev/start", response_class=HTMLResponse)
async def dev_start(request: Request):
    session_id = request.client.host  # crude session id (can refine later)
    DEV_SESSIONS[session_id] = {"step": 0, "answers": []}
    first_question = "What type of project would you like to create? (e.g., web app, CLI tool, automation script)"
    return templates.TemplateResponse("agent.html", {
        "request": request,
        "title": "DevAgent Setup",
        "description": first_question,
        "session_id": session_id
    })

@router.post("/dev/answer", response_class=JSONResponse)
async def dev_answer(request: Request, answer: str = Form(...), session_id: Optional[str] = Form(None)):
    session_id = session_id or request.client.host
    session = DEV_SESSIONS.get(session_id)

    if not session:
        return JSONResponse(status_code=400, content={"error": "Session not found"})

    session["answers"].append(answer)
    session["step"] += 1

    # Save session to disk
    session_file = BASE_DIR / "logs" / "dev_sessions" / f"{session_id}.json"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    with session_file.open("w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)

    questions = [
        "What programming language would you like to use?",
        "Where should I create the project folder?",
        "Should this include deployment setup for Google Cloud?",
        "What integrations are needed? (e.g., Gmail, Google Drive, Sheets)",
        "Would you like to connect it to an existing repo or create a new one?"
    ]

    if session["step"] < len(questions):
        return {"question": questions[session["step"]]}
    else:
        # All answers collected, trigger plan generation and build
        try:
            goal = "Build a " + session["answers"][0] + " using " + session["answers"][1]
            result = generate_plan(goal)
            session["generated_plan"] = result
            session["generated_at"] = datetime.utcnow().isoformat() + "Z"

            # Attempt to parse and build project immediately
            try:
                parsed_plan = json.loads(result)
                build_result = execute_plan(parsed_plan)
                session["built_plan"] = build_result
            except Exception as build_err:
                build_result = {"error": f"Failed to build: {str(build_err)}"}

            return {
                "message": "All setup questions answered. Plan generated and project scaffolded.",
                "answers": session["answers"],
                "plan": result,
                "build_result": build_result
            }
        except Exception as e:
            return {
                "message": "Setup complete but failed to generate plan.",
                "answers": session["answers"],
                "error": str(e)
            }

@router.post("/dev/build", response_class=JSONResponse)
async def dev_build(request: Request, session_id: Optional[str] = Form(None)):
    session_id = session_id or request.client.host
    session = DEV_SESSIONS.get(session_id)

    if not session or "answers" not in session or len(session["answers"]) < 5:
        return JSONResponse(status_code=400, content={"error": "Incomplete session or missing data"})

    project_type, language, folder_path, gcloud, integrations = session["answers"][:5]

    # Generate folder and placeholder files
    base = Path(folder_path).expanduser().resolve()
    try:
        base.mkdir(parents=True, exist_ok=True)
        (base / "README.md").write_text(f"# {project_type.title()} - Powered by DevAgent\n\nLanguage: {language}")
        (base / ".env").write_text("# Environment configuration\n")
        (base / "main.py").write_text("# Entry point\n" if "python" in language.lower() else "// Main file\n")

        apply_templates(base, project_type)

        session["built_at"] = datetime.utcnow().isoformat() + "Z"
        build_log = BASE_DIR / "logs" / "dev_sessions" / f"{session_id}_build.json"
        with build_log.open("w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)

        return {"status": "project scaffolded", "path": str(base)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/dev/resume", response_class=JSONResponse)
async def dev_resume(request: Request, session_id: Optional[str] = None):
    session_id = session_id or request.client.host
    session_file = BASE_DIR / "logs" / "dev_sessions" / f"{session_id}.json"
    if not session_file.exists():
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    with session_file.open("r", encoding="utf-8") as f:
        DEV_SESSIONS[session_id] = json.load(f)

    step = DEV_SESSIONS[session_id].get("step", 0)
    questions = [
        "What programming language would you like to use?",
        "Where should I create the project folder?",
        "Should this include deployment setup for Google Cloud?",
        "What integrations are needed? (e.g., Gmail, Google Drive, Sheets)",
        "Would you like to connect it to an existing repo or create a new one?"
    ]

    if step < len(questions):
        return {"question": questions[step], "step": step}
    else:
        return {"message": "All setup questions answered. Ready to build.", "answers": DEV_SESSIONS[session_id]["answers"]}


# Optional template integration
TEMPLATES = {
    "web app": ["templates/web/index.html", "templates/web/app.js"],
    "cli tool": ["templates/cli/main.py"],
    "automation script": ["templates/scripts/worker.py"]
}

def apply_templates(base: Path, project_type: str):
    template_files = TEMPLATES.get(project_type.lower(), [])
    for rel_path in template_files:
        target_path = base / Path(rel_path).name
        target_path.write_text(f"# {rel_path} generated\n")

@router.post("/dev/library/save", response_class=JSONResponse)
async def save_to_library(request: Request, session_id: Optional[str] = Form(...), label: Optional[str] = Form(None), tags: Optional[str] = Form("")):
    session_file = BASE_DIR / "logs" / "dev_sessions" / f"{session_id}_build.json"
    if not session_file.exists():
        return JSONResponse(status_code=404, content={"error": "Build session not found"})

    with session_file.open("r", encoding="utf-8") as f:
        session_data = json.load(f)

    session_data["uses"] = 0
    session_data["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]

    label = label or f"{session_data['answers'][0].replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    library_file = BASE_DIR / "dev_library" / f"{label}.json"
    library_file.parent.mkdir(parents=True, exist_ok=True)

    with library_file.open("w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

    return {"status": "saved", "file": str(library_file)}

# --- /dev/library/load: semantic search for best library entry ---
from fastapi import Body
from sentence_transformers import SentenceTransformer
import numpy as np

@router.post("/dev/library/load", response_class=JSONResponse)
async def load_from_library(prompt: dict = Body(...)):
    query = prompt.get("prompt")
    if not query:
        return JSONResponse(status_code=400, content={"error": "Prompt is required"})

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vec = model.encode(query, convert_to_numpy=True)

    library_dir = BASE_DIR / "dev_library"
    best_match = None
    best_score = -1.0

    for path in library_dir.glob("*.json"):
        with path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                context = " ".join(data.get("answers", []))
                context_vec = model.encode(context, convert_to_numpy=True)
                score = np.dot(query_vec, context_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(context_vec) + 1e-10)
                if score > best_score:
                    best_score = score
                    best_match = (str(path.name), data)
            except Exception:
                continue

    if best_match:
        return {"file": best_match[0], "score": best_score, "entry": best_match[1]}
    else:
        return JSONResponse(status_code=404, content={"error": "No match found."})
@router.post("/dev/library/apply", response_class=JSONResponse)
async def apply_library_file(request: Request, file: Optional[str] = Form(...)):
    library_file = BASE_DIR / "dev_library" / file
    if not library_file.exists():
        return JSONResponse(status_code=404, content={"error": "Library file not found"})

    try:
        with library_file.open("r", encoding="utf-8") as f:
            session_data = json.load(f)

        if "answers" not in session_data or len(session_data["answers"]) < 5:
            return JSONResponse(status_code=400, content={"error": "Incomplete library entry"})

        project_type, language, folder_path, gcloud, integrations = session_data["answers"][:5]
        base = Path(folder_path).expanduser().resolve()

        base.mkdir(parents=True, exist_ok=True)
        (base / "README.md").write_text(f"# {project_type.title()} - Rebuilt from DevAgent Library\n\nLanguage: {language}")
        (base / ".env").write_text("# Reconstructed environment configuration\n")
        (base / "main.py").write_text("# Reconstructed entry point\n" if "python" in language.lower() else "// Main file\n")

        apply_templates(base, project_type)

        # Increment usage
        session_data["uses"] = session_data.get("uses", 0) + 1
        with library_file.open("w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)

        return {"status": "library applied", "path": str(base)}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
# --- DevAgent Library Management Endpoints ---

@router.get("/dev/library/list", response_class=JSONResponse)
async def list_library_files(tags: Optional[str] = None):
    library_dir = BASE_DIR / "dev_library"
    entries = []
    filter_tags = set(t.strip().lower() for t in tags.split(",")) if tags else set()

    for f in library_dir.glob("*.json"):
        with f.open("r", encoding="utf-8") as file_data:
            try:
                data = json.load(file_data)
                entry_tags = set(t.lower() for t in data.get("tags", []))
                if not filter_tags or filter_tags & entry_tags:
                    entries.append({
                        "file": f.name,
                        "tags": list(entry_tags),
                        "uses": data.get("uses", 0)
                    })
            except:
                continue
    return {"files": entries}

@router.get("/dev/library/loadfile", response_class=JSONResponse)
async def load_library_file(file: str):
    file_path = BASE_DIR / "dev_library" / file
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})

    with file_path.open("r", encoding="utf-8") as f:
        entry = json.load(f)
    return {"entry": entry}


@router.post("/dev/library/delete", response_class=JSONResponse)
async def delete_library_file(payload: dict = Body(...)):
    file = payload.get("file")
    file_path = BASE_DIR / "dev_library" / file
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})

    try:
        file_path.unlink()
        return {"status": "deleted"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- DevAgent Library: Update Tags ---
@router.post("/dev/library/tags", response_class=JSONResponse)
async def update_library_tags(payload: dict = Body(...)):
    file = payload.get("file")
    tags = payload.get("tags")
    file_path = BASE_DIR / "dev_library" / file
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})

    try:
        with file_path.open("r+", encoding="utf-8") as f:
            data = json.load(f)
            data["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        return {"status": "tags updated"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- DevAgent Library: Rename File ---
@router.post("/dev/library/rename", response_class=JSONResponse)
async def rename_library_file(payload: dict = Body(...)):
    file = payload.get("file")
    new_name = payload.get("new_name")
    file_path = BASE_DIR / "dev_library" / file
    new_path = BASE_DIR / "dev_library" / new_name
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})

    try:
        file_path.rename(new_path)
        return {"status": "renamed"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

from web.memory.plan_executor import generate_plan


# TODO: Replace with actual plan executor import when available
# Scaffolded implementation for plan execution
def execute_plan(plan):
    try:
        project_type = plan.get("project_type", "project").replace(" ", "_").lower()
        folder = BASE_DIR / project_type
        folder.mkdir(parents=True, exist_ok=True)

        readme_path = folder / "README.md"
        readme_content = f"# {plan.get('project_title', 'Project')}\n\n## Overview\n{plan.get('overview', '')}"
        readme_path.write_text(readme_content)

        files = plan.get("files", [])
        for file_info in files:
            path = folder / file_info.get("path", "main.py")
            content = file_info.get("content", "# TODO: Implement")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

        return {"status": "scaffolded", "files": [str(folder / f.get("path", "main.py")) for f in files]}
    except Exception as e:
        return {"error": str(e)}

@router.post("/dev/plan", response_class=JSONResponse)
async def dev_plan(request: Request, payload: dict = Body(...)):
    goal = payload.get("goal", "").strip()
    if not goal:
        return JSONResponse(status_code=400, content={"error": "Missing project goal"})

    result = generate_plan(goal)
    try:
        parsed = json.loads(result)
        return {"plan": parsed}
    except Exception:
        return {"response": result}


# --- Dev Plan Build: Execute Plan to Scaffold Project ---
@router.post("/dev/plan/build", response_class=JSONResponse)
async def dev_plan_build(request: Request, payload: dict = Body(...)):
    plan = payload.get("plan")
    if not plan:
        return JSONResponse(status_code=400, content={"error": "Missing build plan"})

    result = execute_plan(plan)
    return result if isinstance(result, dict) else {"error": "Invalid plan execution result"}
@router.get("/dev/explorer", response_class=JSONResponse)
async def dev_explorer(folder: str):
    root = BASE_DIR / folder
    if not root.exists() or not root.is_dir():
        return JSONResponse(status_code=404, content={"error": "Folder not found"})

    files = []
    for file_path in root.rglob("*"):
        if file_path.is_file():
            files.append({
                "name": str(file_path.relative_to(root)),
                "path": str(file_path.relative_to(BASE_DIR))
            })
    return {"files": files}

@router.get("/dev/explorer/view", response_class=HTMLResponse)
async def view_file(path: str):
    file_path = BASE_DIR / path
    if not file_path.exists():
        return HTMLResponse(content=f"File not found: {path}", status_code=404)

    content = file_path.read_text(encoding="utf-8")
    return f"<h2>{path}</h2><pre>{content}</pre>"

@router.post("/dev/plan/tests", response_class=JSONResponse)
async def dev_generate_tests(request: Request, payload: dict = Body(...)):
    plan = payload.get("plan")
    if not plan:
        return JSONResponse(status_code=400, content={"error": "Missing plan input"})

    try:
        prompt = f"Create Python unit test files based on this project plan:\n{json.dumps(plan, indent=2)}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        result = response['choices'][0]['message']['content']
        folder = BASE_DIR / plan.get("project_type", "project").replace(" ", "_").lower()
        test_file = folder / "test_main.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(result)

        return {"status": "Test file generated", "path": str(test_file)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Backend helper for emitting build step progress (currently UI-only, placeholder)
@router.post("/dev/updateBuildSteps", response_class=JSONResponse)
async def update_build_steps(payload: dict = Body(...)):
    # This endpoint can be expanded to emit build step progress
    # For now, just echo payload for UI integration
    return {"status": "ok", "data": payload}
# --- Enhanced /agent command route with backend model selection and memory logging ---
from web.memory.memory_manager import MemoryManager
from web.memory.summarizer_engine import Summarizer
from fastapi import Body

memory = MemoryManager()
summarizer = Summarizer()

@router.post("/agent", response_class=JSONResponse)
async def agent_command_post(request: Request, payload: dict = Body(...)):
    instruction = payload.get("instruction", "").strip()
    model = payload.get("model", "gpt-3.5-turbo")
    stream = payload.get("stream", False)
    log_flag = payload.get("log", True)

    if not instruction:
        return JSONResponse(status_code=400, content={"error": "Missing instruction"})

    try:
        if model.startswith("gpt"):
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": instruction}],
                temperature=0.5
            )
            result = response['choices'][0]['message']['content']
        else:
            result = f"[Unsupported model: {model}]"

        if log_flag:
            memory.store_log_entry({
                "text": instruction,
                "response": result
            })

        return {"response": result}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Inline File Viewer Route ---
@router.get("/view", response_class=HTMLResponse)
async def view_generated_file(path: str):
    try:
        file_path = BASE_DIR / path
        if not file_path.exists() or not file_path.is_file():
            return HTMLResponse(content=f"<h2>❌ File not found:</h2><pre>{path}</pre>", status_code=404)

        content = file_path.read_text(encoding="utf-8")
        # Build dropdown of all files in dev_docs
        all_files = [f for f in (BASE_DIR / "dev_docs").rglob("*") if f.is_file()]
        options = "\n".join([f"<option value='{f.relative_to(BASE_DIR)}'>{f.name}</option>" for f in all_files])
        dropdown_html = f"""
        <form method='get' action='/view'>
          <select name='path'>{options}</select>
          <button type='submit'>View</button>
        </form>
        <a href='/{path}' download>⬇️ Download {file_path.name}</a>
        """
        html = f"<h2>📄 {file_path.name}</h2>{dropdown_html}<pre style='white-space:pre-wrap'>{content}</pre>"
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(content=f"<h2>❌ Error</h2><pre>{str(e)}</pre>", status_code=500)