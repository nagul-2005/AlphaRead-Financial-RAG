import os
import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AlphaRead_Backend")

from pdf_parser import extract_text_from_pdf_bytes
from sec_parser import fetch_sec_10k
from rag_service import rag_engine
from download_10k import download_dataset

app = FastAPI(
    title="AlphaRead Financial GenAI RAG API",
    description="Backend API for PDF ingestion, SEC 10-K report parsing, ChromaDB vector retrieval, and Groq Llama-3 chat reasoning.",
    version="1.0.0"
)

# CORS setup to allow React frontend (Vercel production & local dev)
origins = [
    "https://alpha-read-financial.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class SecIngestRequest(BaseModel):
    ticker: str
    sections: Optional[List[str]] = ["Item 1A", "Item 7"]

class DatasetDownloadRequest(BaseModel):
    tickers: List[str]
    auto_ingest: bool = True

class ChatRequest(BaseModel):
    message: str

# Endpoints
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "app": "AlphaRead Financial GenAI",
        "groq_configured": bool(rag_engine.groq_client)
    }

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Accepts PDF file, extracts text, chunks using LangChain splitter, and stores vectors in ChromaDB."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        pdf_bytes = await file.read()
        pages_data = extract_text_from_pdf_bytes(pdf_bytes, filename=file.filename)
        
        if not pages_data:
            raise HTTPException(status_code=400, detail="No readable text found in PDF.")
            
        total_chunks = 0
        for page in pages_data:
            chunks = rag_engine.ingest_text(
                text=page["text"],
                source_name=f"{file.filename} (Page {page['page_number']})",
                metadata={
                    "page_number": page["page_number"],
                    "source_file": file.filename,
                    "doc_type": "PDF"
                }
            )
            total_chunks += chunks
            
        return {
            "status": "success",
            "message": f"Successfully processed '{file.filename}'.",
            "pages_processed": len(pages_data),
            "chunks_created": total_chunks
        }
    except Exception as e:
        logger.error(f"Error uploading PDF {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest-sec")
async def ingest_sec(request: SecIngestRequest):
    """Fetches SEC 10-K report for stock ticker and extracts requested sections."""
    ticker = request.ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol is required.")
        
    try:
        requested_secs = request.sections if request.sections else ["Item 1A", "Item 7"]
        sec_data = fetch_sec_10k(ticker, requested_sections=requested_secs)
        total_chunks = 0
        
        for section in sec_data.get("sections", []):
            chunks = rag_engine.ingest_text(
                text=section["text"],
                source_name=f"{ticker}_10K_{section['section_name']}",
                metadata={
                    "ticker": ticker,
                    "company_name": sec_data.get("company_name", ticker),
                    "section": section["section_name"],
                    "doc_type": "SEC_10K"
                }
            )
            total_chunks += chunks
            
        return {
            "status": "success",
            "ticker": ticker,
            "company_name": sec_data.get("company_name", ticker),
            "filing_date": sec_data.get("filing_date", "Latest"),
            "sections_ingested": len(sec_data.get("sections", [])),
            "chunks_created": total_chunks
        }
    except Exception as e:
        logger.error(f"Error fetching SEC 10-K for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{source_name:path}")
async def delete_single_document(source_name: str):
    """Deletes all vector embeddings for a specific source document."""
    try:
        success = rag_engine.delete_document(source_name)
        if success:
            return {"status": "success", "message": f"Successfully deleted document '{source_name}'."}
        else:
            raise HTTPException(status_code=404, detail=f"Document '{source_name}' not found.")
    except Exception as e:
        logger.error(f"Error deleting document {source_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download-dataset")
async def download_sec_dataset(request: DatasetDownloadRequest, background_tasks: BackgroundTasks):
    """Triggers downloading SEC 10-K dataset for specified tickers."""
    tickers = [t.strip().upper() for t in request.tickers if t.strip()]
    if not tickers:
        raise HTTPException(status_code=400, detail="At least one ticker is required.")
        
    try:
        # Run download in background or synchronously if few
        from pathlib import Path
        output_dir = Path(__file__).parent / "dataset" / "sec_10k"
        
        download_dataset(tickers=tickers, output_dir=output_dir, ingest_to_chroma=request.auto_ingest)
        
        return {
            "status": "success",
            "message": f"Downloaded and processed 10-K dataset for tickers: {', '.join(tickers)}",
            "tickers": tickers
        }
    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """RAG chat endpoint: retrieves top 3 chunks from ChromaDB, constructs prompt, calls Groq API (Llama-3)."""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="User message cannot be empty.")
        
    try:
        response_data = rag_engine.chat(query=request.message)
        return response_data
    except Exception as e:
        logger.error(f"Error processing chat query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def get_documents():
    """Returns list of all ingested documents in ChromaDB vectorstore."""
    try:
        docs = rag_engine.list_documents()
        return {"documents": docs, "total_documents": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear")
async def clear_database():
    """Clears the vector store."""
    try:
        rag_engine.clear_database()
        return {"status": "success", "message": "Vector database cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
