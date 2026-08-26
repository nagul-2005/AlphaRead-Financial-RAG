import io
import logging
from typing import List, Dict, Any
from parallel_ingestion import parallel_pipeline

logger = logging.getLogger(__name__)

def extract_text_from_pdf_bytes(pdf_bytes: bytes, filename: str = "document.pdf") -> List[Dict[str, Any]]:
    """
    Extracts text from PDF bytes concurrently across all available CPU cores
    using PyMuPDF (fitz) with pypdf and pdfplumber fallbacks.
    """
    try:
        pages_data = parallel_pipeline.parse_pdf_bytes_parallel(pdf_bytes, filename=filename)
        if pages_data:
            return pages_data
    except Exception as e:
        logger.warning(f"Parallel PDF extraction encountered warning for '{filename}': {e}. Running sequential fallback...")

    pages_data = []
    
    # Fallback 1: pypdf
    try:
        import pypdf
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
    except Exception as pypdf_err:
        logger.warning(f"pypdf extraction failed for {filename}: {pypdf_err}")

    # Fallback 2: pdfplumber
    if not pages_data:
        try:
            import pdfplumber
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
        except Exception as plumber_err:
            logger.error(f"pdfplumber extraction failed for {filename}: {plumber_err}")
            raise ValueError(f"Could not extract readable text from PDF '{filename}'.")

    return pages_data
