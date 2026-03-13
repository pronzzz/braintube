import os
import yt_dlp
import logging

logger = logging.getLogger(__name__)

def download_audio(url: str, output_dir: str = "downloads") -> str:
    """
    Downloads the audio from a YouTube video using yt-dlp.
    Returns the path to the downloaded audio file (.mp3).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'quiet': False
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get('id', 'unknown')
        expected_filename = os.path.join(output_dir, f"{video_id}.mp3")
        
        if os.path.exists(expected_filename):
            logger.info(f"Audio downloaded to {expected_filename}")
            return expected_filename
        else:
            raise FileNotFoundError(f"Failed to find downloaded file at {expected_filename}")
