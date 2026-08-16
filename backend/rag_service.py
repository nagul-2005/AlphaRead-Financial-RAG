import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
from groq import Groq
from rank_bm25 import BM25Okapi
from relevance import calibrate_bge_reranker_score, fastembed_relevance_score

# Explicitly load .env file from backend folder
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)
load_dotenv()  # Fallback search

logger = logging.getLogger(__name__)

# Configurable RERANKED Top-K candidate count for LLM context
TOP_K_RERANKED = int(os.getenv("TOP_K_RERANKED", "3"))

# HuggingFace Embeddings loader using fastembed (ONNX runtime, <60MB RAM) with sentence-transformers fallback
class HuggingFaceEmbeddingFunction:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        logger.info(f"Loading embedding engine for '{model_name}'...")
        self.fast_model = None
        self.st_model = None
        
        try:
            from fastembed import TextEmbedding
            self.fast_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            logger.info("FastEmbed ONNX lightweight embedding engine initialized (<60MB RAM).")
        except Exception as e:
            logger.warning(f"FastEmbed init failed ({e}). Trying sentence-transformers fallback...")
            try:
                from sentence_transformers import SentenceTransformer
                self.st_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as fallback_err:
                logger.error(f"SentenceTransformer fallback failed: {fallback_err}")

    def encode(self, texts: List[str]) -> np.ndarray:
        if self.fast_model:
            embeddings_generator = self.fast_model.embed(texts)
            return np.array(list(embeddings_generator), dtype=np.float32)
        elif self.st_model:
            return self.st_model.encode(texts, convert_to_numpy=True)
        else:
            logger.warning("Using basic hash embedding fallback.")
            vectors = []
            for t in texts:
                np.random.seed(abs(hash(t)) % (2**32 - 1))
                vectors.append(np.random.randn(384).astype(np.float32))
            return np.array(vectors, dtype=np.float32)

# BM25 Keyword Search Index Manager
class BM25IndexManager:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.bm25: Optional[BM25Okapi] = None

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def rebuild_index(self, documents: List[Dict[str, Any]]):
        self.documents = documents
        if not documents:
            self.bm25 = None
            return

        corpus = [self._tokenize(doc["content"]) for doc in documents]
        self.bm25 = BM25Okapi(corpus)
        logger.info(f"BM25 index built with {len(documents)} document chunks.")

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        if not self.bm25 or not self.documents:
            return []

        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:min(top_k, len(self.documents))]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score > 0:
                doc_copy = dict(self.documents[idx])
                doc_copy["bm25_score"] = score
                results.append(doc_copy)

        return results

