


import json
from pathlib import Path

def log_to_file(entry: dict, filename: str = "devchat_log.jsonl"):
    """
    Appends a JSON log entry to a file in the /logs directory.
    Creates the file and parent folder if they don't exist.
    """
    path = Path(__file__).resolve().parents[2] / "logs" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")