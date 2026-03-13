import requests
import logging

logger = logging.getLogger(__name__)

def generate_study_materials(text: str, material_type: str = "flashcards", model: str = "llama3.2") -> str:
    """
    Generates study materials (flashcards, quizzes, notes) from text using Ollama.
    """
    logger.info(f"Generating {material_type}...")
    
    # Keeping context limits for local AI
    truncated_text = text[:4000]
    
    prompts = {
        "flashcards": "Generate 5 Anki-style flashcards based on the following text. Format as Question // Answer pairs on separate lines.\n\n",
        "quiz": "Generate a 3-question multiple choice quiz with answers based on the following text.\n\n",
        "notes": "Create structured Cornell-style notes based on the following text.\n\n"
    }
    
    prompt = prompts.get(material_type, prompts["flashcards"]) + truncated_text
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        logger.error(f"Error generating study materials: {e}")
        return f"Error: {str(e)}"
