from google import genai

from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

def get_answer_from_gemini(prompt: str):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    return response.text

