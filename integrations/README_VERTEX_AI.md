# 🔷 Google Vertex AI Integration for RMI

Full-featured Vertex AI integration for the Rug Muncher Investigation (RMI) platform. Provides access to Google's Gemini models, embeddings API, and multimodal capabilities for crypto fraud investigation.

## 🎯 Features

- **Gemini Chat Models**: 2.5 Pro, 2.0 Flash, 1.5 Pro, 1.5 Flash
- **Text Embeddings**: Semantic search with text-embedding-004 (768-dim)
- **Multimodal Analysis**: Screenshot/image analysis for evidence processing
- **Streaming Responses**: Real-time investigation analysis
- **Vector Search**: Vertex AI Matching Engine integration

## 📁 Files

```
/rmi/integrations/
├── vertex_ai_client.py              # Main client class
├── vertex_ai_examples.py            # Usage examples
├── requirements-vertex-ai.txt       # Python dependencies
└── .github/workflows/
    └── vertex-ai-deploy.yml         # GitHub Actions CI/CD

/rmi/scripts/setup/
└── setup_vertex_ai.sh               # Automated setup script
```

## 🚀 Quick Start

### 1. Sign up for Google Cloud Free Tier

- Go to [Google Cloud Console](https://console.cloud.google.com)
- Create a new project (or use existing)
- Enable billing (you get $300 free credits for 90 days)
- Note your **Project ID** and **Project Number**

### 2. Run Setup Script

```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT=your-project-id

# Run automated setup
bash /root/rmi/scripts/setup/setup_vertex_ai.sh
```

This will:
- Enable Vertex AI APIs
- Create a service account
- Download service account key to `/root/.secrets/gcp-service-account.json`
- Grant necessary IAM permissions

### 3. Configure Environment

Update `/root/.env`:

```bash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_PROJECT_NUMBER=your-project-number
VERTEX_AI_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/root/.secrets/gcp-service-account.json
```

### 4. Install Dependencies

```bash
cd /root/rmi
pip install -r integrations/requirements-vertex-ai.txt
```

### 5. Test the Integration

```bash
# Run basic test
python3 /root/rmi/integrations/vertex_ai_client.py

# Run examples
python3 /root/rmi/integrations/vertex_ai_examples.py
```

## 💻 Usage Examples

### Basic Chat

```python
import asyncio
from integrations.vertex_ai_client import get_vertex_ai_client, VertexAIModel

async def main():
    client = await get_vertex_ai_client()
    
    response = await client.chat_investigation(
        message="Analyze this wallet behavior: 0x1234...",
        model=VertexAIModel.GEMINI_2_5_PRO
    )
    print(response)

asyncio.run(main())
```

### Investigation Summary

```python
from integrations.vertex_ai_client import quick_investigation_summary

evidence_data = {
    "token_name": "Suspicious Token",
    "red_flags": ["Anonymous team", "Unverified contract"],
    "transactions": [...]
}

result = await quick_investigation_summary(evidence_data)
print(f"Summary: {result.summary}")
print(f"Risk Factors: {result.risk_factors}")
```

### Screenshot Analysis

```python
from integrations.vertex_ai_client import analyze_evidence_image

result = await analyze_evidence_image(
    image_path="/path/to/telegram_screenshot.png",
    context="Suspicious investment discussion"
)
print(result["wallets"])  # Extracted wallet addresses
```

### Generate Embeddings

```python
from integrations.vertex_ai_client import get_vertex_ai_client

client = await get_vertex_ai_client()

texts = [
    "Rug pull scam where developers abandon project",
    "Pump and dump scheme with coordinated buying"
]

embeddings = await client.generate_embeddings(texts)
# embeddings[0] is a 768-dimensional vector
```

### Streaming Analysis

```python
async for chunk in client.stream_investigation_analysis(evidence_data):
    print(chunk, end="", flush=True)
```

## 🔧 Available Models

| Model | Description | Best For |
|-------|-------------|----------|
| `gemini-2.5-pro-preview-03-25` | Most capable | Complex analysis, reasoning |
| `gemini-2.0-flash-001` | Fast multimodal | Real-time image analysis |
| `gemini-1.5-pro-002` | Long context | Large document analysis |
| `gemini-1.5-flash-002` | Fast & cheap | Quick summaries, chat |
| `text-embedding-004` | Embeddings | Semantic search (768-dim) |
| `multimodalembedding@001` | Multimodal embeddings | Image + text search |

## 🔐 Authentication

### Method 1: Service Account Key (Development)

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Method 2: Application Default Credentials (Production)

```bash
gcloud auth application-default login
```

### Method 3: GitHub Actions

Store the base64-encoded service account key as a GitHub secret:

```bash
# Encode key
cat gcp-service-account.json | base64 -w 0

# Add to GitHub Secrets as GCP_SERVICE_ACCOUNT_KEY
```

## 📊 GitHub Actions CI/CD

The integration includes automated deployment via GitHub Actions:

1. **Tests**: Run on every push
2. **Deploy**: Triggered on main branch pushes
3. **Notify**: Discord notification on completion

### Required GitHub Secrets

- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_CLOUD_PROJECT_NUMBER`: Your project number
- `GCP_SERVICE_ACCOUNT_KEY`: Base64-encoded service account key
- `DISCORD_WEBHOOK_URL` (optional): For deployment notifications

## 💰 Pricing

Vertex AI offers **free tier**:
- $300 credits for 90 days (new users)
- Gemini 1.5 Flash: ~$0.35/million tokens (input)
- Embeddings: ~$0.10/million tokens
- Storage: ~$0.10/GB/month

For typical RMI usage:
- 100 investigation summaries: ~$0.50
- 1000 image analyses: ~$2.00
- 10,000 embeddings: ~$1.00

## 🛠️ Troubleshooting

### "Project not found"
```bash
gcloud config set project YOUR_PROJECT_ID
```

### "API not enabled"
```bash
gcloud services enable aiplatform.googleapis.com
```

### "Permission denied"
Check IAM roles on service account:
- `roles/aiplatform.user`
- `roles/storage.objectViewer`

### "Module not found"
```bash
pip install google-cloud-aiplatform vertexai
```

## 📚 Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Reference](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [Embeddings API](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings)
- [Pricing Calculator](https://cloud.google.com/vertex-ai/pricing)

## 🔗 Integration with RMI

The Vertex AI client integrates seamlessly with existing RMI components:

```python
# Use with evidence processor
from tools.evidence_processor import EvidenceProcessor
from integrations.vertex_ai_client import analyze_evidence_image

processor = EvidenceProcessor()
for image_path in processor.get_images():
    analysis = await analyze_evidence_image(image_path)
    processor.add_metadata(image_path, analysis)

# Use with wallet tracer
from tools.wallet_tracer import WalletTracer
from integrations.vertex_ai_client import quick_investigation_summary

tracer = WalletTracer()
wallet_data = tracer.analyze_batch(addresses)
summary = await quick_investigation_summary(evidence_data, wallet_data)
```

## ✅ Checklist

Before using in production:

- [ ] Created GCP project
- [ ] Enabled Vertex AI API
- [ ] Created service account
- [ ] Downloaded service account key
- [ ] Set environment variables
- [ ] Installed dependencies
- [ ] Tested basic chat
- [ ] Tested image analysis
- [ ] Set up GitHub Actions secrets
- [ ] Configured Discord webhook (optional)

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review Vertex AI documentation
3. Check GCP project quotas and limits

---

**Built for RMI Investigation System** 🔍