# Cross-Encoder Reranker Manager (ONNX FastEmbed for <50MB RAM on Render)
class CrossEncoderReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model_name = model_name
        self.fast_reranker = None
        self.st_reranker = None
        self._load_model()

    def _load_model(self):
        try:
            from fastembed.rerank.cross_encoder import TextReRanker
            logger.info("Initializing FastEmbed ONNX TextReRanker ('BAAI/bge-reranker-base') for low RAM footprint (<50MB)...")
            self.fast_reranker = TextReRanker(model_name="BAAI/bge-reranker-base")
            logger.info("FastEmbed ONNX TextReRanker initialized successfully.")
        except Exception as e:
            logger.warning(f"FastEmbed TextReRanker init failed ({e}). Trying sentence-transformers fallback...")
            try:
                from sentence_transformers import CrossEncoder
                self.st_reranker = CrossEncoder("BAAI/bge-reranker-base", max_length=512)
                logger.info("SentenceTransformer CrossEncoder loaded successfully.")
            except Exception as e2:
                logger.warning(f"CrossEncoder fallback bypassed ({e2}). Using RRF score ranking.")

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = TOP_K_RERANKED) -> List[Dict[str, Any]]:
        if not candidates:
            return []

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = TOP_K_RERANKED) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        def compute_true_score(
            cand: Dict[str, Any],
            raw_rerank_s: Optional[float] = None,
            *,
            score_is_probability: bool = False
        ) -> float:
            """
            Computes exact relevance match score using BGE CrossEncoder logit calibration.
            BGE decision threshold center is ~ 2.0.
            - Unrelated queries (raw logit ~ 0.0 or negative) -> < 15% match.
            - Highly relevant queries (raw logit ~ +4.0) -> > 85% match.
            """
            d_s = float(cand.get("dense_score", 0.0))

            if raw_rerank_s is not None:
                calibrated = calibrate_bge_reranker_score(
                    raw_rerank_s,
                    score_is_probability=score_is_probability
                )
                if calibrated is not None:
                    return calibrated

            # Use true dense vector cosine similarity
            if d_s > 0.0:
                return round(min(0.99, max(0.02, d_s)), 3)

            # BM25 keyword score fallback
            bm25_s = float(cand.get("bm25_score", 0.0))
            if bm25_s > 0.0:
                return round(min(0.75, max(0.05, bm25_s / 50.0)), 3)

            return 0.05

        # FastPath 1: FastEmbed ONNX TextReRanker (<50MB RAM)
        if self.fast_reranker:
            try:
                docs = [c["content"] for c in candidates]
                rerank_results = list(self.fast_reranker.rerank(query, docs))
                
                scored_candidates = []
                for idx, item in enumerate(rerank_results):
                    c_idx = item.get("index") if isinstance(item, dict) else getattr(item, "index", idx)
                    score_val = item.get("score") if isinstance(item, dict) else getattr(item, "score", None)
                    
                    c_orig = candidates[c_idx]
                    # FastEmbed supplies a bounded ranking score, while the
                    # SentenceTransformers branch below uses BGE logits.  Use
                    # a lexical evidence guard here instead of logit
                    # calibration so valid matches are not over-filtered.
                    final_score = fastembed_relevance_score(query, c_orig["content"], score_val)
                    if final_score is None:
                        final_score = compute_true_score(c_orig)
                    c_copy = dict(c_orig)
                    c_copy["reranker_score"] = float(score_val) if score_val is not None else None
                    c_copy["relevance_score"] = final_score
                    scored_candidates.append(c_copy)
                
                scored_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
                return scored_candidates[:min(top_k, len(scored_candidates))]
            except Exception as e:
                logger.error(f"Error during FastEmbed reranking: {e}")

        # FastPath 2: SentenceTransformers Fallback
        if self.st_reranker:
            try:
                pairs = [(query, c["content"]) for c in candidates]
                # CrossEncoder.predict applies sigmoid by default for one-label
                # models.  Request logits so the BGE calibration below is only
                # applied once; treating the default output as a percentage was
                # the source of unrelated 50%+ citation matches.
                import torch
                scores = self.st_reranker.predict(
                    pairs,
                    activation_fn=torch.nn.Identity(),
                    show_progress_bar=False
                )
                if isinstance(scores, (int, float)):
                    scores = [scores]

                scored_candidates = []
                for idx, (candidate, score) in enumerate(zip(candidates, scores)):
                    final_score = compute_true_score(candidate, raw_rerank_s=float(score))
                    c_copy = dict(candidate)
                    c_copy["reranker_score"] = float(score)
                    c_copy["relevance_score"] = final_score
                    scored_candidates.append(c_copy)

                scored_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
                return scored_candidates[:min(top_k, len(scored_candidates))]
            except Exception as e:
                logger.error(f"Error during ST CrossEncoder reranking: {e}")

        # Fallback: Preserve true Dense Vector Similarity
        scored_candidates = []
        for c in candidates:
            c_copy = dict(c)
            final_score = compute_true_score(c)
            c_copy["relevance_score"] = final_score
            scored_candidates.append(c_copy)
            
        scored_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_candidates[:top_k]

