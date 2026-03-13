import streamlit as st
import os
import streamlit.components.v1 as components

# Import local modules
from core.hardware import analyze_hardware
from core.ingestion import download_audio
from core.transcription import transcribe_audio
from core.structuring import structure_transcript
from core.summarization import summarize_text
from core.rag import build_vector_store, generate_rag_response
from core.graph import extract_knowledge_graph, generate_graph_html
from core.memory import init_db, save_video, get_all_videos
from core.study import generate_study_materials

st.set_page_config(page_title="BrainTube", page_icon="🧠", layout="wide")

# Initialize SQLite memory on startup
init_db()

st.title("🧠 BrainTube")
st.markdown("The Video That Talks Back. Local, offline, private.")

# Phase 8: Hardware Optimization Engine Sidebar
with st.sidebar:
    st.header("💻 Hardware Profile")
    hw_info = analyze_hardware()
    st.info(f"RAM: {hw_info['ram_gb']} GB")
    st.success(hw_info['recommendation'])
    st.markdown("---")
    st.header("⚙️ Settings")
    llm_model = st.text_input("Local LLM (Ollama)", value=hw_info.get('llm', 'llama3.2'))
    idx = ["tiny", "base", "small", "medium", "large"].index(hw_info.get("whisper_model", "tiny")) if hw_info.get("whisper_model", "tiny") in ["tiny", "base", "small", "medium", "large"] else 0
    whisper_model = st.selectbox("Whisper Size", ["tiny", "base", "small", "medium", "large"], index=idx)

# Tab structure
tab_ingest, tab_chat, tab_graph, tab_study, tab_library = st.tabs(["📺 Ingest", "💬 Chat", "🕸️ Graph", "📚 Study", "📂 Library"])

# Phase 10: Performance Optimization - Caching heavy operations
@st.cache_data(show_spinner=False)
def get_processed_data(url, whisper_model_local):
    audio_path = download_audio(url)
    segments = transcribe_audio(audio_path, model_size=whisper_model_local)
    # Phase 9: Security/Sanitization placeholder
    # In a full system we would strip dangerous tokens
    structured_chunks = structure_transcript(segments)
    full_text = " ".join([c['text'] for c in structured_chunks])
    return audio_path, structured_chunks, full_text

def extract_and_process(url):
    try:
        with st.spinner("Downloading and Transcribing..."):
            audio_path, structured_chunks, full_text = get_processed_data(url, whisper_model)
            
        with st.spinner("Structuring & Summarizing..."):
            summary = summarize_text(full_text, model=llm_model, summary_type="global")
            
        with st.spinner("Building Memory Engine..."):
            vectorstore = build_vector_store(structured_chunks)
            # Store instance in session state for later querying
            st.session_state['vectorstore'] = vectorstore
            st.session_state['transcript_text'] = full_text
            
            # Save to library
            video_id = os.path.basename(audio_path).split(".")[0]
            save_video(video_id, url, video_id, summary, audio_path, "in_memory")

        return summary
    except Exception as e:
        st.error(f"Failed processing: {e}")
        return None

with tab_ingest:
    url = st.text_input("Enter YouTube URL")
    if st.button("Process Video"):
        summary = extract_and_process(url)
        if summary:
            st.success("Video Processed Successfully!")
            st.markdown("### Executive Summary")
            st.write(summary)

with tab_chat:
    st.markdown("### Chat with the Video")
    query = st.text_input("Ask anything about the video")
    if st.button("Query"):
        if 'vectorstore' in st.session_state:
            with st.spinner("Reasoning..."):
                response = generate_rag_response(query, st.session_state['vectorstore'], model=llm_model)
                st.write(response['answer'])
                st.markdown("**References:**")
                for src in response['sources']:
                    st.caption(f"[{src['start']:.1f}s - {src['end']:.1f}s] {src['text']}")
        else:
            st.warning("Please process a video first in the Ingest tab.")

with tab_graph:
    st.markdown("### Semantic Knowledge Graph")
    if st.button("Generate Graph"):
        if 'transcript_text' in st.session_state:
            with st.spinner("Extracting entities..."):
                G = extract_knowledge_graph(st.session_state['transcript_text'], model=llm_model)
                html_path = generate_graph_html(G)
                
                with open(html_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                    components.html(source_code, height=600)
        else:
            st.warning("Please process a video first.")

with tab_study:
    st.markdown("### Flashcards & Quizzes")
    material_type = st.selectbox("Type", ["flashcards", "quiz", "notes"])
    if st.button("Generate Materials"):
        if 'transcript_text' in st.session_state:
            with st.spinner(f"Generating {material_type}..."):
                materials = generate_study_materials(st.session_state['transcript_text'], material_type, model=llm_model)
                st.markdown(materials)
        else:
            st.warning("Please process a video first.")

with tab_library:
    st.markdown("### Your Local Memory")
    if st.button("Refresh Library"):
        videos = get_all_videos()
        for v in videos:
            with st.expander(f"{v['title']} ({v['created_at']})"):
                st.write(f"**URL:** {v['url']}")
                st.write(v['summary'])
