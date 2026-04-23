"""
Vertex AI Integration for RMI Investigation System
Provides access to Google's Gemini models, embeddings, and other Vertex AI services
"""

import os
import json
import base64
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, ChatSession, Part
from vertexai.preview.embedding import EmbeddingModel
import vertexai


class VertexAIModel(str, Enum):
    """Available Vertex AI models"""

    GEMINI_2_5_PRO = "gemini-2.5-pro-preview-03-25"
    GEMINI_2_0_FLASH = "gemini-2.0-flash-001"
    GEMINI_1_5_PRO = "gemini-1.5-pro-002"
    GEMINI_1_5_FLASH = "gemini-1.5-flash-002"
    EMBEDDINGS = "text-embedding-004"
    MULTIMODAL_EMBEDDINGS = "multimodalembedding@001"


@dataclass
class VertexAIConfig:
    """Configuration for Vertex AI"""

    project_id: str
    location: str = "us-central1"
    credentials_path: Optional[str] = None


@dataclass
class InvestigationAnalysis:
    """Result from analyzing investigation data"""

    summary: str
    risk_factors: List[str]
    recommended_actions: List[str]
    confidence_score: float
    entity_relationships: Dict[str, Any]


class VertexAIClient:
    """
    Google Vertex AI client for RMI investigation system
    Provides: Gemini chat, embeddings, document analysis, multimodal processing
    """

    def __init__(self, config: Optional[VertexAIConfig] = None):
        """Initialize Vertex AI client"""
        self.config = config or self._load_config_from_env()
        self._init_vertex_ai()
        self._models: Dict[str, Any] = {}

    def _load_config_from_env(self) -> VertexAIConfig:
        """Load configuration from environment variables"""
        return VertexAIConfig(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
            location=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
            credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        )

    def _init_vertex_ai(self):
        """Initialize Vertex AI SDK"""
        if not self.config.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")

        vertexai.init(
            project=self.config.project_id,
            location=self.config.location,
            credentials=self.config.credentials_path,
        )

    def get_model(self, model_name: str) -> GenerativeModel:
        """Get or create a generative model instance"""
        if model_name not in self._models:
            self._models[model_name] = GenerativeModel(model_name)
        return self._models[model_name]

    async def generate_investigation_summary(
        self,
        evidence_data: Dict[str, Any],
        wallet_data: Optional[List[Dict]] = None,
        model: str = VertexAIModel.GEMINI_2_5_PRO,
    ) -> InvestigationAnalysis:
        """
        Generate comprehensive investigation summary

        Args:
            evidence_data: Structured evidence from investigation
            wallet_data: Optional wallet tracing data
            model: Which Gemini model to use

        Returns:
            InvestigationAnalysis with summary, risks, and recommendations
        """
        # Build comprehensive prompt
        prompt = self._build_investigation_prompt(evidence_data, wallet_data)

        # Get model and generate
        gemini_model = self.get_model(model)

        # Run in thread pool since Vertex AI SDK is synchronous
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: gemini_model.generate_content(prompt)
        )

        # Parse structured response
        return self._parse_investigation_response(response.text)

    def _build_investigation_prompt(
        self, evidence_data: Dict[str, Any], wallet_data: Optional[List[Dict]]
    ) -> str:
        """Build investigation analysis prompt"""
        prompt = f"""You are an expert crypto fraud investigator analyzing evidence for a potential rug pull or scam.

## EVIDENCE DATA:
{json.dumps(evidence_data, indent=2)}

"""
        if wallet_data:
            prompt += f"""## WALLET ANALYSIS DATA:
{json.dumps(wallet_data, indent=2)}

"""

        prompt += """## ANALYSIS REQUIREMENTS:
Please provide a structured analysis in the following format:

**SUMMARY:**
[Brief 2-3 sentence summary of the investigation findings]

**RISK FACTORS (list):**
- [Risk factor 1]
- [Risk factor 2]
- [etc]

**RECOMMENDED ACTIONS (list):**
- [Action 1]
- [Action 2]
- [etc]

**CONFIDENCE SCORE:** [0.0-1.0]

**ENTITY RELATIONSHIPS:**
[Describe relationships between wallets, entities, and suspicious patterns]

Be thorough but concise. Focus on actionable intelligence."""

        return prompt

    def _parse_investigation_response(self, text: str) -> InvestigationAnalysis:
        """Parse structured response from Gemini"""
        lines = text.split("\n")

        summary = ""
        risk_factors = []
        recommended_actions = []
        confidence_score = 0.5
        entity_relationships = {}

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("**SUMMARY:**"):
                current_section = "summary"
                continue
            elif line.startswith("**RISK FACTORS"):
                current_section = "risks"
                continue
            elif line.startswith("**RECOMMENDED ACTIONS"):
                current_section = "actions"
                continue
            elif line.startswith("**CONFIDENCE SCORE:**"):
                try:
                    score_text = line.split(":")[1].strip()
                    confidence_score = float(
                        score_text.replace("[", "").replace("]", "")
                    )
                except:
                    pass
                current_section = None
                continue
            elif line.startswith("**ENTITY RELATIONSHIPS:**"):
                current_section = "entities"
                continue

            if current_section == "summary":
                summary += line + " "
            elif current_section == "risks" and line.startswith("-"):
                risk_factors.append(line[1:].strip())
            elif current_section == "actions" and line.startswith("-"):
                recommended_actions.append(line[1:].strip())
            elif current_section == "entities":
                entity_relationships["raw"] = (
                    entity_relationships.get("raw", "") + line + "\n"
                )

        return InvestigationAnalysis(
            summary=summary.strip(),
            risk_factors=risk_factors,
            recommended_actions=recommended_actions,
            confidence_score=confidence_score,
            entity_relationships=entity_relationships,
        )

    async def analyze_screenshot(
        self,
        image_path: str,
        context: Optional[str] = None,
        model: str = VertexAIModel.GEMINI_2_0_FLASH,
    ) -> Dict[str, Any]:
        """
        Analyze investigation screenshot/image using multimodal Gemini

        Args:
            image_path: Path to image file
            context: Optional context about the image
            model: Gemini model to use

        Returns:
            Dict with analysis results
        """
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = f.read()

        image_part = Part.from_data(image_data, mime_type="image/png")

        prompt = """Analyze this crypto investigation screenshot. Identify:
1. Any wallet addresses visible
2. Transaction hashes
3. Token symbols or contract addresses
4. Suspicious indicators
5. Exchange or platform identifiers
6. People or entities mentioned

Format as JSON with these keys: wallets, transactions, tokens, risk_indicators, platforms, entities"""

        if context:
            prompt = f"Context: {context}\n\n{prompt}"

        gemini_model = self.get_model(model)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: gemini_model.generate_content([image_part, prompt])
        )

        # Try to parse as JSON
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"raw_analysis": response.text, "parsed": False}

    async def generate_embeddings(
        self, texts: List[str], model: str = VertexAIModel.EMBEDDINGS
    ) -> List[List[float]]:
        """
        Generate embeddings for semantic search

        Args:
            texts: List of text strings to embed
            model: Embedding model to use

        Returns:
            List of embedding vectors
        """
        embedding_model = EmbeddingModel.from_pretrained(model)

        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: [
                embedding_model.get_embeddings([text])[0].values for text in texts
            ],
        )

        return embeddings

    async def chat_investigation(
        self,
        message: str,
        history: Optional[List[Dict]] = None,
        model: str = VertexAIModel.GEMINI_1_5_FLASH,
    ) -> str:
        """
        Chat with Gemini about investigation context

        Args:
            message: User message
            history: Optional conversation history
            model: Model to use

        Returns:
            Response text
        """
        gemini_model = self.get_model(model)

        # Start or continue chat
        if history:
            chat = gemini_model.start_chat(history=history)
        else:
            chat = gemini_model.start_chat()

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: chat.send_message(message))

        return response.text

    async def stream_investigation_analysis(
        self, evidence_data: Dict[str, Any], model: str = VertexAIModel.GEMINI_2_0_FLASH
    ) -> AsyncGenerator[str, None]:
        """
        Stream investigation analysis in real-time

        Args:
            evidence_data: Evidence to analyze
            model: Model to use

        Yields:
            Text chunks as they're generated
        """
        prompt = self._build_investigation_prompt(evidence_data, None)
        gemini_model = self.get_model(model)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: gemini_model.generate_content(prompt, stream=True)
        )

        for chunk in response:
            yield chunk.text

    def create_embedding_index(
        self,
        index_name: str,
        dimension: int = 768,
        description: str = "RMI investigation evidence embeddings",
    ) -> str:
        """
        Create a Vertex AI Matching Engine index for vector search

        Args:
            index_name: Name for the index
            dimension: Embedding dimension (768 for text-embedding-004)
            description: Index description

        Returns:
            Index resource name
        """
        from google.cloud.aiplatform.matching_engine import MatchingEngineIndex

        index = MatchingEngineIndex.create_tree_ah_index(
            display_name=index_name,
            contents_delta_uri="",  # Will be updated when deploying
            dimensions=dimension,
            approximate_neighbors_count=150,
            distance_measure_type="DOT_PRODUCT_DISTANCE",
            description=description,
            labels={"project": "rmi", "type": "investigation"},
        )

        return index.resource_name


