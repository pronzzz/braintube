import os
import logging
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

def transcribe_audio(audio_path: str, model_size: str = "tiny", compute_type: str = "int8") -> list:
    """
    Transcribes the audio file using faster-whisper.
    Returns a list of dictionaries containing segment details.
    """
    logger.info(f"Loading faster-whisper model '{model_size}'...")
    # By default, use CPU with int8 quantization for broader compatibility.
    model = WhisperModel(model_size, device="cpu", compute_type=compute_type)
    
    logger.info(f"Transcribing {audio_path}...")
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")
    
    results = []
    for segment in segments:
        results.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })
        
    logger.info(f"Transcription complete. Found {len(results)} segments.")
    return results
