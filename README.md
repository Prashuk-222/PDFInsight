# PDF Q&A Backend Service

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
---

## Project Overview

This project is a backend service that allows users to upload PDF documents and ask questions about the content in real-time. It uses FastAPI for handling API requests, WebSocket for real-time interactions, and natural language processing (NLP) with LangChain or LlamaIndex for analyzing and answering questions based on the PDF content.

### Key Features
- **PDF Upload**: Upload and store PDF documents on the server.
- **Real-Time Q&A**: Use WebSocket to ask questions related to PDF content and receive instant answers.
- **Session-Based Context**: Maintains the session's context for follow-up questions within the WebSocket session.
- **Rate Limiting**: Limits excessive requests to prevent abuse.
- **Testing Suite**: Comprehensive tests for endpoints, WebSocket functionality, and rate limiting.

---

## Architecture

This backend service is structured with FastAPI as the main framework. Key components include:

- **FastAPI**: Main framework for handling API requests and WebSocket communication.
- **SQLite/PostgreSQL**: Database to store document metadata and extracted text.
- **Local Storage / AWS S3**: For storing uploaded PDF files.
- **LangChain/LlamaIndex**: NLP processing for generating answers to questions based on PDF content.
- **PyMuPDF**: PDF text extraction library.
- **Redis**: Used for rate limiting (if using FastAPI-Limiter).

## Technologies Used

- **Backend Framework**: FastAPI with WebSocket support
- **Database**: SQLite or PostgreSQL
- **File Storage**: Local filesystem (or AWS S3 for cloud storage)
- **NLP Processing**: LangChain or LlamaIndex
- **Rate Limiting**: Redis and FastAPI-Limiter
- **Testing**: Pytest

---

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- Virtual environment manager (e.g., `venv`)
- Redis (for rate limiting, optional)

### Step 1: Clone the Repository
```bash
git clone <repository_url>
cd pdf-qa-backend
```
### Step 2: Create a Virtual Environment and Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```
### Step 3: Configure the Database
- Update DATABASE_URL in models.py for SQLite or PostgreSQL.
- Initialize the database:
```bash
from models import Base, engine
Base.metadata.create_all(bind=engine)
```
### Step 4: Run the Server
```bash
uvicorn main:app --reload
```
In main.py, initialize FastAPI-Limiter with Redis.

