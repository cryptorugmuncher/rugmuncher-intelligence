#!/usr/bin/env python3
"""
Export API Keys for Backup
==========================
This exports your current API keys to an encrypted file.
Run this after creating keys so you have a record.

The export includes key IDs and previews (not full keys for security)
Use this to document which keys exist and who they belong to.
"""

import asyncio
import json
import os
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Load env
with open('/root/rmi/v2/api/.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            os.environ[key] = val.strip('"').strip("'")

DATABASE_URL = os.environ.get('DATABASE_URL', '')
ASYNC_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

engine = create_async_engine(ASYNC_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def export_keys():
    """Export all API keys to backup file"""
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT
                k.id,
                k.name,
                k.key_preview,
                k.permissions::text as permissions,
                k.is_active,
                k.request_count,
                k.created_at,
                k.last_used_at,
                u.email as user_email,
                u.tier as user_tier
            FROM api_keys k
            LEFT JOIN users u ON k.user_id = u.id
            ORDER BY k.created_at DESC
        """))

        keys = []
        for row in result:
            keys.append({
                'id': str(row.id),
                'name': row.name,
                'preview': f"...{row.key_preview}" if row.key_preview else None,
                'user_email': row.user_email,
                'user_tier': row.user_tier,
                'permissions': row.permissions,
                'is_active': row.is_active,
                'request_count': row.request_count,
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'last_used_at': row.last_used_at.isoformat() if row.last_used_at else None,
            })

        export_data = {
            'exported_at': datetime.now().isoformat(),
            'database': ASYNC_URL.split('@')[-1] if '@' in ASYNC_URL else 'unknown',
            'total_keys': len(keys),
            'active_keys': sum(1 for k in keys if k['is_active']),
            'keys': keys
        }

        # Save to file
        backup_file = f"/root/rmi/backups/api_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        # Also save latest
        latest_file = "/root/rmi/backups/api_keys_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        os.chmod(backup_file, 0o600)
        os.chmod(latest_file, 0o600)

        print(f"[+] Exported {len(keys)} keys to: {backup_file}")
        print(f"[+] Also saved to: {latest_file}")
        print()
        print(f"Active keys: {export_data['active_keys']}")
        print(f"Inactive keys: {export_data['total_keys'] - export_data['active_keys']}")

        # Summary table
        print()
        print("KEYS SUMMARY:")
        print("-" * 80)
        for key in keys[:10]:  # Show first 10
            status = "✓" if key['is_active'] else "✗"
            print(f"{status} {key['name'][:30]:<30} {key['user_email'] or 'N/A':<25} {key['request_count']:>6} req")

        if len(keys) > 10:
            print(f"... and {len(keys) - 10} more")


if __name__ == "__main__":
    asyncio.run(export_keys())
