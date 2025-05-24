

import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def generate_patch_plan(instruction: str) -> dict:
    """
    Parses an instruction and determines which file should be modified.
    This version only simulates a mapping.
    """
    instruction = instruction.lower()
    timestamp = datetime.utcnow().isoformat() + "Z"

    if "streaming" in instruction:
        target_file = "web/templates/chat.html"
        action = "Insert streaming-friendly response container"
    elif "summarize" in instruction and "logs" in instruction:
        target_file = "web/routes/logquery.py"
        action = "Add summarization routine using DevAssistantAgent"
    elif "add route" in instruction:
        target_file = "web/routes/agent.py"
        action = "Create new FastAPI route"
    else:
        target_file = None
        action = "No recognized action"

    return {
        "timestamp": timestamp,
        "instruction": instruction,
        "target": target_file,
        "action": action
    }