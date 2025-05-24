

from pathlib import Path
from datetime import datetime

def apply_patch_plan(patch_plan: dict) -> dict:
    target = patch_plan.get("target")
    action = patch_plan.get("action")
    instruction = patch_plan.get("instruction")

    if not target:
        return {"status": "skipped", "reason": "No target file in patch plan"}

    file_path = Path(target)
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

    # Append a comment with the action and instruction
    timestamp = datetime.utcnow().isoformat() + "Z"
    edit_block = f"\n\n# [PATCHED] {timestamp}\n# ACTION: {action}\n# INSTRUCTION: {instruction}\n"

    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(edit_block)
        return {
            "status": "patched",
            "file": str(file_path),
            "timestamp": timestamp,
            "note": "Appended patch instruction as comment"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}