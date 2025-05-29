import os
import openai
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def check_openai():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        openai.Model.list()
        return True, "OpenAI key valid"
    except Exception as e:
        return False, f"OpenAI error: {str(e)}"

def check_gemini():
    key = os.getenv("GEMINI_API_KEY")
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-pro")
        _ = model.generate_content("Ping")
        return True, "Gemini key valid"
    except Exception as e:
        return False, f"Gemini error: {str(e)}"

if __name__ == "__main__":
    print("🔑 Validating API keys...\n")

    ok_openai, msg_openai = check_openai()
    print("✅" if ok_openai else "❌", msg_openai)

    ok_gemini, msg_gemini = check_gemini()
    print("✅" if ok_gemini else "❌", msg_gemini)
