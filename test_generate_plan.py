from web.memory.planner_utils import generate_plan

sample_input = {"prompt": "Deploy a new AI agent to automate file cleanup."}
plan = generate_plan(sample_input)

for step in plan:
    print(f"Step {step['step']}: {step['action']} - {step.get('details', '')}")
