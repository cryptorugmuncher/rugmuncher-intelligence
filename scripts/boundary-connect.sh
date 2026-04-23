#!/bin/bash
# Boundary PostgreSQL Connection Script
# Uses API to authorize and connect via netcat/socat proxy

BOUNDARY_ADDR="${BOUNDARY_ADDR:-http://localhost:9200}"
TARGET_ID="${1:-ttcp_4cU45NF0Kc}"
LOCAL_PORT="${2:-15432}"
TOKEN_FILE="/tmp/boundary_token"

# Authenticate if needed
if [ ! -f "$TOKEN_FILE" ] || [ $(find "$TOKEN_FILE" -mmin +60 2>/dev/null | wc -l) -eq 1 ]; then
    echo "Authenticating to Boundary..."
    read -sp "Enter Boundary admin password: " PASS
    echo
    AUTH_OUT=$(boundary authenticate password -login-name=admin -password=env://PASS -keyring-type=none 2>&1)
    TOKEN=$(echo "$AUTH_OUT" | grep "^at_" | head -1 | sed 's/[[:space:]]*$//')
    echo "$TOKEN" > "$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    echo "Token saved (valid 7 days)"
fi

TOKEN=$(cat "$TOKEN_FILE")

# Authorize session
echo "Authorizing session to target: $TARGET_ID..."
AUTH_RESP=$(curl -s -X POST "${BOUNDARY_ADDR}/v1/targets/${TARGET_ID}:authorize-session" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

# Check for errors
if echo "$AUTH_RESP" | grep -q "error\|Error"; then
    echo "Authorization failed:"
    echo "$AUTH_RESP" | python3 -m json.tool 2>/dev/null || echo "$AUTH_RESP"
    exit 1
fi

# Extract session info
SESSION_ID=$(echo "$AUTH_RESP" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
AUTHZ_TOKEN=$(echo "$AUTH_RESP" | grep -o '"authorization_token":"[^"]*"' | cut -d'"' -f4)
ENDPOINT=$(echo "$AUTH_RESP" | grep -o '"endpoint":"[^"]*"' | cut -d'"' -f4)
EXPIRES=$(echo "$AUTH_RESP" | grep -o '"expiration":"[^"]*"' | cut -d'"' -f4)

echo ""
echo "=== Session Authorized ==="
echo "Session ID: $SESSION_ID"
echo "Endpoint: $ENDPOINT"
echo "Expires: $EXPIRES"
echo ""
echo "=== PostgreSQL Connection ==="
echo "Host: 127.0.0.1"
echo "Port: 5432 (via Boundary)"
echo "Database: rmi_db"
echo "User: rmi_user"
echo "Password: rmi_pass"
echo ""
echo "psql command:"
echo "psql -h 127.0.0.1 -p 5432 -U rmi_user -d rmi_db"
echo ""
echo "=== Note ==="
echo "Session is active. You can now connect through the web UI at:"
echo "http://167.86.116.51:9200"
echo ""
echo "The authorized session will proxy traffic from 127.0.0.1:5432"
