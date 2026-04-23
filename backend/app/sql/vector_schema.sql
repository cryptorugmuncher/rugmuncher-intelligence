-- RMI Vector Search & RAG Schema (pgvector)
-- Run in Supabase SQL Editor

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ═══════════════════════════════════════════════════════════
-- RAG DOCUMENTS (source documents chunked)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS rag_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    namespace TEXT NOT NULL DEFAULT 'default',
    source_type TEXT NOT NULL DEFAULT 'doc',
    source_path TEXT NOT NULL,
    title TEXT,
    chunk_index INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 1,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rag_docs_namespace ON rag_documents(namespace);
CREATE INDEX IF NOT EXISTS idx_rag_docs_source ON rag_documents(source_path);

-- ═══════════════════════════════════════════════════════════
-- EMBEDDINGS (vector representations of chunks)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES rag_documents(id) ON DELETE CASCADE,
    namespace TEXT NOT NULL DEFAULT 'default',
    embedding vector(384),
    model_name TEXT DEFAULT 'all-MiniLM-L6-v2',
    content_hash TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_embeddings_namespace ON embeddings(namespace);
CREATE INDEX IF NOT EXISTS idx_embeddings_document ON embeddings(document_id);

-- HNSW index for fast similarity search (pgvector 0.5+)
CREATE INDEX IF NOT EXISTS idx_embeddings_vector_hnsw ON embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ═══════════════════════════════════════════════════════════
-- SEARCH FUNCTION
-- ═══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION search_embeddings(
    query_embedding vector(384),
    target_namespace TEXT DEFAULT 'default',
    match_count INTEGER DEFAULT 5,
    min_similarity FLOAT DEFAULT 0.7
)
RETURNS TABLE(
    id UUID,
    document_id UUID,
    namespace TEXT,
    content TEXT,
    similarity FLOAT,
    metadata JSONB,
    source_path TEXT,
    title TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.document_id,
        e.namespace,
        d.content,
        1 - (e.embedding <=> query_embedding) AS similarity,
        d.metadata,
        d.source_path,
        d.title
    FROM embeddings e
    JOIN rag_documents d ON d.id = e.document_id
    WHERE e.namespace = target_namespace
      AND 1 - (e.embedding <=> query_embedding) >= min_similarity
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ═══════════════════════════════════════════════════════════
-- AGENT MEMORY (short-term memory for agents)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    namespace TEXT NOT NULL DEFAULT 'default',
    memory_type TEXT NOT NULL DEFAULT 'observation',
    content TEXT NOT NULL,
    embedding vector(384),
    importance_score FLOAT DEFAULT 0.5,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_agent_memory_agent ON agent_memory(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_memory_namespace ON agent_memory(namespace);
CREATE INDEX IF NOT EXISTS idx_agent_memory_expires ON agent_memory(expires_at);

-- ═══════════════════════════════════════════════════════════
-- AI SEARCH NAMESPACES (registry)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS ai_search_namespaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    document_count INTEGER DEFAULT 0,
    embedding_model TEXT DEFAULT 'all-MiniLM-L6-v2',
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO ai_search_namespaces (name, description, config)
VALUES
    ('default', 'General knowledge base', '{"public": true}'),
    ('threat_intel', 'Scam reports, rug pulls, threat actor profiles', '{"public": false}'),
    ('docs', 'Project documentation, API docs, guides', '{"public": true}'),
    ('contracts', 'Smart contract source code and audits', '{"public": true}'),
    ('community', 'Community discussions, FAQs, support', '{"public": true}')
ON CONFLICT (name) DO NOTHING;
