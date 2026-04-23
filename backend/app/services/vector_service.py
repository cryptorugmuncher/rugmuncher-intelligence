"""
RMI Vector Service
==================
Manages embeddings, RAG search, and agent memory with namespace isolation.
Uses Supabase pgvector for storage.
"""

import os
import sys
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger("vector_service")

# Lazy imports for embedding model
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Lazy import for OpenAI (fallback embedder)
try:
    import openai
except ImportError:
    openai = None

# Supabase client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db_client import RMI_DB

_db = RMI_DB()
_embedding_model = None
_default_model_name = "all-MiniLM-L6-v2"


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None and SentenceTransformer is not None:
        logger.info("Loading embedding model: %s", _default_model_name)
        _embedding_model = SentenceTransformer(_default_model_name)
    return _embedding_model


def _compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]


def embed_text(text: str, model_name: Optional[str] = None) -> List[float]:
    """Generate embedding vector for text."""
    model = _get_embedding_model()
    if model is not None:
        vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return vec.tolist()

    # Fallback: try OpenAI if available
    if openai is not None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client = openai.OpenAI(api_key=api_key)
            resp = client.embeddings.create(input=text, model="text-embedding-3-small")
            return resp.data[0].embedding

    raise RuntimeError("No embedding model available. Install sentence-transformers or set OPENAI_API_KEY.")


def upsert_document(
    content: str,
    source_path: str,
    namespace: str = "default",
    title: Optional[str] = None,
    source_type: str = "doc",
    chunk_index: int = 0,
    total_chunks: int = 1,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Store a document chunk and its embedding."""
    sb = _db.client
    content_hash = _compute_hash(content)

    # Insert document
    doc_result = sb.table("rag_documents").insert({
        "namespace": namespace,
        "source_type": source_type,
        "source_path": source_path,
        "title": title or source_path,
        "chunk_index": chunk_index,
        "total_chunks": total_chunks,
        "content": content,
        "metadata": metadata or {},
        "updated_at": datetime.utcnow().isoformat(),
    }).execute()

    if not doc_result.data:
        raise RuntimeError("Failed to insert document")

    doc_id = doc_result.data[0]["id"]

    # Generate and insert embedding
    vector = embed_text(content)
    emb_result = sb.table("embeddings").insert({
        "document_id": doc_id,
        "namespace": namespace,
        "embedding": vector,
        "model_name": _default_model_name,
        "content_hash": content_hash,
        "metadata": metadata or {},
    }).execute()

    # Update namespace document count
    try:
        sb.rpc("increment_namespace_count", {"ns": namespace}).execute()
    except Exception:
        pass

    return {
        "document_id": doc_id,
        "embedding_id": emb_result.data[0]["id"] if emb_result.data else None,
        "namespace": namespace,
    }


def search_similar(
    query: str,
    namespace: str = "default",
    limit: int = 5,
    min_similarity: float = 0.7,
) -> List[Dict[str, Any]]:
    """Semantic search within a namespace."""
    sb = _db.client
    vector = embed_text(query)

    result = sb.rpc("search_embeddings", {
        "query_embedding": vector,
        "target_namespace": namespace,
        "match_count": limit,
        "min_similarity": min_similarity,
    }).execute()

    return result.data or []


def delete_namespace(namespace: str) -> Dict[str, Any]:
    """Delete all documents and embeddings in a namespace."""
    sb = _db.client
    sb.table("embeddings").delete().eq("namespace", namespace).execute()
    sb.table("rag_documents").delete().eq("namespace", namespace).execute()
    sb.table("ai_search_namespaces").delete().eq("name", namespace).execute()
    return {"deleted": True, "namespace": namespace}


def list_namespaces() -> List[Dict[str, Any]]:
    """List all AI search namespaces."""
    sb = _db.client
    result = sb.table("ai_search_namespaces").select("*").execute()
    return result.data or []


# ═══════════════════════════════════════════════════════════
# AGENT MEMORY
# ═══════════════════════════════════════════════════════════

def store_agent_memory(
    agent_name: str,
    content: str,
    namespace: str = "default",
    memory_type: str = "observation",
    importance: float = 0.5,
    ttl_hours: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Store a memory for an agent with optional embedding."""
    sb = _db.client
    expires = None
    if ttl_hours:
        expires = (datetime.utcnow() + timedelta(hours=ttl_hours)).isoformat()

    try:
        vector = embed_text(content)
    except Exception:
        vector = None

    result = sb.table("agent_memory").insert({
        "agent_name": agent_name,
        "namespace": namespace,
        "memory_type": memory_type,
        "content": content,
        "embedding": vector,
        "importance_score": importance,
        "metadata": metadata or {},
        "expires_at": expires,
    }).execute()

    return result.data[0] if result.data else {}


def search_agent_memory(
    agent_name: str,
    query: str,
    namespace: str = "default",
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Search agent memory semantically."""
    sb = _db.client
    try:
        vector = embed_text(query)
        result = sb.rpc("search_embeddings", {
            "query_embedding": vector,
            "target_namespace": namespace,
            "match_count": limit,
            "min_similarity": 0.6,
        }).execute()
        return result.data or []
    except Exception as e:
        logger.warning("Semantic memory search failed: %s", e)
        # Fallback to text search
        result = sb.table("agent_memory").select("*").eq("agent_name", agent_name).eq("namespace", namespace).ilike("content", f"%{query}%").limit(limit).execute()
        return result.data or []


def cleanup_expired_memories() -> int:
    """Delete expired agent memories. Returns count deleted."""
    sb = _db.client
    now = datetime.utcnow().isoformat()
    result = sb.table("agent_memory").delete().lt("expires_at", now).execute()
    return len(result.data) if result.data else 0
