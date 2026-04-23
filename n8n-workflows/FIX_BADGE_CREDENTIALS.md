# Fix Badge Unlock Workflow Credentials

## Problem
Badge Unlock workflow needs PostgreSQL credentials configured in n8n UI.

## Steps to Fix

### 1. Access n8n UI
```
http://167.86.116.51:5678
```

### 2. Go to Settings → Credentials

### 3. Create PostgreSQL Credential
**Name:** `Supabase PostgreSQL`
**Type:** PostgreSQL

**Connection Details:**
- **Host:** `db.ufblzfxqwgaekrewncbi.supabase.co`
- **Port:** `5432`
- **Database:** `postgres`
- **User:** `postgres`
- **Password:** [Your Supabase password]
- **SSL:** `require`

### 4. Create Twitter OAuth2 Credential
**Name:** `Twitter OAuth2`
**Type:** Twitter OAuth2 API

**Connection Details:**
- **Client ID:** [Your Twitter App Client ID]
- **Client Secret:** [Your Twitter App Client Secret]

### 5. Create Discord Webhook Credential
**Name:** `Discord Webhook`
**Type:** Discord Webhook

**Connection Details:**
- **Webhook URL:** `https://discord.com/api/webhooks/[YOUR_WEBHOOK_ID]/[YOUR_WEBHOOK_TOKEN]`

### 6. Update Workflow
In the Badge Unlock workflow:
- Select `Badge Earned Trigger` node
- Change credential from `postgres-creds` to `Supabase PostgreSQL`
- Repeat for `Get Badge Details` and `Get User Details` nodes
- Save workflow

### 7. Activate Workflow
Toggle the workflow to **ACTIVE**

## Verify
Test by inserting a badge record:
```sql
INSERT INTO user_badges (user_id, badge_id) VALUES ('test-user-id', 'rare-badge-id');
```

Check if notifications are sent to Discord/X.

## Alternative: Use Webhook Instead
If PostgreSQL trigger is problematic, replace with HTTP webhook:
1. Delete `Badge Earned Trigger` node
2. Add `Webhook` node as trigger
3. Set webhook URL: `/webhook/badge-unlock`
4. Update Supabase to send webhook on badge insert
