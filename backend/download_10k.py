#!/usr/bin/env python3
"""
AlphaRead - SEC EDGAR 10-K Dataset Auto-Downloader Script
Downloads 10-K financial reports (MD&A and Risk Factors) directly from SEC EDGAR
for a list of stock tickers and saves them locally in ./dataset/sec_10k/
Optionally auto-ingests reports into ChromaDB vector database.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SEC_Downloader")

# Import SEC parser module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sec_parser import fetch_sec_10k

DATASET_DIR = Path(__file__).parent / "dataset" / "sec_10k"

def download_ticker_10k(ticker: str, output_dir: Path) -> dict:
    """Downloads 10-K sections for a single ticker and saves to disk."""
    logger.info(f"Downloading 10-K report for ticker: {ticker.upper()}...")
    try:
        data = fetch_sec_10k(ticker)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / f"{ticker.upper()}_10K.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
            
        logger.info(f"Successfully saved 10-K data for {ticker.upper()} -> {filepath}")
        return data
    except Exception as e:
        logger.error(f"Failed to download 10-K for {ticker.upper()}: {e}")
        return {}

def download_dataset(tickers: list, output_dir: Path = DATASET_DIR, ingest_to_chroma: bool = False):
    """Downloads 10-K reports for multiple tickers and optionally ingests them into RAG DB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Starting SEC 10-K dataset download for {len(tickers)} tickers: {', '.join(tickers)}")
    
    downloaded_records = []
    for ticker in tickers:
        data = download_ticker_10k(ticker, output_dir)
        if data:
            downloaded_records.append(data)
            
    logger.info(f"Finished downloading {len(downloaded_records)}/{len(tickers)} 10-K reports into {output_dir}")
    
    if ingest_to_chroma and downloaded_records:
        logger.info("Auto-ingesting downloaded 10-K dataset into ChromaDB...")
        try:
            from rag_service import rag_engine
            total_chunks = 0
            for record in downloaded_records:
                for section in record.get("sections", []):
                    chunks = rag_engine.ingest_text(
                        text=section["text"],
                        source_name=f"{record['ticker']}_10K_{section['section_name']}",
                        metadata={
                            "ticker": record["ticker"],
                            "company_name": record.get("company_name", record["ticker"]),
                            "section": section["section_name"],
                            "doc_type": "SEC_10K"
                        }
                    )
                    total_chunks += chunks
            logger.info(f"Successfully auto-ingested dataset into ChromaDB ({total_chunks} total chunks created).")
        except Exception as e:
            logger.error(f"Error during ChromaDB auto-ingestion: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AlphaRead SEC EDGAR 10-K Dataset Downloader")
    parser.add_argument(
        "--tickers", 
        nargs="+", 
        default=["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "TSLA"],
        help="List of stock tickers to download 10-K reports for (default: AAPL MSFT NVDA AMZN GOOGL TSLA)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default=str(DATASET_DIR),
        help="Directory path to save dataset files"
    )
    parser.add_argument(
        "--ingest", 
        action="store_true", 
        help="Automatically ingest downloaded dataset into ChromaDB vector database"
    )
    
    args = parser.parse_args()
    download_dataset(
        tickers=[t.upper() for t in args.tickers],
        output_dir=Path(args.output),
        ingest_to_chroma=args.ingest
    )
