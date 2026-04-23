#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Google Vertex AI Setup Script for RMI
# Run this after creating your GCP project and service account
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "🔷 Google Vertex AI Setup for RMI"
echo "═══════════════════════════════════════════════════════════════════════════════"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}✅ gcloud CLI found${NC}"

# Get project ID from env or prompt
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
if [ -z "$PROJECT_ID" ]; then
    echo ""
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
fi

echo ""
echo -e "${BLUE}📋 Setting up project: $PROJECT_ID${NC}"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo ""
echo -e "${YELLOW}🔧 Enabling Vertex AI APIs...${NC}"
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com

# Create service account
SERVICE_ACCOUNT_NAME="rmi-vertex-ai"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo ""
echo -e "${YELLOW}👤 Creating service account: $SERVICE_ACCOUNT_NAME${NC}"

# Check if service account exists
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL &> /dev/null; then
    echo -e "${GREEN}✅ Service account already exists${NC}"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="RMI Vertex AI Service Account" \
        --description="Service account for RMI Vertex AI integration"
    echo -e "${GREEN}✅ Service account created${NC}"
fi

# Grant roles
echo ""
echo -e "${YELLOW}🔑 Granting IAM roles...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.objectViewer"

echo -e "${GREEN}✅ IAM roles granted${NC}"

# Create and download service account key
SECRETS_DIR="/root/.secrets"
KEY_FILE="${SECRETS_DIR}/gcp-service-account.json"

echo ""
echo -e "${YELLOW}🔐 Creating service account key...${NC}"

# Create secrets directory
mkdir -p $SECRETS_DIR
chmod 700 $SECRETS_DIR

# Check if key already exists
if [ -f "$KEY_FILE" ]; then
    echo -e "${YELLOW}⚠️  Key file already exists at $KEY_FILE${NC}"
    read -p "Overwrite? (y/N): " OVERWRITE
    if [[ $OVERWRITE =~ ^[Yy]$ ]]; then
        gcloud iam service-accounts keys create $KEY_FILE \
            --iam-account=$SERVICE_ACCOUNT_EMAIL
        echo -e "${GREEN}✅ New key downloaded${NC}"
    fi
else
    gcloud iam service-accounts keys create $KEY_FILE \
        --iam-account=$SERVICE_ACCOUNT_EMAIL
    echo -e "${GREEN}✅ Key downloaded to $KEY_FILE${NC}"
fi

# Set permissions
chmod 600 $KEY_FILE

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}Project ID:${NC}     $PROJECT_ID"
echo -e "${BLUE}Project Number:${NC} $PROJECT_NUMBER"
echo -e "${BLUE}Service Account:${NC} $SERVICE_ACCOUNT_EMAIL"
echo -e "${BLUE}Key File:${NC}       $KEY_FILE"
echo ""
echo "📝 Update your .env file with:"
echo "   GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
echo "   GOOGLE_CLOUD_PROJECT_NUMBER=$PROJECT_NUMBER"
echo "   GOOGLE_APPLICATION_CREDENTIALS=$KEY_FILE"
echo ""
echo "🧪 Test the setup:"
echo "   python3 /root/rmi/integrations/vertex_ai_client.py"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
