import requests
import json
import logging

logger = logging.getLogger(__name__)

# Assuming standard default local Ollama port
OLLAMA_API_URL = "http://localhost:11434/api/generate"
# Using llama3.2 as a good default for 2026 local specs, falling back to any available small model like gemma:2b if instructed
DEFAULT_MODEL = "llama3.2" 

def summarize_text(text: str, model: str = DEFAULT_MODEL, summary_type: str = "global") -> str:
    """
    Summarizes the text using local Ollama model.
    summary_type can be: global, bullet, executive
    """
    logger.info(f"Generating {summary_type} summary using {model} directly through Ollama API...")
    
    prompts = {
        "global": "Provide a comprehensive global summary of the following video transcript:\n\n",
        "bullet": "Provide a bullet-point summary of the key takeaways from the following video transcript:\n\n",
        "executive": "Provide a high-level executive summary of the following video transcript:\n\n"
    }
    
    prompt = prompts.get(summary_type, prompts["global"]) + text
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.ConnectionError:
        error_msg = "Error connecting to Ollama. Ensure Ollama is running locally on port 11434."
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        logger.error(f"Error communicating with Ollama: {e}")
        return f"Error generation summary: {str(e)}"
