"""
RAG & Vector Search Router
==========================
Endpoints for semantic search, document ingestion, and agent memory.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.vector_service import (
    upsert_document,
    search_similar,
    list_namespaces,
    delete_namespace,
    store_agent_memory,
    search_agent_memory,
    cleanup_expired_memories,
)

router = APIRouter(prefix="/api/v1", tags=["rag"])


class DocumentIngestRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)
    source_path: str = Field(..., max_length=500)
    namespace: str = Field(default="default", max_length=100)
    title: Optional[str] = None
    source_type: str = "doc"
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    namespace: str = Field(default="default", max_length=100)
    limit: int = Field(default=5, ge=1, le=50)
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0)


class AgentMemoryRequest(BaseModel):
    agent_name: str = Field(..., max_length=100)
    content: str = Field(..., max_length=10000)
    namespace: str = Field(default="default", max_length=100)
    memory_type: str = Field(default="observation", max_length=50)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    ttl_hours: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


# ── PUBLIC ENDPOINTS ──

@router.post("/rag/search")
async def rag_search(req: SearchRequest):
    """Semantic search across documents."""
    try:
        results = search_similar(
            query=req.query,
            namespace=req.namespace,
            limit=req.limit,
            min_similarity=req.min_similarity,
        )
        return {
            "query": req.query,
            "namespace": req.namespace,
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/namespaces")
async def get_namespaces():
    """List all available search namespaces."""
    return {"namespaces": list_namespaces()}


# ── ADMIN / SYSTEM ENDPOINTS ──

@router.post("/rag/documents")
async def ingest_document(req: DocumentIngestRequest):
    """Ingest a document chunk into the vector store."""
    try:
        result = upsert_document(
            content=req.content,
            source_path=req.source_path,
            namespace=req.namespace,
            title=req.title,
            source_type=req.source_type,
            metadata=req.metadata,
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rag/namespaces/{namespace}")
async def clear_namespace(namespace: str):
    """Delete all data in a namespace."""
    try:
        return delete_namespace(namespace)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── AGENT MEMORY ENDPOINTS ──

@router.post("/rag/agent/memory")
async def create_agent_memory(req: AgentMemoryRequest):
    """Store a memory for an agent."""
    try:
        result = store_agent_memory(
            agent_name=req.agent_name,
            content=req.content,
            namespace=req.namespace,
            memory_type=req.memory_type,
            importance=req.importance,
            ttl_hours=req.ttl_hours,
            metadata=req.metadata,
        )
        return {"success": True, "memory": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/agent/memory/{agent_name}")
async def query_agent_memory(
    agent_name: str,
    query: str,
    namespace: str = "default",
    limit: int = 5,
):
    """Search an agent's memory."""
    try:
        results = search_agent_memory(
            agent_name=agent_name,
            query=query,
            namespace=namespace,
            limit=limit,
        )
        return {"agent": agent_name, "query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/agent/memory/cleanup")
async def agent_memory_cleanup():
    """Remove expired agent memories."""
    try:
        count = cleanup_expired_memories()
        return {"cleaned": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
