import os
import platform
import psutil

def analyze_hardware() -> dict:
    """
    Analyzes local hardware to determine optimal offline model specifications.
    """
    info = {
        "system": platform.system(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count() or 4,
        "ram_gb": round(psutil.virtual_memory().total / (1024.**3), 2)
    }
    
    # Graceful degradation for low-spec systems
    if info["ram_gb"] < 8.0:
        info["recommendation"] = "Low Spec Mode: Recommend 'tiny' Whisper and 'gemma:2b' or 'qwen:0.5b' LLM."
        info["whisper_model"] = "tiny"
        info["llm"] = "gemma:2b"
    elif info["ram_gb"] <= 16.0:
        info["recommendation"] = "Mid Spec Mode: Recommend 'base' Whisper and 'llama3.2' LLM."
        info["whisper_model"] = "base"
        info["llm"] = "llama3.2"
    else:
        info["recommendation"] = "High Spec Mode: Recommend 'small'/'medium' Whisper and 'llama3.2' or 'mixtral'."
        info["whisper_model"] = "small"
        info["llm"] = "llama3.2"
        
    return info
