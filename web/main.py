from fastapi import APIRouter
from fastapi import HTTPException
import subprocess
import os
import shlex

from web.utils.response import success_response, error_response

router = APIRouter()

@router.post("/execute")
async def execute_command(command: str):
    try:
        proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = proc.communicate(timeout=10)
        return success_response({"output": output.decode()[:5000]})
    except subprocess.TimeoutExpired:
        proc.kill()
        return error_response("⏱️ Command timed out.", status_code=500)
    except Exception as e:
        return error_response(f"❌ Error: {str(e)}", status_code=500)

@router.get("/history")
async def get_history():
    history_file = os.path.expanduser("~/.bash_history")
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            return success_response({"output": f.read()})
    else:
        return error_response("No history available.", status_code=404)

@router.get("/system-info")
async def get_system_info():
    info = []
    try:
        uname = subprocess.check_output(["uname", "-a"]).decode().strip()
        info.append(uname)
    except Exception:
        info.append("Unable to get system info")
    return success_response({"output": "\n".join(info)})
