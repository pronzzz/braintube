# BrainTube Technical Guide

## System Architecture

BrainTube consists of an ingestion pipeline and several local intelligence modules wrapped in a Streamlit interface.

### Core Modules

- `app.py`: The Main UI entry point. Coordinates ingestion, querying, and library management tabs.
- `core/ingestion.py`: Invokes `yt-dlp` to download optimal audio strictly for text analysis.
- `core/transcription.py`: Uses `faster-whisper` on local CPU resources to generate transcription mapping dictionaries.
- `core/structuring.py`: Processes and cleans transcripts. Checks for malicious "ignore all previous instructions" commands (prompt injection) and chunks texts semantically.
- `core/rag.py`: Implements a multi-chunk semantic search loop loading contexts into `FAISS`.
- `core/graph.py`: Invokes Ollama to structure data into entities and relationships, outputting to a D3/Cytoscape format template (`graph.html`).
- `core/summarization.py` & `core/study.py`: Prompt wrappers converting unstructured video contexts into summaries, flashcards, or quizzes.
- `core/hardware.py`: A `psutil` integration recommending whisper model sizes and local SLM tiers.
- `core/memory.py`: Stores document metadata into `braintube.sqlite3`.

## Customizing Models

By default, BrainTube detects your RAM and defaults to:
- `< 8GB`: tiny whisper, gemma:2b LLM
- `< 16GB`: base whisper, llama3.2 LLM
- `> 16GB`: small whisper, llama3.2 LLM

You can change these freely in the UI Sidebar. If you wish to pull new local models, ensure you run `ollama pull <model_name>` on your terminal before using it in the application.
