
# plan_executor_combined.py
# Standalone plan executor, compatible with any system and Friday AI agent integration.
import os
import re
import json

# Optional AI imports
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

USE_GEMINI = os.getenv("USE_GEMINI", "true").lower() == "true"
PLAN_STORAGE_FILE = 'web/memory/plans.json'

def generate_plan(prompt):
    prompt = prompt.strip()
    if not prompt:
        return [], "No prompt provided."

    plan = try_ai_generation(prompt)
    if plan:
        return plan, "AI"

    fallback = generate_fallback_plan(prompt)
    return fallback, "fallback"

def try_ai_generation(prompt):
    prompt_block = f"""Create a step-by-step plan for the following goal:
{prompt}

Respond with a numbered list. Each step should include:
- A concise action
- An optional explanation
"""

    if USE_GEMINI and GENAI_AVAILABLE:
        try:
            model = genai.GenerativeModel("gemini-pro")
            result = model.generate_content(prompt_block)
            return parse_plan_text(result.text.strip())
        except Exception as e:
            print(f"[Gemini Error] {e}")

    if OPENAI_AVAILABLE:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt_block}],
                timeout=10
            )
            return parse_plan_text(response.choices[0].message.content.strip())
        except Exception as e:
            print(f"[OpenAI Error] {e}")

    return None

def parse_plan_text(text):
    steps = []
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        match = re.match(r'^\d+\.\s*(.+)', line.strip())
        if match:
            content = match.group(1)
            if " - " in content:
                action, details = content.split(" - ", 1)
            else:
                action, details = content, ""
            steps.append({"step": len(steps)+1, "action": action.strip(), "details": details.strip()})
    return steps

def generate_fallback_plan(prompt):
    return [
        {"step": 1, "action": "Understand the objective", "details": f"Clarify what it means to: {prompt}"},
        {"step": 2, "action": "Break down tasks", "details": "List the required components"},
        {"step": 3, "action": "Organize resources", "details": "Get tools, info, and people"},
        {"step": 4, "action": "Start building", "details": "Begin executing the steps"},
        {"step": 5, "action": "Test and adjust", "details": "Validate progress and iterate"},
        {"step": 6, "action": "Finalize and review", "details": "Document and finish"}
    ]

def store_plan(plan_id, steps):
    path = PLAN_STORAGE_FILE
    if not os.path.exists(path):
        memory = {}
    else:
        with open(path, 'r') as f:
            memory = json.load(f)
    memory[plan_id] = steps
    with open(path, 'w') as f:
        json.dump(memory, f, indent=2)
    return {"status": "stored", "plan_id": plan_id}


# Refactored core logic as reusable function
def generate_and_store_plan(prompt: str):
    prompt = prompt.strip()
    if not prompt:
        return {"error": "No input provided"}
    steps, source = generate_plan(prompt)
    plan_id = prompt[:50].replace(" ", "_").lower()
    result = store_plan(plan_id, steps)
    output = {
        "plan_id": plan_id,
        "source": source,
        "steps": steps,
        "storage": result
    }
    return output

def run():
    user_prompt = input("Enter your planning objective: ").strip()
    if not user_prompt:
        print(json.dumps({"error": "No input provided"}, indent=2))
        return
    output = generate_and_store_plan(user_prompt)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    run()


# Optional API route for agent integration
try:
    from fastapi import APIRouter, Body
    from fastapi.responses import JSONResponse

    router = APIRouter()

    @router.post("/agent/plan")
    async def plan_from_agent(payload: dict = Body(...)):
        prompt = payload.get("prompt", "").strip()
        if not prompt:
            return JSONResponse(status_code=400, content={"error": "Missing 'prompt'"})
        steps, source = generate_plan(prompt)
        plan_id = prompt[:50].replace(" ", "_").lower()
        result = store_plan(plan_id, steps)
        return {
            "plan_id": plan_id,
            "source": source,
            "steps": steps,
            "storage": result
        }

except ImportError:
    pass  # FastAPI not available in CLI mode
