from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from web.utils.patch_assistant import PatchAssistant
from web.utils.response import success_response, error_response
from pathlib import Path
import google.generativeai as genai
import os
import openai
import logging

logger = logging.getLogger(__name__)


from web.memory.plan_executor import generate_plan

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")

USE_GEMINI = os.getenv("USE_GEMINI", "true").lower() == "true"

DEV_SESSIONS = {"latest": {"generated_plan": "", "diagnostic_feedback": "", "readme_path": ""}}

router = APIRouter()

@router.post("/dev/plan")
def generate_plan_route(payload: dict):
    try:
        goal = payload.get("goal")
        if not goal:
            return error_response("Missing 'goal' in payload.")

        try:
            plan = generate_plan(goal)
        except Exception as e:
            return error_response(f"Failed to generate plan: {e}")

        DEV_SESSIONS["latest"]["generated_plan"] = plan

        return success_response({"message": "Plan generated successfully.", "plan": plan})

    except Exception as e:
        return error_response(str(e))

templates = Jinja2Templates(directory="web/templates")

@router.post("/dev/plan/auto")
def auto_generate_plan_route():
    try:
        plan = DEV_SESSIONS["latest"].get("generated_plan")
        if not plan:
            return error_response("No generated plan available.")

        diagnose_prompt = f"""You are a senior software architect. Review this project plan and identify:
- Any missing steps
- Unclear or vague items
- Suggestions to improve structure or quality

Plan:
{plan}
"""
        try:
            if USE_GEMINI:
                model = genai.GenerativeModel("gemini-pro")
                diagnosis_result = model.generate_content(diagnose_prompt)
                feedback = diagnosis_result.text.strip()
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": diagnose_prompt}]
                )
                feedback = response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("Gemini Error in dev_plan_auto: %s", e)
            return error_response(f"Gemini API call failed: {e}")

        DEV_SESSIONS["latest"]["diagnostic_feedback"] = feedback

        assistant = PatchAssistant()
        file_path = Path("web/routes/agent.py")
        patch_success = assistant.patch_summarizer_import(file_path)

        return success_response({
            "message": "Auto pipeline completed.",
            "diagnosis": feedback,
            "patch_success": patch_success,
            "patched_file": str(file_path)
        })

    except Exception as e:
        return error_response(str(e))

@router.post("/dev/plan/docs")
def generate_docs():
    try:
        plan = DEV_SESSIONS["latest"].get("generated_plan")
        if not plan:
            return error_response("No generated plan available.")

        prompt = f"""Write a clean and professional README.md file based on this project plan:
{plan}

Include:
- Title
- Description
- Features
- Setup Instructions
- Usage
"""

        try:
            if USE_GEMINI:
                model = genai.GenerativeModel("gemini-pro")
                result = model.generate_content(prompt)
                content = result.text.strip()
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("Gemini Error in generate_docs: %s", e)
            return error_response(f"Gemini API call failed: {e}")

        target_path = Path("web_app/README.md")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content)

        DEV_SESSIONS["latest"]["readme_path"] = str(target_path)

        return success_response({
            "message": "README.md generated.",
            "path": str(target_path),
            "content": content
        })
    except Exception as e:
        return error_response(str(e))

@router.post("/dev/plan/diagnose")
def diagnose_plan():
    try:
        plan = DEV_SESSIONS["latest"].get("generated_plan")
        if not plan:
            return error_response("No generated plan available.")

        prompt = f"""You are a senior software architect. Review this project plan and identify:
- Any missing steps
- Unclear or vague items
- Suggestions to improve structure or quality

Plan:
{plan}
"""

        if USE_GEMINI:
            model = genai.GenerativeModel("gemini-pro")
            result = model.generate_content(prompt)
            feedback = result.text.strip()
        else:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            feedback = response.choices[0].message.content.strip()

        DEV_SESSIONS["latest"]["diagnostic_feedback"] = feedback

        return success_response({"feedback": feedback})
    except Exception as e:
        return error_response(str(e))

@router.post("/dev/patch")
def dev_patch_summarizer():
    assistant = PatchAssistant()
    file_path = Path("web/routes/agent.py")
    success = assistant.patch_summarizer_import(file_path)
    return success_response({"success": success})


# New route to serve generated docs as HTML

@router.get("/dev/plan/docs/view", response_class=HTMLResponse)
def view_generated_docs(request: Request):
    try:
        path = DEV_SESSIONS["latest"].get("readme_path")
        if not path:
            return HTMLResponse(content="No README.md found.", status_code=404)
        content = Path(path).read_text(encoding="utf-8")
        return templates.TemplateResponse("doc_view.html", {"request": request, "content": content})
    except Exception as e:
        logger.error("Error in view_generated_docs: %s", e)
        return HTMLResponse(content=f"Error: {e}", status_code=500)


# Health check endpoint for backend status verification
@router.get("/health")
def health_check():
    return {"status": "ok"}
