#!/usr/bin/env python3
"""
RAG MCP Server for Documentation Search

Exposes documentation semantic search capabilities to Claude Code via MCP protocol.

Tools provided:
- query_docs: Semantic search across indexed documentation
- reindex_docs: Trigger re-indexing of documentation
- get_stats: Get indexing statistics and info
- filter_by_path: Search within specific document paths
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import subprocess

# NOTE: chromadb, sentence_transformers are imported LAZILY inside initialize_rag()
# to avoid blocking MCP server startup (~13s of import time would cause connection timeout)
from mcp.server import Server
from mcp.types import Tool, TextContent


# Configuration
CHROMA_DB_PATH = ".chroma"
COLLECTION_NAME = "documentation"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
INDEX_SCRIPT_PATH = "scripts/index_docs.py"

# Global state
embedding_model = None
chroma_client = None
collection = None
_rag_initialized = False


def initialize_rag():
    """Initialize RAG components (embedding model and ChromaDB) with lazy imports"""
    global embedding_model, chroma_client, collection, _rag_initialized

    if _rag_initialized:
        return

    try:
        # Lazy import heavy dependencies (chromadb ~2s, sentence_transformers ~11s)
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer

        # Load embedding model
        if embedding_model is None:
            sys.stderr.write("Loading embedding model...\n")
            embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            sys.stderr.write("Embedding model loaded\n")

        # Connect to ChromaDB
        if chroma_client is None:
            chroma_path = Path(CHROMA_DB_PATH)
            if not chroma_path.exists():
                raise FileNotFoundError(
                    f"ChromaDB not found at {CHROMA_DB_PATH}. "
                    f"Run 'python scripts/index_docs.py' first."
                )

            chroma_client = chromadb.PersistentClient(
                path=CHROMA_DB_PATH,
                settings=Settings(anonymized_telemetry=False)
            )

            # Get collection
            collection = chroma_client.get_collection(COLLECTION_NAME)
            sys.stderr.write(f"Connected to collection: {COLLECTION_NAME}\n")

        _rag_initialized = True

    except Exception as e:
        sys.stderr.write(f"Error initializing RAG: {e}\n")
        raise


def query_documentation(
    query: str,
    n_results: int = 5,
    filter_path: Optional[str] = None
) -> List[Dict]:
    """
    Query documentation using semantic search

    Args:
        query: Search query (natural language)
        n_results: Number of results to return
        filter_path: Optional path filter (e.g., "Requirements/")

    Returns:
        List of results with text, metadata, and similarity scores
    """
    initialize_rag()

    # Generate query embedding
    query_embedding = embedding_model.encode([query])[0].tolist()

    # Build where filter if path specified
    where_filter = None
    if filter_path:
        where_filter = {
            "$or": [
                {"file_path": {"$contains": filter_path}},
                {"section": {"$contains": filter_path}}
            ]
        }

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter
    )

    # Format results
    formatted_results = []
    for i in range(len(results['ids'][0])):
        formatted_results.append({
            'text': results['documents'][0][i],
            'file_path': results['metadatas'][0][i].get('file_path', ''),
            'section': results['metadatas'][0][i].get('section', ''),
            'headers': results['metadatas'][0][i].get('headers', ''),
            'distance': results['distances'][0][i] if 'distances' in results else None
        })

    return formatted_results


def get_collection_stats() -> Dict:
    """Get statistics about the indexed documentation"""
    initialize_rag()

    count = collection.count()

    # Get sample documents to extract metadata
    sample = collection.get(limit=min(count, 100))

    # Extract unique file paths
    file_paths = set()
    for metadata in sample.get('metadatas', []):
        if 'file_path' in metadata:
            file_paths.add(metadata['file_path'])

    return {
        'total_chunks': count,
        'collection_name': COLLECTION_NAME,
        'database_path': CHROMA_DB_PATH,
        'embedding_model': EMBEDDING_MODEL,
        'sample_files': sorted(list(file_paths))[:10],
        'total_unique_files': len(file_paths)
    }


async def reindex_documentation() -> str:
    """Trigger re-indexing of documentation"""
    try:
        sys.stderr.write("Starting re-indexing...\n")

        # Import the indexing function
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from scripts.index_docs import index_documents, DOCS_FOLDER, CHROMA_DB_PATH, COLLECTION_NAME

        # Run indexing in thread to avoid blocking
        def run_indexing():
            try:
                index_documents(DOCS_FOLDER, CHROMA_DB_PATH, COLLECTION_NAME, show_progress=False)
                return "success"
            except Exception as e:
                return f"error: {str(e)}"

        # Execute in thread with timeout
        result = await asyncio.wait_for(
            asyncio.to_thread(run_indexing),
            timeout=60.0
        )

        if result == "success":
            # Reset global state to reload collection
            global chroma_client, collection, _rag_initialized
            chroma_client = None
            collection = None
            _rag_initialized = False

            sys.stderr.write("Re-indexing completed successfully\n")
            return "Re-indexing completed successfully"
        else:
            return f"Re-indexing failed: {result}"

    except asyncio.TimeoutError:
        return "Re-indexing timed out after 60 seconds"
    except Exception as e:
        return f"Error during re-indexing: {str(e)}"


# Create MCP server
app = Server("docs-rag")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available RAG tools"""
    return [
        Tool(
            name="query_docs",
            description=(
                "Semantic search across project documentation. "
                "Returns relevant document chunks with source citations. "
                "Use this to find requirements, specifications, and guidelines "
                "before implementing features."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g., 'authentication requirements', 'API security guidelines')"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 20)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "filter_path": {
                        "type": "string",
                        "description": "Optional filter to search within specific paths (e.g., 'Requirements/', 'API/')",
                        "default": None
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="reindex_docs",
            description=(
                "Trigger re-indexing of all documentation. "
                "Use this after adding or updating documentation files. "
                "May take 1-2 minutes depending on documentation size."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_stats",
            description=(
                "Get statistics about indexed documentation including "
                "chunk count, file count, and sample file list."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict) -> List[TextContent]:
    """Handle tool calls"""

    try:
        if name == "query_docs":
            query = arguments.get("query")
            n_results = arguments.get("n_results", 5)
            filter_path = arguments.get("filter_path")

            if not query:
                return [TextContent(
                    type="text",
                    text="Error: 'query' parameter is required"
                )]

            # Perform search
            results = query_documentation(query, n_results, filter_path)

            # Format response
            if not results:
                response = f"No results found for query: '{query}'"
                if filter_path:
                    response += f"\nFilter: {filter_path}"
            else:
                response = f"Found {len(results)} relevant documentation chunks:\n\n"

                for i, result in enumerate(results, 1):
                    response += f"--- Result {i} ---\n"
                    response += f"Source: {result['file_path']}\n"
                    if result['section']:
                        response += f"Section: {result['section']}\n"
                    if result['headers']:
                        response += f"Headers: {result['headers']}\n"
                    response += f"\nContent:\n{result['text']}\n\n"

            return [TextContent(type="text", text=response)]

        elif name == "reindex_docs":
            result = await reindex_documentation()
            return [TextContent(type="text", text=result)]

        elif name == "get_stats":
            stats = get_collection_stats()

            response = "Documentation Index Statistics\n\n"
            response += f"Total chunks: {stats['total_chunks']}\n"
            response += f"Unique files: {stats['total_unique_files']}\n"
            response += f"Collection: {stats['collection_name']}\n"
            response += f"Database: {stats['database_path']}\n"
            response += f"Embedding model: {stats['embedding_model']}\n\n"
            response += "Sample indexed files:\n"
            for file in stats['sample_files']:
                response += f"  - {file}\n"

            return [TextContent(type="text", text=response)]

        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        sys.stderr.write(f"{error_msg}\n")
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Run MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        sys.stderr.write("RAG MCP Server starting...\n")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
