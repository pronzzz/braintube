<div align="center">
  <h1>🧠 BrainTube</h1>
  <p><strong>The Video That Talks Back. Local, offline, private.</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://www.python.org/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-ff4b4b.svg)](https://streamlit.io/)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Local AI](https://img.shields.io/badge/Local%20AI-Ollama-white.svg)](https://ollama.com/)
</div>

---

## Overview

BrainTube is a fully local, privacy-first YouTube intelligence system. It transforms video content into structured, queryable knowledge entirely on your own hardware without relying on cloud APIs.

By combining `yt-dlp`, local `faster-whisper` transcription, FAISS embeddings, and local language models via Ollama, BrainTube creates an offline "second brain" out of YouTube.

## Features

- **Offline-First Processing**: Downloads, transcribes, and summarizes videos locally.
- **Conversational Memory**: Chat with video transcripts via RAG using FAISS.
- **Semantic Knowledge Graph**: Generates interactive graphs (people, concepts, technologies) using local SLMs.
- **Study Mode**: Auto-generate flashcards, quizzes, and Cornell-style notes.
- **Multi-Video Library**: Save processed data into a local SQLite memory engine.
- **Hardware-Adaptive**: Automatically recommends model configurations based on system RAM via `psutil`.

## Installation

### Prerequisites
1. **Python 3.9+**
2. **[Ollama](https://ollama.com/)** running locally (default: `localhost:11434`)
3. Optional: `ffmpeg` installed on your system (often required by `yt-dlp`).

### Setup

```bash
# Clone the repository
git clone https://github.com/pronzzz/braintube.git
cd braintube

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install yt-dlp faster-whisper streamlit faiss-cpu langchain-community sentence-transformers psutil networkx
```

## Quick Start

1. Start your local Ollama instance (ensure models like `llama3.2` are pulled):
   ```bash
   ollama pull llama3.2
   ```

2. Run the BrainTube Streamlit interface:
   ```bash
   streamlit run app.py
   ```

3. Paste a YouTube URL into the "Ingest" tab and let your local AI do the rest.

## Documentation

- [Project Guide](GUIDE.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## Technology Stack

- **Audio/Video**: `yt-dlp`
- **Transcription**: `faster-whisper` (CTranslate2 backend)
- **Vector Search**: `langchain`, `FAISS`
- **Local LLM Inference**: `Ollama`
- **Interface**: `Streamlit`
- **Database**: `SQLite`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
