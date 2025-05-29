import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

LOG_FILE = Path("logs/user_log.jsonl")

def get_recent_logs(limit=50, log_path=LOG_FILE):
    if not log_path.exists():
        return {"count": 0, "logs": []}

    with open(log_path, "r") as f:
        lines = f.readlines()

    logs = []
    for line in lines[-limit:]:
        try:
            logs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    logger.info(f"Fetched {len(logs)} logs from {log_path}")
    return {
        "count": len(logs),
        "logs": logs
    }