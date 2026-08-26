import io
import os
import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

logger = logging.getLogger(__name__)

# Token Text Splitter initialization with fallback
try:
    from langchain_text_splitters import TokenTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import TokenTextSplitter
    except ImportError:
        TokenTextSplitter = None

# Top-level worker functions (must be top-level for ProcessPoolExecutor pickling)

def _extract_pdf_page_worker(args: Tuple[bytes, int, str]) -> Tuple[int, str, str]:
    """
    Worker function executed inside ProcessPoolExecutor (GIL bypassed).
    Extracts text from a single PDF page using PyMuPDF (fitz) with pypdf fallback.
    
    Args:
        args: Tuple of (pdf_bytes, page_number_1_indexed, filename)
        
    Returns:
        Tuple of (page_number, extracted_text, filename)
    """
    pdf_bytes, page_num, filename = args
    extracted_text = ""

    # Strategy 1: High-performance C++ PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if 0 <= page_num - 1 < len(doc):
            extracted_text = doc[page_num - 1].get_text("text") or ""
        doc.close()
    except Exception as e:
        # Strategy 2: pypdf fallback
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            if 0 <= page_num - 1 < len(reader.pages):
                extracted_text = reader.pages[page_num - 1].extract_text() or ""
        except Exception as pypdf_err:
            logger.warning(f"Worker page {page_num} extraction error for {filename}: {pypdf_err}")

    return page_num, extracted_text.strip(), filename

def _chunk_text_worker(args: Tuple[str, Dict[str, Any], int, int]) -> List[Dict[str, Any]]:
    """
    Worker function executed inside ProcessPoolExecutor (GIL bypassed).
    Splits text using subword TokenTextSplitter (default: 256 tokens ~ 1,000 chars, 30 tokens overlap)
    and attaches exact document/section metadata.
    
    Args:
        args: Tuple of (text, base_metadata, chunk_size_tokens, chunk_overlap_tokens)
        
    Returns:
        List of processed chunk dictionaries containing id, content, and metadata.
    """
    text, base_metadata, chunk_size, chunk_overlap = args
    if not text or not text.strip():
        return []

    # Use TokenTextSplitter matching FastEmbed/BAAI subword token boundaries
    if TokenTextSplitter is not None:
        splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        raw_chunks = splitter.split_text(text)
    else:
        # Naive word-level fallback if langchain_text_splitters is unavailable
        words = text.split()
        raw_chunks = []
        step = chunk_size - chunk_overlap
        for i in range(0, len(words), max(1, step)):
            raw_chunks.append(" ".join(words[i:i + chunk_size]))

    processed_chunks = []
    source_name = base_metadata.get("source", "Financial Document")
    sec_or_page = base_metadata.get("page_number", base_metadata.get("section", 0))

    for idx, chunk in enumerate(raw_chunks):
        c_clean = chunk.strip()
        if not c_clean:
            continue

        c_hash = hash(c_clean) & 0xffffffff
        chunk_id = f"{source_name}_chunk_{sec_or_page}_{idx}_{c_hash}"

        chunk_meta = {
            **base_metadata,
            "chunk_id": chunk_id,
            "chunk_index": idx,
            "token_count": len(c_clean.split()),
            "snippet": c_clean[:150] + "..."
        }

        processed_chunks.append({
            "id": chunk_id,
            "content": c_clean,
            "metadata": chunk_meta
        })

    return processed_chunks

class ParallelIngestionPipeline:
    """
    Production-Grade Parallel Document Ingestion & Token Chunking Pipeline.
    Bypasses Python's GIL using ProcessPoolExecutor for concurrent multi-core PDF parsing
    and subword token chunking.
    """
    def __init__(self, max_workers: Optional[int] = None, default_token_chunk_size: int = 256, default_token_overlap: int = 30):
        self.num_cores = max_workers or max(1, multiprocessing.cpu_count() - 1)
        self.chunk_size = default_token_chunk_size
        self.chunk_overlap = default_token_overlap
        logger.info(f"ParallelIngestionPipeline initialized using {self.num_cores} CPU worker processes.")

    def parse_pdf_bytes_parallel(self, pdf_bytes: bytes, filename: str = "document.pdf") -> List[Dict[str, Any]]:
        """
        Extracts text from PDF bytes concurrently across all available CPU cores.
        """
        try:
            import fitz
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            doc.close()
        except Exception:
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                total_pages = len(reader.pages)
            except Exception as e:
                logger.error(f"Could not read PDF structure for {filename}: {e}")
                return []

        if total_pages == 0:
            return []

        tasks = [(pdf_bytes, page_num, filename) for page_num in range(1, total_pages + 1)]
        pages_data = []

        # Single page fast-path (avoid process spawn overhead for 1-page docs)
        if total_pages == 1:
            res = _extract_pdf_page_worker(tasks[0])
            if res[1]:
                pages_data.append({"page_number": res[0], "text": res[1], "source": filename})
            return pages_data

        # Parallel extraction across ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=min(self.num_cores, total_pages)) as executor:
            future_to_page = {executor.submit(_extract_pdf_page_worker, t): t[1] for t in tasks}
            for future in as_completed(future_to_page):
                page_num, text, fname = future.result()
                if text:
                    pages_data.append({
                        "page_number": page_num,
                        "text": text,
                        "source": fname
                    })

        pages_data.sort(key=lambda x: x["page_number"])
        logger.info(f"Extracted {len(pages_data)} pages from '{filename}' concurrently ({self.num_cores} workers).")
        return pages_data

    def chunk_texts_parallel(self, items: List[Tuple[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Splits multiple text blocks / SEC 10-K sections concurrently using subword TokenTextSplitter.
        
        Args:
            items: List of (text_content, base_metadata_dict) tuples.
            
        Returns:
            Flat list of processed chunk dicts (id, content, metadata).
        """
        if not items:
            return []

        tasks = [(text, meta, self.chunk_size, self.chunk_overlap) for text, meta in items]

        # Single item fast-path
        if len(items) == 1:
            return _chunk_text_worker(tasks[0])

        all_chunks = []
        with ProcessPoolExecutor(max_workers=min(self.num_cores, len(items))) as executor:
            futures = [executor.submit(_chunk_text_worker, t) for t in tasks]
            for future in as_completed(futures):
                try:
                    res_chunks = future.result()
                    all_chunks.extend(res_chunks)
                except Exception as e:
                    logger.error(f"Error in parallel chunk worker: {e}")

        logger.info(f"Parallel chunking generated {len(all_chunks)} token-aligned chunks across {len(items)} inputs.")
        return all_chunks

# Global Singleton Pipeline instance
parallel_pipeline = ParallelIngestionPipeline()
