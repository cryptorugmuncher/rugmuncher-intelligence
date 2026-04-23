# ═══════════════════════════════════════════════════════════════════════════════
# RMI Vertex AI Integration - Quick Start Examples
# ═══════════════════════════════════════════════════════════════════════════════

import asyncio
import json
from typing import Dict, Any
import sys

sys.path.insert(0, "/root/rmi")

from integrations.vertex_ai_client import (
    VertexAIClient,
    VertexAIModel,
    get_vertex_ai_client,
    quick_investigation_summary,
    analyze_evidence_image,
)


async def example_basic_chat():
    """Example 1: Basic chat with Gemini"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Chat with Gemini")
    print("=" * 70)

    client = await get_vertex_ai_client()

    response = await client.chat_investigation(
        message="What are common signs of a crypto rug pull?",
        model=VertexAIModel.GEMINI_1_5_FLASH,
    )

    print(f"Response:\n{response}\n")


async def example_investigation_summary():
    """Example 2: Generate investigation summary"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Investigation Summary")
    print("=" * 70)

    evidence_data = {
        "token_name": "MoonRocket Finance",
        "contract_address": "0x1234...abcd",
        "launch_date": "2026-04-01",
        "red_flags": [
            "Anonymous team with no prior projects",
            "Unverified contract on Etherscan",
            "50% of supply held by 3 wallets",
            "Website created 3 days before launch",
        ],
        "transactions": [
            {"type": "mint", "amount": "1,000,000", "to": "0xdead...beef"},
            {"type": "transfer", "amount": "500,000", "to": "exchange_wallet"},
        ],
    }

    wallet_data = [
        {
            "address": "0xdead...beef",
            "risk_score": 85,
            "exchange": None,
            "balance": "$2.5M",
        },
        {
            "address": "0x1234...5678",
            "risk_score": 45,
            "exchange": "Binance",
            "balance": "$150K",
        },
    ]

    result = await quick_investigation_summary(evidence_data, wallet_data)

    print(f"\n📝 Summary:\n{result.summary}\n")
    print(f"⚠️  Risk Factors:")
    for risk in result.risk_factors:
        print(f"   - {risk}")
    print(f"\n✅ Recommended Actions:")
    for action in result.recommended_actions:
        print(f"   - {action}")
    print(f"\n📊 Confidence Score: {result.confidence_score:.2f}")


async def example_embeddings():
    """Example 3: Generate embeddings for semantic search"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Text Embeddings")
    print("=" * 70)

    client = await get_vertex_ai_client()

    texts = [
        "Rug pull scam where developers abandon project",
        "Pump and dump scheme with coordinated buying",
        "Liquidity removal from DEX causing price crash",
        "Honest DeFi project with transparent team",
    ]

    embeddings = await client.generate_embeddings(texts)

    print(f"Generated {len(embeddings)} embeddings")
    print(f"Embedding dimensions: {len(embeddings[0])}")
    print(f"First embedding (first 5 values): {embeddings[0][:5]}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("RMI VERTEX AI INTEGRATION - EXAMPLES")
    print("=" * 70)

    asyncio.run(example_basic_chat())
    asyncio.run(example_investigation_summary())
    asyncio.run(example_embeddings())

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)
