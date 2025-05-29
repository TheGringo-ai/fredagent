import google.generativeai as genai

def diagnose_traceback(traceback: str) -> dict:
    """
    Use Gemini Pro to diagnose a Python traceback and return a summary and code patch suggestion.

    Returns:
        dict: {"summary": str, "patch": str}
    """
    prompt = f"""
You're an expert Python debugger. Given the following traceback, identify the root cause and suggest a specific fix.

Traceback:
{traceback}

Return your output in this format:

Summary:
<one-line fix explanation>

Patch:
```python
<code snippet that should be inserted or updated>
```
"""

    model = genai.GenerativeModel("gemini-pro")
    try:
        response = model.generate_content(prompt)
        output = response.text.strip()
    except Exception as e:
        return {
            "summary": "Failed to generate response.",
            "patch": f"Error: {str(e)}"
        }

    summary, patch = "", ""
    if "Summary:" in output and "Patch:" in output:
        parts = output.split("Patch:")
        summary = parts[0].replace("Summary:", "").strip()
        patch = parts[1].strip()
    else:
        summary = "Could not parse structured output."
        patch = output

    return {"summary": summary, "patch": patch}