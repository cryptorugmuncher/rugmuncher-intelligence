#!/bin/bash
# Direct PostgreSQL connection through Boundary
# This creates a session and connects via the worker proxy

BOUNDARY_ADDR="http://localhost:9200"
TARGET_ID="ttcp_4cU45NF0Kc"

# Authenticate
echo "Authenticating..."
echo "JHXhwmrnQZKO5RasfYuI" > /tmp/boundary_pass
TOKEN=$(boundary authenticate password -login-name=admin -password=file:///tmp/boundary_pass -keyring-type=none 2>&1 | grep "^at_" | head -1 | sed 's/[[:space:]]*$//')

if [ -z "$TOKEN" ]; then
    echo "Authentication failed"
    exit 1
fi

# Authorize session via API
echo "Authorizing session to PostgreSQL..."
AUTH_RESP=$(curl -s -X POST "${BOUNDARY_ADDR}/v1/targets/${TARGET_ID}:authorize-session" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

if echo "$AUTH_RESP" | grep -q "error"; then
    echo "Failed: $AUTH_RESP"
    exit 1
fi

# Parse response
SESSION_ID=$(echo "$AUTH_RESP" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
WORKER_ADDR=$(echo "$AUTH_RESP" | grep -o '"worker_info":\[{"address":"[^"]*"' | cut -d'"' -f6)

echo ""
echo "========================================"
echo "SESSION AUTHORIZED: $SESSION_ID"
echo "========================================"
echo ""
echo "Connection Details:"
echo "  Host: 127.0.0.1"
echo "  Port: 5432"
echo "  Database: rmi_db"
echo "  User: rmi_user"
echo "  Password: rmi_pass"
echo ""
echo "Connection URL:"
echo "postgresql://rmi_user:rmi_pass@127.0.0.1:5432/rmi_db"
echo ""
echo "psql command:"
echo "psql -h 127.0.0.1 -p 5432 -U rmi_user -d rmi_db"
echo ""
echo "Session expires in 8 hours"
echo "========================================"
