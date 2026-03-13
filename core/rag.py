import logging
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import requests

logger = logging.getLogger(__name__)

# Single instance of embedding model initialized lazily
_embeddings_model = None

def get_embeddings_model():
    global _embeddings_model
    if _embeddings_model is None:
        logger.info("Initializing HuggingFace embeddings on CPU...")
        _embeddings_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2", 
            model_kwargs={'device': 'cpu'}
        )
    return _embeddings_model

def build_vector_store(structured_chunks: list) -> FAISS:
    """
    Builds an in-memory FAISS vector store from structured chunks.
    """
    logger.info(f"Building FAISS vector store for {len(structured_chunks)} chunks...")
    chunks_text = [chunk['text'] for chunk in structured_chunks]
    metadatas = [{"start": chunk['start'], "end": chunk['end']} for chunk in structured_chunks]
    
    embeddings = get_embeddings_model()
    vectorstore = FAISS.from_texts(chunks_text, embeddings, metadatas=metadatas)
    return vectorstore

def generate_rag_response(query: str, vectorstore: FAISS, model: str = "llama3.2") -> dict:
    """
    Retrieves the most relevant chunks and passes them to the local Ollama LLM
    to answer the query.
    """
    logger.info(f"Retrieving chunks for query: '{query}'")
    docs = vectorstore.similarity_search(query, k=4)
    
    context = ""
    sources = []
    
    for i, doc in enumerate(docs):
        start = doc.metadata.get("start", 0)
        end = doc.metadata.get("end", 0)
        context += f"[Excerpt {i+1} - Timestamp: {start:.2f}s to {end:.2f}s]\n{doc.page_content}\n\n"
        sources.append({"start": start, "end": end, "text": doc.page_content})
        
    prompt = f"""You are an intelligent video assistant. Answer the user's question using ONLY the provided excerpts from the video transcript.
If the answer is not contained in the excerpts, say "I don't have enough context in the video to answer that."
When answering, reference the timestamps if relevant.

EXCERPTS:
{context}

QUESTION: {query}
ANSWER:"""

    logger.info("Generating response from local LLM...")
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    answer = "Error generating response."
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        answer = response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        error_msg = "Error connecting to Ollama. Ensure Ollama is running locally on port 11434."
        logger.error(error_msg)
        answer = error_msg
    except Exception as e:
        logger.error(f"Error communicating with Ollama: {e}")
        answer = f"Error: {e}"
        
    return {"answer": answer, "sources": sources}
