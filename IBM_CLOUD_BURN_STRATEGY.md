# IBM Cloud $200 Credit — Maximum Burn Strategy
## Fighter Jet Deployment: 30 Days to Zero Credits

**Credit:** $200 USD
**Expires:** 30 days
**Goal:** Extract maximum compute value, migrate workloads before expiry

---

## The "Burn Hierarchy" (Most Value First)

### Tier 1: GPU Compute (Highest Value)

| Service | Burn Rate | 30-Day Cost | Strategy |
|---------|-----------|-------------|----------|
| **Watsonx.ai GPU** | $2.50/hour (V100) | $1,800/mo | Run LLM inference, embeddings, model training |
| **Code Engine GPU** | $3.50/hour (A100) | $2,520/mo | Max out with batch ML jobs |

**Action:** Deploy immediately
```bash
# Watsonx.ai - GPU for model inference
# Deploy your RMI ML models for scam detection
ibmcloud watsonx.ai deployment create \
  --name rmi-scam-detector \
  --model rmi_xgboost_model.pkl \
  --hardware-spec V100

# Run batch inference on all historical contracts
# 24/7 for 7 days = $420 burn
```

### Tier 2: Bare Metal & VMs (Persistent Workloads)

| Service | Specs | Cost/Mo | Use For |
|---------|-------|---------|---------|
| **bx2d-metal-96x384** | 96 vCPU, 384GB RAM | $1,200/mo | TigerGraph database node |
| **mx2d-metal-96x1024** | 96 vCPU, 1TB RAM | $2,000/mo | In-memory graph cache |
| **cx2d-48x96** | 48 vCPU, 96GB RAM | $400/mo | Pre-compute workers |

**Action:** Deploy bare metal immediately
```bash
# Create bare metal for TigerGraph (graph database)
ibmcloud is bm-create \
  --name rmi-tigergraph-node \
  --profile bx2d-metal-96x384 \
  --image ubuntu-22-amd64 \
  --key rmi-ssh-key

# Install TigerGraph (native graph, 10x faster than Neo4j)
ssh root@<bare-metal-ip> << 'EOF'
curl -s https://dl.tigergraph.com/enterprise/tigergraph-3.9.0.tar.gz | tar xz
cd tigergraph*/ && sudo ./install.sh
EOF
```

### Tier 3: Kubernetes Clusters (Auto-scaling)

| Service | Cost | Use |
|---------|------|-----|
| **IKS (VPC)** | $0.10/hour + workers | Regional data processing |
| **OpenShift** | $0.20/hour + workers | Containerized pre-compute |

**Action:** Multi-region K8s deployment
```bash
# Create clusters in 3 regions (US, EU, APAC)
for region in us-south eu-de jp-tok; do
  ibmcloud ks cluster create vpc-gen2 \
    --name rmi-cluster-$region \
    --zone ${region}-1 \
    --flavor bx2.4x16 \
    --workers 3 \
    --kube-version 1.28
done

# 3 clusters × 3 workers × $0.40/hour = ~$850/mo
# Deploy RPC rotators to each region for latency
```

### Tier 4: Serverless Functions (Burst Compute)

| Service | Free Tier | Paid Burn |
|---------|-----------|-----------|
| **IBM Cloud Functions** | 400k GB-seconds | $0.000016/GB-sec |
| **Code Engine** | 100k vCPU-seconds | $0.000024/vCPU-sec |

**Action:** Pre-compute burst jobs
```python
# Deploy pre-compute workers to IBM Code Engine
# ibmcloud ce application create --name rmi-precompute

# Nightly burst: 1000 tokens × 10k wallets = 10M operations
# Run 100 parallel containers for 1 hour each
# 100 containers × 1 hour × $0.50 = $50/night
```

---

## RMI-Specific Burn Plan (30-Day Sprint)

### Week 1: Infrastructure Foundation

**Day 1-2: Deploy Core**
- Bare metal TigerGraph node ($40/day = $280/week)
- Watsonx.ai GPU for ML training ($60/day = $420/week)
- 3-region IKS clusters ($120/day = $840/week)

**Day 3-4: Data Migration**
- Migrate graph data to IBM TigerGraph
- Deploy RPC rotators to IBM Cloud Functions
- Pre-compute 100k wallet clusters

**Day 5-7: Burn Validation**
- Verify $200/day burn rate
- Monitor credit balance daily
- Adjust if under-burning

### Week 2-3: Maximum Compute

**ML Training Sprint**
```python
# Train scam detection model on full dataset
# Watsonx.ai with 4× V100 GPUs
# 24/7 training for 14 days
# 4 GPUs × $2.50/hr × 336 hours = $3,360 (scaled down to credit limit)
```

**Graph Analytics**
- Run Louvain clustering on 1M wallet nodes
- Compute cross-chain bridge heuristics
- Generate risk scores for all tracked tokens

**Burst Processing**
- Backfill 6 months of transaction data
- Compute gas-funding trees for top 1000 tokens
- Batch embedding generation for contracts

### Week 4: Migrate & Preserve

**Before Credit Expires:**
1. Export all trained models (Watsonx → local)
2. Backup TigerGraph to S3 (IBM COS)
3. Migrate IKS workloads to GCP/AWS free tiers
4. Snapshot bare metal to custom image

---

## Cost Monitoring

```bash
# Daily burn check script
#!/bin/bash
# /root/rmi/scripts/ibm-cloud-burn-check.sh

CREDIT_REMAINING=$(ibmcloud billing account-usage --json | jq '.resources[].cost')
DAYS_LEFT=30
TARGET_BURN_PER_DAY=6.67  # $200 / 30 days

echo "IBM Cloud Credit Burn Report"
echo "Remaining: $CREDIT_REMAINING"
echo "Target daily: $TARGET_BURN_PER_DAY"
echo "Status: $(if (( $(echo "$CREDIT_REMAINING / $DAYS_LEFT" | bc -l) > $TARGET_BURN_PER_DAY )); then echo "UNDER-BURNING"; else echo "ON TRACK"; fi)"
```

---

## Automation: Auto-Scale to Burn

```yaml
# ibmcloud-autoscaler.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rmi-precompute-autoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rmi-precompute
  minReplicas: 10
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
```

---

## Summary: The Burn Formula

| Week | Primary Burn | Daily Rate | Weekly Total |
|------|--------------|------------|--------------|
| 1 | Bare metal + Watsonx | $200/day | $1,400 |
| 2 | GPU training + IKS | $250/day | $1,750 |
| 3 | Burst compute + Code Engine | $300/day | $2,100 |
| 4 | Migration prep | $100/day | $700 |

**Total extractable value:** $5,950 equivalent compute for $200

---

## Immediate Actions (Do Today)

1. **Sign up:** https://cloud.ibm.com/registration
2. **Verify:** Credit card (not charged if in free tier)
3. **Deploy:**
   ```bash
   ibmcloud login
   ibmcloud target -r us-south
   ibmcloud is bm-create --name rmi-burn-1 --profile bx2d-metal-96x384
   ```
4. **Monitor:** Set daily burn alerts at $5, $10, $15 thresholds

**Result:** Zero cost, maximum compute, all data preserved before expiry.