# Pure-Python Persistent Vector Store
class LocalVectorStore:
    def __init__(self, persist_dir: str = "./vector_store"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        self.store_file = os.path.join(persist_dir, "vectors.json")
        self.documents = []
        self.embeddings = []
        self.metadatas = []
        self.ids = []
        self._load()

    def _load(self):
        if os.path.exists(self.store_file):
            try:
                with open(self.store_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.metadatas = data.get("metadatas", [])
                    self.ids = data.get("ids", [])
                    raw_emb = data.get("embeddings", [])
                    self.embeddings = np.array(raw_emb, dtype=np.float32) if raw_emb else np.empty((0, 384))
            except Exception as e:
                logger.warning(f"Could not load vector store file: {e}")
                self.documents, self.metadatas, self.ids, self.embeddings = [], [], [], np.empty((0, 384))
        else:
            self.embeddings = np.empty((0, 384))

    def _save(self):
        emb_list = self.embeddings.tolist() if len(self.embeddings) > 0 else []
        with open(self.store_file, "w", encoding="utf-8") as f:
            json.dump({
                "documents": self.documents,
                "metadatas": self.metadatas,
                "ids": self.ids,
                "embeddings": emb_list
            }, f)

    def add(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str], embeddings_arr: np.ndarray):
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)
        if len(self.embeddings) == 0:
            self.embeddings = embeddings_arr
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings_arr])
        self._save()

    def query(self, query_emb: np.ndarray, top_k: int = 20) -> Dict[str, Any]:
        if len(self.documents) == 0 or len(self.embeddings) == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        norm_query = query_emb / (np.linalg.norm(query_emb) + 1e-10)
        norm_emb = self.embeddings / (np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-10)
        similarities = np.dot(norm_emb, norm_query.T).flatten()
        
        top_indices = np.argsort(similarities)[::-1][:min(top_k, len(self.documents))]
        
        res_docs = [self.documents[i] for i in top_indices]
        res_metas = [self.metadatas[i] for i in top_indices]
        res_dists = [float(1.0 - similarities[i]) for i in top_indices]
        
        return {"documents": [res_docs], "metadatas": [res_metas], "distances": [res_dists]}

    def count(self) -> int:
        return len(self.documents)

    def delete_document(self, source_name: str) -> int:
        indices_to_keep = []
        deleted_count = 0
        for i, meta in enumerate(self.metadatas):
            if meta.get("source") == source_name or source_name in self.ids[i]:
                deleted_count += 1
            else:
                indices_to_keep.append(i)
                
        if deleted_count > 0:
            self.documents = [self.documents[i] for i in indices_to_keep]
            self.metadatas = [self.metadatas[i] for i in indices_to_keep]
            self.ids = [self.ids[i] for i in indices_to_keep]
            if len(indices_to_keep) > 0:
                self.embeddings = self.embeddings[indices_to_keep]
            else:
                self.embeddings = np.empty((0, 384))
            self._save()
            
        return deleted_count

    def clear(self):
        self.documents = []
        self.metadatas = []
        self.ids = []
        self.embeddings = np.empty((0, 384))
        if os.path.exists(self.store_file):
            os.remove(self.store_file)

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        chunks = []
        for doc, meta, cid in zip(self.documents, self.metadatas, self.ids):
            chunks.append({
                "id": cid,
                "content": doc,
                "metadata": meta,
                "source": meta.get("source", "Unknown"),
                "page": meta.get("page_number", meta.get("section", "N/A")),
                "ticker": meta.get("ticker", "N/A"),
                "chunk_index": meta.get("chunk_index", 0)
            })
        return chunks

