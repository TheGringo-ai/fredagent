<file name=web/utils/memory_tools.py>
from pathlib import Path
import json

def get_recent_logs(log_file_path="logs/user_log.jsonl", limit=50):
    path = Path(log_file_path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines[-limit:]]
</file>

from web.utils.llm import call_llm

class DevAssistantAgent:
    def __init__(self):
        self.name = "DevAssistant"

    def run_prompt(self, prompt: str, model: str = "openai") -> dict:
        if not prompt.strip():
            return {"error": "Prompt cannot be empty."}

        response = call_llm(prompt=prompt, model=model)
        return {
            "agent": self.name,
            "input": prompt,
            "model": model,
            "response": response
        }