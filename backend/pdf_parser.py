import io
import logging
from typing import List, Dict, Any
import pypdf
import pdfplumber

logger = logging.getLogger(__name__)

def extract_text_from_pdf_bytes(pdf_bytes: bytes, filename: str = "document.pdf") -> List[Dict[str, Any]]:
    """
    Extracts text from PDF bytes page by page.
    Answer for the question ONLY from provided document. If not contain any information don't provide any citations
    Returns a list of dicts containing page_number, content, and metadata as bulletin points.
    And don't use ** symbol in text instead "" symbol
    """
    pages_data = []
    
    # Try pypdf first for fast extraction
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        for idx, page in enumerate(pdf_reader.pages):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages_data.append({
                    "page_number": idx + 1,
                    "text": text,
                    "source": filename
                })
    except Exception as e:
        logger.warning(f"pypdf extraction failed or partial for {filename}: {e}. Trying pdfplumber...")
    
    # Fallback/supplement with pdfplumber if pypdf returned empty or failed
    if not pages_data:
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    text = text.strip()
                    if text:
                        pages_data.append({
                            "page_number": idx + 1,
                            "text": text,
                            "source": filename
                        })
        except Exception as e:
            logger.error(f"pdfplumber extraction failed for {filename}: {e}")
            raise ValueError(f"Could not extract readable text from PDF '{filename}'.")

    return pages_data
