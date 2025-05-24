

import os
from pathlib import Path
from memory.agents.dev_assistant import AgentControlCenter
from memory.patcher.patch_executor import execute_patch

class ControlCenter:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir or os.getcwd())
        self.agent = AgentControlCenter()
        print(f"[INIT] ControlCenter initialized with base directory: {self.base_dir}")

    def handle_instruction(self, instruction: str, source: str = "agent"):
        print(f"[INSTRUCTION] Received: {instruction}")
        plan = self.agent.plan(instruction, source=source)
        if not plan or "file" not in plan or "action" not in plan:
            print("[ERROR] Invalid plan format.")
            return {"status": "error", "message": "Invalid plan from agent."}

        file_path = self.base_dir / plan["file"]
        print(f"[PATCH] Target: {file_path}")
        result = execute_patch(file_path, plan)
        return {"status": "ok", "result": result}

if __name__ == "__main__":
    cc = ControlCenter()
    test_instruction = "Add a logging statement after each function call in upload.py"
    output = cc.handle_instruction(test_instruction)
    print("[RESULT]", output)