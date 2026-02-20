# ⚽ FIFA World Cup AI Analyst

An AI-powered FIFA World Cup analytics platform using RAG architecture, LLM integration, and a Next.js full-stack interface.

## Tech Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI
- **RAG**: LangChain, ChromaDB, Sentence Transformers
- **LLM**: Groq API (Llama 3.1) — 100% free
- **Data**: FIFA World Cup dataset (Kaggle)

## Features
- Ask natural language questions about World Cup history
- RAG pipeline retrieves relevant data before answering
- No hallucination — LLM only uses retrieved context

## Setup

### 1. Clone the repo
git clone https://github.com/sachin199914/fifa-ai-analyst
cd fifa-ai-analyst

### 2. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn groq chromadb sentence-transformers pandas scikit-learn python-dotenv

### 3. Add Environment Variables
Create a `.env` file in the project root:
GROQ_API_KEY=your_groq_api_key_here
Get your free key at: https://console.groq.com

### 4. Download Data
Download FIFA World Cup dataset from Kaggle and place CSVs in /data folder.
Then run:
python scripts/clean_data.py
python scripts/create_chunks.py
python scripts/ingest_to_chromadb.py

### 5. Run Backend
cd backend
uvicorn main:app --reload --port 8000

### 6. Run Frontend
cd frontend
npm install
npm run dev

Open http://localhost:3000