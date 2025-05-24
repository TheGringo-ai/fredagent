import os
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

# Import OpenAI and Gemini (Google GenerativeAI)
import openai
import google.generativeai as genai

# Set API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

import re
import difflib

class AgentControlCenter:
    def run_prompt(self, prompt: str, model: str = "openai") -> str:
        if model == "gemini":
            try:
                gemini_model = genai.GenerativeModel("gemini-pro")
                response = gemini_model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                return f"[GEMINI ERROR] {e}"
        else:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"[OPENAI ERROR] {e}"

    def process_agent_instruction(self, instruction: str) -> str:
        # Check for file edit commands
        if "upload.py" in instruction.lower() and "comment" in instruction.lower():
            target_path = "web/routes/upload.py"
            comment = "# 📝 This comment was added by the assistant based on user instruction."

            if "preview" in instruction.lower():
                return self.preview_comment_patch(target_path, comment)

            try:
                with open(target_path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n{comment}\n")
                return f"✅ Comment added to {target_path}"
            except Exception as e:
                return f"❌ Failed to update {target_path}: {e}"

        elif "streaming" in instruction.lower():
            return "✅ Detected request to add streaming token response. Action queued."
        elif "summarize" in instruction.lower():
            return "🧠 Planning summarization integration into docquery."
        elif "auto reload" in instruction.lower():
            return "🔁 Would trigger app reload after changes."
        else:
            return f"🤖 Instruction noted: '{instruction}'. No recognized automation triggered yet."


    def modify_function_in_file(self, file_path: str, function_name: str, new_code: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Regex to find the function definition and its body
            pattern = rf"(def {function_name}\(.*?\):\n)([ \t]+.*\n)+"
            match = re.search(pattern, content)

            if not match:
                return f"❌ Function '{function_name}' not found in {file_path}"

            indent = " " * 4  # default to 4 spaces
            replacement = f"{match.group(1)}{indent}{new_code.strip().replace(chr(10), f'\\n{indent}')}\n"
            updated_content = re.sub(pattern, replacement, content)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            return f"✅ Function '{function_name}' updated in {file_path}"
        except Exception as e:
            return f"❌ Error updating function '{function_name}' in {file_path}: {e}"

    def preview_comment_patch(self, file_path: str, comment: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_lines = f.readlines()

            new_lines = original_lines + ["\n", comment + "\n"]
            diff = difflib.unified_diff(
                original_lines, new_lines,
                fromfile="original", tofile="patched",
                lineterm=""
            )
            return "\n".join(diff)
        except Exception as e:
            return f"❌ Failed to preview diff for {file_path}: {e}"

    def plan_instruction(self, instruction: str) -> dict:
        # Placeholder for future planning logic
        return {"action": "plan_not_implemented", "input": instruction}

    def route_instruction(self, plan: dict) -> str:
        # Placeholder for routing logic
        return "🧭 Routing logic not yet implemented."

    def run_patch_plan(self, plan: dict) -> str:
        # Placeholder for patch execution logic
        return "🔧 Patch execution not yet implemented."

router = APIRouter()

@router.get("/log/query", response_class=PlainTextResponse)
async def query_log():
    log_path = Path("logs/user_log.jsonl")
    if not log_path.exists():
        return "Log file not found."

    with log_path.open("r", encoding="utf-8") as f:
        log_entries = f.readlines()

    prompt = (
        "Summarize the following user activity logs. "
        "Highlight names, ages, and any patterns in the data:\n\n"
        + "".join(log_entries[-20:])
    )

    agent = AgentControlCenter()
    return agent.run_prompt(prompt)
