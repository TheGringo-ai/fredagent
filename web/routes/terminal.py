from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import subprocess
from web.utils.response import success_response, error_response

router = APIRouter()

@router.post("/terminal/exec")
async def execute_command(request: Request):
    data = await request.json()
    command = data.get("command", "").strip()

    if not command:
        return error_response("No command provided.", status_code=400)

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout or result.stderr
        return success_response({"output": output[:5000]})  # Limit long outputs
    except subprocess.TimeoutExpired:
        return error_response("⏱️ Command timed out.", status_code=500)
    except Exception as e:
        return error_response(f"❌ Error: {str(e)}", status_code=500)