# Singleton instance
_vertex_ai_client: Optional[VertexAIClient] = None


async def get_vertex_ai_client() -> VertexAIClient:
    """Get or create singleton Vertex AI client"""
    global _vertex_ai_client
    if _vertex_ai_client is None:
        _vertex_ai_client = VertexAIClient()
    return _vertex_ai_client


async def quick_investigation_summary(
    evidence_data: Dict[str, Any], wallet_data: Optional[List[Dict]] = None
) -> InvestigationAnalysis:
    """Quick helper to get investigation summary without managing client"""
    client = await get_vertex_ai_client()
    return await client.generate_investigation_summary(evidence_data, wallet_data)


async def analyze_evidence_image(
    image_path: str, context: Optional[str] = None
) -> Dict[str, Any]:
    """Quick helper to analyze an evidence image"""
    client = await get_vertex_ai_client()
    return await client.analyze_screenshot(image_path, context)


if __name__ == "__main__":
    # Test the integration
    async def test():
        client = VertexAIClient()
        print(f"✅ Vertex AI client initialized")
        print(f"   Project: {client.config.project_id}")
        print(f"   Location: {client.config.location}")

        # Test simple generation
        model = client.get_model(VertexAIModel.GEMINI_1_5_FLASH)
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: model.generate_content("Say hello in 5 words or less")
        )
        print(f"\n📝 Test response: {response.text}")

    asyncio.run(test())
