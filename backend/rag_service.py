import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
from groq import Groq

# Explicitly load .env file from backend folder
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)
load_dotenv()  # Fallback search

logger = logging.getLogger(__name__)

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
            # Deterministic hash embedding fallback if no ML engine loaded
            logger.warning("Using basic hash embedding fallback.")
            vectors = []
            for t in texts:
                np.random.seed(abs(hash(t)) % (2**32 - 1))
                vectors.append(np.random.randn(384).astype(np.float32))
            return np.array(vectors, dtype=np.float32)

# Pure-Python Persistent Vector Store (Used when Windows AppControl blocks gRPC/ChromaDB DLLs)
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

    def query(self, query_emb: np.ndarray, top_k: int = 3) -> Dict[str, Any]:
        if len(self.documents) == 0 or len(self.embeddings) == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        # Compute cosine similarity
        norm_query = query_emb / (np.linalg.norm(query_emb) + 1e-10)
        norm_emb = self.embeddings / (np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-10)
        similarities = np.dot(norm_emb, norm_query.T).flatten()
        
        # Top-k indices
        top_indices = np.argsort(similarities)[::-1][:min(top_k, len(self.documents))]
        
        res_docs = [self.documents[i] for i in top_indices]
        res_metas = [self.metadatas[i] for i in top_indices]
        res_dists = [float(1.0 - similarities[i]) for i in top_indices]
        
        return {"documents": [res_docs], "metadatas": [res_metas], "distances": [res_dists]}

    def count(self) -> int:
        return len(self.documents)

    def delete_document(self, source_name: str) -> int:
        """Deletes all chunks matching source_name."""
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

class RAGEngine:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_fn = HuggingFaceEmbeddingFunction("all-MiniLM-L6-v2")
        
        # Try initializing ChromaDB; fallback to LocalVectorStore if Windows AppControl blocks gRPC DLL
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

        # Initialize LangChain text splitter (chunk_size=1000, chunk_overlap=200)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize Groq client
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.groq_client = None
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq API client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")

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
                "chunk_index": idx,
                "source": source_name,
                "snippet": chunk[:150] + "..."
            }
            documents.append(chunk)
            metadatas.append(chunk_meta)
            ids.append(chunk_id)
            
        # Generate embeddings
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
            
        logger.info(f"Ingested {len(chunks)} chunks into vector store for '{source_name}'.")
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
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
                dist = distances[idx] if idx < len(distances) else 0.5
                similarity = round(max(0.0, 1.0 - float(dist)), 3)
                
                retrieved_chunks.append({
                    "content": doc_text,
                    "source": meta.get("source", "Financial Document"),
                    "page": meta.get("page_number", meta.get("section", "N/A")),
                    "ticker": meta.get("ticker", "N/A"),
                    "chunk_index": meta.get("chunk_index", idx),
                    "relevance_score": similarity
                })
                
        return retrieved_chunks

    def chat(self, query: str) -> Dict[str, Any]:
        chunks = self.retrieve(query, top_k=3)
        
        if not chunks:
            return {
                "answer": "No financial documents have been ingested yet. Please upload a PDF report or fetch an SEC 10-K ticker from the left panel to begin analyzing.",
                "citations": []
            }
            
        context_blocks = []
        citations = []
        for idx, item in enumerate(chunks, 1):
            context_blocks.append(f"[Source {idx} - {item['source']} (Relevance: {item['relevance_score']})]:\n{item['content']}")
            citations.append({
                "source_id": idx,
                "document": item["source"],
                "section_or_page": str(item["page"]),
                "snippet": item["content"],
                "relevance_score": item["relevance_score"]
            })
            
        formatted_context = "\n\n".join(context_blocks)
        
        system_prompt = (
            "You are AlphaRead, an expert Financial AI Assistant specializing in financial statements, SEC 10-K filings, and quantitative analysis.\n"
            "Answer the user's question accurately using ONLY the provided document context below.\n"
            "Guidelines:\n"
            "1. Be precise, professional, and clear.\n"
            "2. Cite key numerical figures and financial facts from the context.\n"
            "3. Reference [Source 1], [Source 2], etc. inline when explaining facts from specific documents.\n"
            "4. If the provided context does not contain enough information to answer definitively, state what is present in the context and note any limitations."
        )
        
        user_prompt = f"FINANCIAL DOCUMENT CONTEXT:\n{formatted_context}\n\nUSER QUESTION: {query}"
        
        answer = ""
        groq_error_msg = ""
        
        # Check and initialize Groq client if key exists
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
            "citations": citations
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
        """Deletes vector embeddings for a specific source document."""
        if self.use_chroma and self.collection:
            try:
                self.collection.delete(where={"source": source_name})
                logger.info(f"Deleted ChromaDB vectors for source '{source_name}'.")
                return True
            except Exception as e:
                logger.error(f"Error deleting ChromaDB source '{source_name}': {e}")
                return False
        elif self.local_store:
            deleted_count = self.local_store.delete_document(source_name)
            logger.info(f"Deleted {deleted_count} chunks from local store for '{source_name}'.")
            return deleted_count > 0
        return False

    def clear_database(self):
        if self.use_chroma:
            self.chroma_client.delete_collection("financial_documents")
            self.collection = self.chroma_client.get_or_create_collection(
                name="financial_documents",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.local_store.clear()

# Global singleton RAG engine instance
rag_engine = RAGEngine()
