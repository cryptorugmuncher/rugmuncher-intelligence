# Vercel Deployment Guide

## Prerequisites
- Vercel account connected to your GitHub
- Domain: rugmunch.io configured in Vercel

## Current Setup
✅ vercel.json configured
✅ dist/ folder ready with built assets
✅ Routing configured
✅ Headers set for caching

## Deploy Steps

### Method 1: Vercel CLI (Recommended)
```bash
cd /root/rmi/rmi-frontend

# Login (first time only)
vercel login

# Link project
vercel link

# Deploy to production
vercel --prod
```

### Method 2: Git Push (Auto-deploy)
```bash
cd /root/rmi/rmi-frontend

# Initialize git if not already
git init
git add .
git commit -m "Initial deploy"

# Push to GitHub (triggers auto-deploy)
git push origin main
```

### Method 3: Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Import Git repository
3. Select /root/rmi/rmi-frontend
4. Deploy

## Post-Deployment

### Configure Domain
1. In Vercel dashboard, go to Project Settings → Domains
2. Add: `rugmunch.io`
3. Update DNS at your registrar:
   - Type: CNAME
   - Name: @
   - Value: cname.vercel-dns.com

### Environment Variables
Add these in Vercel dashboard (Settings → Environment Variables):
- `NEXT_PUBLIC_SUPABASE_URL`: https://ufblzfxqwgaekrewncbi.supabase.co
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: [your-anon-key]
- `API_URL`: https://api-internal.rugmunch.io

## Current Deploy URL
After deployment, your site will be at:
- Production: https://rugmunch.io (after domain config)
- Preview: https://[project-name]-rugmunch.vercel.app

## Troubleshooting
If build fails:
```bash
# Rebuild from source
cd /root/rmi/rmi-frontend
npm install --legacy-peer-deps
npm run build
vercel --prod
```

## Architecture
```
User → rugmunch.io (Vercel Edge)
  ├── Static assets (CDN)
  ├── API routes → Cloudflare Tunnel → Your server
  └── Real-time → Supabase
```

Your server IP remains hidden behind Cloudflare Tunnel.
