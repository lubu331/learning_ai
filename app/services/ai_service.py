import requests
from app.services.pdf_service import extract_text_from_pdf
import json

OLLAMA_URL = "http://localhost:11434/api/generate"  # Default Ollama port


def generate_quiz_from_text(text: str, topic: str, grade: str) -> dict:
    prompt = f"""You are an educational assistant. 
    Based on the following text, generate 5 multiple-choice questions for a {grade} student studying '{topic}'.

    Format strictly as JSON array of objects:
    [
        {{ "question": "...", "options": ["A", "B", "C", "D"], "answer": "A" }}
    ]

    Text content:
    {text[:2000]}"""  # Limiting context for local demo

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "llama3",  # Ensure you have llama3 pulled in Ollama
            "prompt": prompt,
            "stream": False
        })

        if response.status_code == 200:
            result = response.json()
            # Parse the JSON string from the LLM output
            questions_data = json.loads(result['response'])
            return {"success": True, "questions": questions_data}
        else:
            return {"success": False, "error": "Local AI connection failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_quiz_from_file(file_path: str, topic: str, grade: str) -> dict:
    text = extract_text_from_pdf(file_path)
    if not text or "Error" in text:
        return {"success": False, "error": "Could not read PDF"}

    return generate_quiz_from_text(text, topic, grade)