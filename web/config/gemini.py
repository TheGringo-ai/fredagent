import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
genai.configure(api_key=GEMINI_API_KEY)

def stream_gemini_response(prompt: str):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            yield chunk.text
    except Exception as e:
        yield f"\n[Gemini ERROR] {str(e)}"
