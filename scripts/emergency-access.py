#!/usr/bin/env python3
"""
RMI Emergency Access Tool
=========================
Use this if you:
- Lost all API keys
- Locked yourself out of admin access
- Need to create a new admin user/key
- Database permissions are broken

Usage:
    cd /root/rmi/v2/api
    python3 /root/rmi/scripts/emergency-access.py create-admin-key
    python3 /root/rmi/scripts/emergency-access.py list-keys
    python3 /root/rmi/scripts/emergency-access.py reset-key <key-id>
    python3 /root/rmi/scripts/emergency-access.py create-master-key

This script bypasses normal auth and connects directly to the database.
"""

import sys
import hashlib
import secrets
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Load env
import os
with open('/root/rmi/v2/api/.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            os.environ[key] = val.strip('"').strip("'")

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

# Convert to async URL if needed
if DATABASE_URL.startswith('postgresql://'):
    ASYNC_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
elif DATABASE_URL.startswith('postgresql+asyncpg://'):
    ASYNC_URL = DATABASE_URL
else:
    print(f"ERROR: Unsupported database URL format")
    sys.exit(1)

engine = create_async_engine(ASYNC_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def generate_api_key():
    """Generate a secure API key"""
    prefix = "rmi_"
    token = secrets.token_urlsafe(32)
    return prefix + token


def hash_key(key):
    """Hash an API key for storage"""
    return hashlib.sha256(key.encode()).hexdigest()


async def create_admin_key():
    """Create a new admin API key"""
    api_key = generate_api_key()
    key_hash = hash_key(api_key)
    key_preview = api_key[-6:]

    async with async_session() as session:
        # Check if we have a users table with any users
        result = await session.execute(text("""
            SELECT id FROM users LIMIT 1
        """))
        user = result.scalar()

        if not user:
            # Create emergency admin user
            result = await session.execute(text("""
                INSERT INTO users (id, email, tier, is_active, joined_at)
                VALUES (gen_random_uuid(), 'admin@emergency.local', 'ELITE', true, NOW())
                RETURNING id
            """))
            user = result.scalar()
            await session.commit()
            print(f"[+] Created emergency admin user: {user}")

        # Create the API key
        result = await session.execute(text("""
            INSERT INTO api_keys (id, user_id, name, key_hash, key_preview, permissions, is_active, created_at)
            VALUES (
                gen_random_uuid(),
                :user_id,
                'EMERGENCY ADMIN KEY',
                :key_hash,
                :preview,
                '["read", "write", "admin"]',
                true,
                NOW()
            )
            RETURNING id
        """), {
            'user_id': user,
            'key_hash': key_hash,
            'preview': key_preview
        })
        key_id = result.scalar()
        await session.commit()

        print("=" * 60)
        print("EMERGENCY ADMIN API KEY CREATED")
        print("=" * 60)
        print(f"Key ID: {key_id}")
        print(f"User ID: {user}")
        print("")
        print("YOUR NEW API KEY (SAVE THIS IMMEDIATELY):")
        print("")
        print(f"  {api_key}")
        print("")
        print("=" * 60)
        print("Usage:")
        print(f'  curl -H "Authorization: Bearer {api_key}" \\')
        print(f'    http://localhost:8000/api/v2/scans')
        print("=" * 60)


async def list_keys():
    """List all active API keys (for recovery)"""
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT
                k.id,
                k.name,
                k.key_preview,
                k.permissions::text,
                k.is_active,
                k.request_count,
                k.last_used_at,
                u.email as user_email
            FROM api_keys k
            LEFT JOIN users u ON k.user_id = u.id
            WHERE k.is_active = true
            ORDER BY k.last_used_at DESC NULLS LAST
        """))

        print("\nACTIVE API KEYS:")
        print("-" * 80)
        for row in result:
            print(f"ID:          {row.id}")
            print(f"Name:        {row.name}")
            print(f"Preview:     ...{row.key_preview}")
            print(f"User:        {row.user_email}")
            print(f"Permissions: {row.permissions}")
            print(f"Active:      {row.is_active}")
            print(f"Usage:       {row.request_count} requests")
            print(f"Last Used:   {row.last_used_at}")
            print("-" * 40)


async def reset_key(key_id):
    """Reset/revoke a specific key and create new one"""
    async with async_session() as session:
        # Get key info
        result = await session.execute(text("""
            SELECT user_id FROM api_keys WHERE id = :key_id
        """), {'key_id': key_id})
        row = result.scalar()

        if not row:
            print(f"ERROR: Key {key_id} not found")
            return

        # Revoke old key
        await session.execute(text("""
            UPDATE api_keys
            SET is_active = false, name = name || ' [REVOKED]'
            WHERE id = :key_id
        """), {'key_id': key_id})

        # Create new key
        api_key = generate_api_key()
        key_hash = hash_key(api_key)
        key_preview = api_key[-6:]

        result = await session.execute(text("""
            INSERT INTO api_keys (id, user_id, name, key_hash, key_preview, permissions, is_active, created_at)
            VALUES (
                gen_random_uuid(),
                (SELECT user_id FROM api_keys WHERE id = :old_key_id),
                'REPLACEMENT KEY',
                :key_hash,
                :preview,
                '["read", "write", "admin"]',
                true,
                NOW()
            )
            RETURNING id
        """), {
            'old_key_id': key_id,
            'key_hash': key_hash,
            'preview': key_preview
        })
        new_key_id = result.scalar()
        await session.commit()

        print(f"[+] Revoked old key: {key_id}")
        print("=" * 60)
        print("NEW REPLACEMENT KEY:")
        print("=" * 60)
        print(f"Key ID: {new_key_id}")
        print("")
        print(f"  {api_key}")
        print("")
        print("=" * 60)


async def create_master_key():
    """Create a permanent master key (for disaster recovery)"""
    # Use a deterministic but secure master key based on SECRET_KEY
    secret = os.environ.get('SECRET_KEY', 'fallback-secret')
    master_raw = f"rmi_master_{hashlib.sha256(secret.encode()).hexdigest()[:32]}"
    master_key = f"rmi_{master_raw}"
    key_hash = hash_key(master_key)

    async with async_session() as session:
        # Check if master key exists
        result = await session.execute(text("""
            SELECT id FROM api_keys WHERE key_hash = :hash
        """), {'hash': key_hash})

        if result.scalar():
            print("[!] Master key already exists in database")
            print("[!] If you've lost it, you need to regenerate SECRET_KEY")
            return

        # Get or create master user
        result = await session.execute(text("""
            SELECT id FROM users WHERE email = 'master@system.local' LIMIT 1
        """))
        user_id = result.scalar()

        if not user_id:
            result = await session.execute(text("""
                INSERT INTO users (id, email, tier, is_active, joined_at)
                VALUES (gen_random_uuid(), 'master@system.local', 'ENTERPRISE', true, NOW())
                RETURNING id
            """))
            user_id = result.scalar()

        # Insert master key
        result = await session.execute(text("""
            INSERT INTO api_keys (id, user_id, name, key_hash, key_preview, permissions, is_active, created_at)
            VALUES (
                gen_random_uuid(),
                :user_id,
                'MASTER RECOVERY KEY [GUARD THIS]',
                :key_hash,
                'MASTER',
                '["read", "write", "admin", "system"]',
                true,
                NOW()
            )
            RETURNING id
        """), {
            'user_id': user_id,
            'key_hash': key_hash
        })
        key_id = result.scalar()
        await session.commit()

        print("=" * 60)
        print("MASTER RECOVERY KEY CREATED")
        print("=" * 60)
        print("Key ID:", key_id)
        print("")
        print("THIS IS YOUR DISASTER RECOVERY KEY:")
        print(f"  {master_key}")
        print("")
        print("⚠️  WARNING: Store this in your password manager NOW")
        print("⚠️  This key can access everything and never expires")
        print("⚠️  It is derived from your SECRET_KEY")
        print("=" * 60)

        # Save to file with restricted permissions
        backup_file = '/root/rmi/backups/MASTER_KEY.txt'
        with open(backup_file, 'w') as f:
            f.write(f"RMI Master Recovery Key\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Key: {master_key}\n")
            f.write(f"Key ID: {key_id}\n")
        os.chmod(backup_file, 0o600)
        print(f"[+] Also saved to: {backup_file} (chmod 600)")


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCommands:")
        print("  create-admin-key    Create new admin API key")
        print("  list-keys           Show all active keys")
        print("  reset-key <id>      Revoke key and create replacement")
        print("  create-master-key   Create disaster recovery master key")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create-admin-key":
        await create_admin_key()
    elif command == "list-keys":
        await list_keys()
    elif command == "reset-key":
        if len(sys.argv) < 3:
            print("Usage: emergency-access.py reset-key <key-id>")
            sys.exit(1)
        await reset_key(sys.argv[2])
    elif command == "create-master-key":
        await create_master_key()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
