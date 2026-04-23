"""
Mirror.xyz Publisher Integration
================================
Publish newsletters to Mirror.xyz (Web3 publishing platform).

Environment:
    MIRROR_API_KEY - Mirror API key (if available)
    MIRROR_SIGNER_PRIVATE_KEY - Optional: sign transactions directly

Mirror uses a GraphQL API. Articles are published as Arweave transactions.
For now we support:
  - Draft creation via API
  - Publishing via wallet signature (advanced)
  - Linking to published Mirror posts in newsletter records
"""
import os
import json
from typing import Optional, Dict, Any
import httpx

MIRROR_API_KEY = os.getenv("MIRROR_API_KEY", "")
MIRROR_API_URL = "https://mirror-api.com/graphql"


class MirrorPublisher:
    def __init__(self):
        self.api_key = MIRROR_API_KEY
        self.enabled = bool(self.api_key)

    async def publish_article(
        self,
        title: str,
        body: str,
        tags: Optional[list] = None,
        cover_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Publish an article to Mirror.xyz. Returns Arweave tx hash and Mirror URL."""
        if not self.enabled:
            return {
                "status": "demo",
                "message": "Mirror publishing is in demo mode. Add MIRROR_API_KEY to enable.",
                "title": title,
                "url": f"https://mirror.xyz/demo/{title.lower().replace(' ', '-')}",
                "arweave_tx": "demo_tx_" + str(hash(title) % 1000000),
            }

        # GraphQL mutation for creating entry
        mutation = """
        mutation CreateEntry($input: CreateEntryInput!) {
          createEntry(input: $input) {
            id
            title
            body
            digest
            arweaveTransactionRequest {
              transactionId
              slug
            }
          }
        }
        """
        variables = {
            "input": {
                "title": title,
                "body": body,
                "tags": tags or ["crypto", "rugpull", "intelligence"],
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                MIRROR_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                json={"query": mutation, "variables": variables},
            )
            data = resp.json()
            if "errors" in data:
                return {"status": "error", "errors": data["errors"]}

            entry = data["data"]["createEntry"]
            arweave = entry.get("arweaveTransactionRequest", {})
            return {
                "status": "published",
                "mirror_id": entry["id"],
                "title": entry["title"],
                "digest": entry.get("digest"),
                "arweave_tx": arweave.get("transactionId"),
                "slug": arweave.get("slug"),
                "url": f"https://mirror.xyz/{arweave.get('slug', '')}",
            }

    async def get_publications(self, address: str) -> Dict[str, Any]:
        """Get publications for a wallet address."""
        if not self.enabled:
            return {"status": "demo", "publications": []}

        query = """
        query Publications($address: String!) {
          user(address: $address) {
            publications {
              title
              digest
              timestamp
            }
          }
        }
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                MIRROR_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                json={"query": query, "variables": {"address": address}},
            )
            return {"status": "ok", "data": resp.json()}


mirror_publisher = MirrorPublisher()