class RAGEngine:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_fn = HuggingFaceEmbeddingFunction("all-MiniLM-L6-v2")
        self.bm25_manager = BM25IndexManager()
        self.reranker_manager = CrossEncoderReranker("BAAI/bge-reranker-base")
        
        # Try initializing ChromaDB; fallback to LocalVectorStore
        self.use_chroma = False
        self.chroma_client = None
        self.collection = None
        self.local_store = None

        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.chroma_client.get_or_create_collection(
                name="financial_documents",
                metadata={"hnsw:space": "cosine"}
            )
            self.use_chroma = True
            logger.info("ChromaDB vector engine initialized successfully.")
        except Exception as e:
            logger.warning(f"ChromaDB initialization bypassed ({e}). Operating via high-performance Local Vector Engine.")
            self.local_store = LocalVectorStore(persist_dir="./vector_store")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.groq_client = None
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq API client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")

        # Synchronize BM25 index with existing store documents
        self._sync_bm25_index()

    def _sync_bm25_index(self):
        """Builds BM25 index over all stored document chunks."""
        all_chunks = self._get_all_stored_chunks()
        self.bm25_manager.rebuild_index(all_chunks)

    def _get_all_stored_chunks(self) -> List[Dict[str, Any]]:
        chunks = []
        if self.use_chroma and self.collection:
            count = self.collection.count()
            if count > 0:
                data = self.collection.get(include=["documents", "metadatas"])
                docs = data.get("documents", [])
                metas = data.get("metadatas", [])
                ids = data.get("ids", [])
                for cid, d, m in zip(ids, docs, metas):
                    chunks.append({
                        "id": cid,
                        "content": d,
                        "metadata": m,
                        "source": m.get("source", "Unknown"),
                        "page": m.get("page_number", m.get("section", "N/A")),
                        "ticker": m.get("ticker", "N/A"),
                        "chunk_index": m.get("chunk_index", 0)
                    })
        elif self.local_store:
            chunks = self.local_store.get_all_chunks()
        return chunks

    def ingest_text(self, text: str, source_name: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        if not text or not text.strip():
            return 0
            
        base_meta = metadata or {}
        base_meta["source"] = source_name
        
        chunks = self.text_splitter.split_text(text)
        if not chunks:
            return 0
            
        documents = []
        metadatas = []
        ids = []
        
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{source_name}_chunk_{idx}_{hash(chunk) & 0xffffffff}"
            chunk_meta = {
                **base_meta,
                "chunk_id": chunk_id,
                "chunk_index": idx,
                "source": source_name,
                "snippet": chunk[:150] + "..."
            }
            documents.append(chunk)
            metadatas.append(chunk_meta)
            ids.append(chunk_id)
            
        embeddings_np = self.embedding_fn.encode(documents)
        
        if self.use_chroma and self.collection:
            embeddings_list = embeddings_np.tolist()
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                self.collection.add(
                    documents=documents[i:i+batch_size],
                    embeddings=embeddings_list[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size]
                )
        else:
            self.local_store.add(documents, metadatas, ids, embeddings_np)
            
        # Re-sync BM25 index with new chunks
        self._sync_bm25_index()
        logger.info(f"Ingested {len(chunks)} chunks into vector store for '{source_name}'.")
        return len(chunks)

    def dense_retrieve(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Dense Vector Retrieval using ChromaDB or LocalVectorStore."""
        count = self.collection.count() if self.use_chroma else self.local_store.count()
        if count == 0:
            return []
            
        query_emb = self.embedding_fn.encode([query])
        
        if self.use_chroma and self.collection:
            results = self.collection.query(
                query_embeddings=query_emb.tolist(),
                n_results=min(top_k, count),
                include=["documents", "metadatas", "distances"]
            )
        else:
            results = self.local_store.query(query_emb[0], top_k=top_k)
        
        retrieved_chunks = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results.get("distances", [[]])[0]
            
            for idx in range(len(docs)):
                doc_text = docs[idx]
                meta = metas[idx] if idx < len(metas) else {}
                dist = distances[idx] if idx < len(distances) else 0.8
                raw_similarity = max(0.0, 1.0 - float(dist))
                
                # Calibrate raw vector similarity to subtract high-dimensional baseline (~0.50)
                # Unrelated text (raw sim ~ 0.50) -> calibrated sim ~ 0.05
                # Highly relevant text (raw sim ~ 0.85-0.95) -> calibrated sim ~ 0.70-0.90
                if raw_similarity <= 0.50:
                    calibrated_similarity = round(max(0.02, raw_similarity * 0.3), 3)
                else:
                    calibrated_similarity = round(min(0.99, (raw_similarity - 0.50) / 0.50 * 0.70 + 0.30), 3)
                    
                chunk_id = meta.get("chunk_id", f"{meta.get('source', 'doc')}_chunk_{meta.get('chunk_index', idx)}")
                
                retrieved_chunks.append({
                    "id": chunk_id,
                    "content": doc_text,
                    "source": meta.get("source", "Financial Document"),
                    "page": meta.get("page_number", meta.get("section", "N/A")),
                    "ticker": meta.get("ticker", "N/A"),
                    "chunk_index": meta.get("chunk_index", idx),
                    "dense_score": calibrated_similarity
                })
                
        return retrieved_chunks

    def hybrid_retrieve(self, query: str, top_candidates: int = 20, rrf_k: int = 60) -> List[Dict[str, Any]]:
        """
        1. HYBRID SEARCH: Combines Dense (ChromaDB) + Sparse (BM25) candidates using Reciprocal Rank Fusion (RRF).
        RRF(d) = sum( 1 / (rrf_k + rank_m(d)) )
        """
        dense_results = self.dense_retrieve(query, top_k=top_candidates)
        bm25_results = self.bm25_manager.search(query, top_k=top_candidates)

        if not dense_results and not bm25_results:
            return []

        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        # Process Dense Ranks
        for rank, item in enumerate(dense_results, start=1):
            # Both retrieval paths must use the same identity.  Old Chroma
            # metadata may not have ``chunk_id``, so source + chunk index is
            # used as a backwards-compatible canonical key.
            doc_id = f"{item['source']}::{item.get('chunk_index', 0)}"
            doc_map[doc_id] = item
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank))

        # Process BM25 Ranks
        for rank, item in enumerate(bm25_results, start=1):
            doc_id = f"{item['source']}::{item.get('chunk_index', 0)}"
            if doc_id not in doc_map:
                doc_map[doc_id] = item
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank))

        # Sort candidates by RRF score
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        hybrid_candidates = []
        for doc_id in sorted_ids[:top_candidates]:
            candidate = dict(doc_map[doc_id])
            candidate["rrf_score"] = round(rrf_scores[doc_id], 4)
            hybrid_candidates.append(candidate)

        logger.info(f"Hybrid retrieval generated {len(hybrid_candidates)} candidates using RRF.")
        return hybrid_candidates

    def retrieve(self, query: str, top_k: int = TOP_K_RERANKED) -> List[Dict[str, Any]]:
        """
        Combined Multi-Stage Pipeline:
        1. Hybrid Search (Dense + BM25 via RRF) -> Top 20 Candidates
        2. Cross-Encoder Reranking (bge-reranker-base) -> Top top_k Candidates
        """
        hybrid_candidates = self.hybrid_retrieve(query, top_candidates=20, rrf_k=60)
        if not hybrid_candidates:
            return []

        # Step 2: Cross-Encoder Reranking
        reranked_results = self.reranker_manager.rerank(query, hybrid_candidates, top_k=top_k)
        return reranked_results

    def chat(self, query: str) -> Dict[str, Any]:
        """
        Main RAG Chat Pipeline:
        Hybrid Search (BM25+Dense RRF) -> Cross-Encoder Reranker -> Relevance Filtering -> Groq Llama-3
        """
        raw_chunks = self.retrieve(query, top_k=TOP_K_RERANKED)
        
        if not raw_chunks:
            return {
                "answer": "No financial documents have been ingested yet. Please upload a PDF report or fetch an SEC 10-K ticker from the left panel to begin analyzing.",
                "citations": []
            }
            
        # Filter chunks to keep only relevant context (relevance_score >= 0.35)
        RELEVANCE_THRESHOLD = 0.35
        relevant_chunks = [c for c in raw_chunks if c.get("relevance_score", 0.0) >= RELEVANCE_THRESHOLD]
        
        if not relevant_chunks:
            logger.info(f"All retrieved chunks fell below relevance threshold ({RELEVANCE_THRESHOLD}) for query '{query}'.")
            return {
                "answer": f"The provided documents do not contain relevant information to answer your question: '{query}'. Please upload a document containing details on this topic.",
                "citations": []
            }
            
        context_blocks = []
        citations = []
        for idx, item in enumerate(relevant_chunks, 1):
            rel_score = item.get("relevance_score", 0.85)
            context_blocks.append(f"[Source {idx} - {item['source']} (Relevance: {rel_score})]:\n{item['content']}")
            citations.append({
                "source_id": idx,
                "document": item["source"],
                "section_or_page": str(item["page"]),
                "snippet": item["content"],
                "relevance_score": rel_score
            })
            
        formatted_context = "\n\n".join(context_blocks)
        
        system_prompt = (
            "You are AlphaRead, an expert Financial AI Assistant specializing in financial statements, SEC 10-K filings, and quantitative analysis.\n\n"
            "CRITICAL INSTRUCTIONS FOR CONTEXT PROCESSING:\n"
            "1. LOOK FOR MARKDOWN TABLES: The provided context contains structural Markdown tables representing Balance Sheets, Income Statements, and Footnotes. Read these tables vertically and horizontally to align financial metrics with their exact dates and values and Don't give those tables as it is convert to to readable numericals with text. Do not guess.\n"
            "2. DISREGARD CORPORATE INTROS: Do not get distracted by conversational or qualitative summary sentences (e.g., 'AWS remains a key driver...'). If a query asks for performance or numeric metrics, bypass the introduction and extract the values from the underlying data rows or footnotes.\n"
            "3. ABSOLUTE ZERO HALLUCINATION ROADBLOCK: If the provided context contains textual references to an Item or Section but lacks explicit quantitative figures or financial tables requested, you MUST explicitly state that numeric values are missing from the current context. Never invent or round a financial metric.\n\n"
            "RESPONSE SCHEMA RULES:\n"
            "- If a financial table is found, preserve its structure in your output using clean Markdown tables.\n"
            "- Bold all raw numbers, currency denominations, and percentage growth rates (e.g., **$24,632 million**, **+12%**).\n"
            "- Cite the exact Item or Section metadata tag attached to the context block (e.g., [Source 1 - Item 7]) for every fact provided.\n"
            "- If the answer cannot be determined with exact numeric precision from the provided chunks, output: 'The context confirms the existence of this section, but the exact numeric data was cut off or missing from the retrieval pipeline.\n'"
            "- Analyse those tables and give a readable numericals with text. Don't just give the table as it is and don't use '*' and '| :--- | :---: | :---: | :---: |'"
        )
        
        user_prompt = f"FINANCIAL DOCUMENT CONTEXT:\n{formatted_context}\n\nUSER QUESTION: {query}"
        
        answer = ""
        groq_error_msg = ""
        
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not self.groq_client and api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                logger.info("Groq client dynamically initialized.")
            except Exception as e:
                groq_error_msg = f"Groq client init error: {e}"
                logger.error(groq_error_msg)

        if self.groq_client:
            models_to_try = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama3-70b-8192",
                "llama3-8b-8192",
                "mixtral-8x7b-32768"
            ]
            for model_name in models_to_try:
                try:
                    logger.info(f"Invoking Groq LLM API model '{model_name}'...")
                    response = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.2,
                        max_tokens=1024
                    )
                    answer = response.choices[0].message.content
                    logger.info(f"Groq API call succeeded using model '{model_name}'.")
                    break
                except Exception as e:
                    groq_error_msg = f"Groq API error on model '{model_name}': {e}"
                    logger.error(groq_error_msg)

        if not answer:
            answer = self._generate_fallback_answer(query, chunks, groq_error_msg)
            
        return {
            "answer": answer,
            "citations": citations,
            "retrieval_method": "Hybrid Search (BM25 + Dense RRF) + BGE Cross-Encoder Reranking"
        }

    def _generate_fallback_answer(self, query: str, chunks: List[Dict[str, Any]], groq_error: str = "") -> str:
        sources_used = ", ".join(list(set(c["source"] for c in chunks)))
        
        summary = (
            f"Based on the retrieved financial documents (**{sources_used}**), here are the key analytical insights regarding your query:\n\n"
        )
        
        for idx, chunk in enumerate(chunks, 1):
            text_preview = chunk["content"].replace("\n", " ").strip()
            if len(text_preview) > 350:
                text_preview = text_preview[:350] + "..."
            summary += f"**Key Insight {idx} (from {chunk['source']})**: {text_preview}\n\n"
            
        api_key_present = bool(os.getenv("GROQ_API_KEY", "").strip())
        if api_key_present:
            if groq_error:
                summary += f"\n*⚠️ Groq API key is set, but returned an error: `{groq_error}`*"
            else:
                summary += "\n*⚠️ Groq API key is set, but client connection could not be established.*"
        else:
            summary += "\n*Note: To enable direct Llama-3 generative responses via Groq, add your `GROQ_API_KEY` to environment variables.*"
            
        return summary

    def list_documents(self) -> List[Dict[str, Any]]:
        count = self.collection.count() if self.use_chroma else self.local_store.count()
        if count == 0:
            return []
            
        if self.use_chroma:
            all_items = self.collection.get(include=["metadatas"])
            metas = all_items.get("metadatas", [])
        else:
            metas = self.local_store.metadatas
        
        docs_map = {}
        for m in metas:
            source = m.get("source", "Unknown")
            if source not in docs_map:
                docs_map[source] = {
                    "source": source,
                    "ticker": m.get("ticker", "N/A"),
                    "doc_type": m.get("doc_type", "PDF" if not m.get("ticker") else "SEC_10K"),
                    "chunks_count": 0
                }
            docs_map[source]["chunks_count"] += 1
            
        return list(docs_map.values())

    def delete_document(self, source_name: str) -> bool:
        """Deletes vector embeddings for a specific source document and syncs BM25 index."""
        deleted = False
        if self.use_chroma and self.collection:
            try:
                self.collection.delete(where={"source": source_name})
                logger.info(f"Deleted ChromaDB vectors for source '{source_name}'.")
                deleted = True
            except Exception as e:
                logger.error(f"Error deleting ChromaDB source '{source_name}': {e}")
                deleted = False
        elif self.local_store:
            deleted_count = self.local_store.delete_document(source_name)
            logger.info(f"Deleted {deleted_count} chunks from local store for '{source_name}'.")
            deleted = deleted_count > 0

        if deleted:
            self._sync_bm25_index()
        return deleted

    def clear_database(self):
        if self.use_chroma:
            self.chroma_client.delete_collection("financial_documents")
            self.collection = self.chroma_client.get_or_create_collection(
                name="financial_documents",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.local_store.clear()
            
        self._sync_bm25_index()

# Global singleton RAG engine instance
rag_engine = RAGEngine()
