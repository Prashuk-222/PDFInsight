from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from slowapi.util import get_remote_address
from pydantic import BaseModel
from typing import Dict
import numpy as np
import fitz  # PyMuPDF
import tempfile
import os


app = FastAPI()

templates = Jinja2Templates(directory="templates")

os.environ["GOOGLE_API_KEY"] = "AIzaSyCPKyxAyjqT-oRG-GLE80zC5VdcGw6F7sI"

#Embedding Model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

active_sessions: Dict[str, Dict] = {}


@app.get("/")
async def upload_page(request: Request):
    """Render the PDF upload page."""
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    """Handle PDF upload, extract text, and redirect to Q&A page."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    # Extract text from the PDF using PyMuPDF
    pdf_text = ""
    with fitz.open(temp_file_path) as doc:
        for page in doc:
            pdf_text += page.get_text()

    # Generate embeddings
    pdf_embedding = embedding_model.embed_query(text=pdf_text)

    # Generate a unique session ID
    session_id = file.filename.split('.')[0]
    active_sessions[session_id] = {
        "pdf_text": pdf_text,
        "pdf_embedding": pdf_embedding,
        "history": []
    }

    # Clean up temporary file
    os.remove(temp_file_path)

    # Redirect to Q&A page with the session_id
    return RedirectResponse(url=f"/question-answer/{session_id}", status_code=303)

@app.get("/question-answer/{session_id}")
async def question_answer_page(request: Request, session_id: str):
    """Render the Q&A page with WebSocket connection."""
    if session_id not in active_sessions:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("qa.html", {"request": request, "session_id": session_id})

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time Q&A with embeddings."""
    await websocket.accept()
    
    # Ensure session exists
    session_data = active_sessions.get(session_id)
    if not session_data:
        await websocket.send_text("Session not found or PDF not uploaded.")
        await websocket.close()
        return

    pdf_embedding = session_data["pdf_embedding"]
    pdf_text = session_data["pdf_text"]
    session_history = session_data["history"]

    try:
        while True:
            # Receive question from WebSocket
            question = await websocket.receive_text()
            session_history.append({"role": "user", "content": question})

            # Generate an embedding for the question
            question_embedding = embedding_model.embed_query(text=question)

            relevant_text = find_relevant_text(pdf_text, question)

            # Determine response based on the relevance of the text found
            if relevant_text:
                answer = relevant_text
            else:
                answer = "No relevant information found in the PDF for your question."

            # Send the answer back to the WebSocket
            await websocket.send_text(answer)
            
            # Append answer to session history
            session_history.append({"role": "assistant", "content": answer})

    except WebSocketDisconnect:
        # Clean up session data on WebSocket disconnect
        active_sessions.pop(session_id, None)

def find_relevant_text(pdf_text: str, question: str) -> str:
    """Simple keyword matching to find relevant text in the PDF."""
    # You could implement more advanced text search logic here
    # For now, we'll return the first sentence that contains any keyword from the question.
    question_keywords = question.split()
    sentences = pdf_text.split('. ')  # Split the text into sentences
    
    for sentence in sentences:
        if any(keyword.lower() in sentence.lower() for keyword in question_keywords):
            return sentence.strip()  # Return the first relevant sentence

    return ""  # Return empty if no relevant text is found