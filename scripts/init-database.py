#!/usr/bin/env python3
"""
Initialize RMI Database Schema
==============================
Creates all tables if they don't exist.
Run this before creating API keys.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Load env
with open('/root/rmi/v2/api/.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            os.environ[key] = val.strip('"').strip("'")

DATABASE_URL = os.environ.get('DATABASE_URL', '')
ASYNC_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

async def init_db():
    engine = create_async_engine(ASYNC_URL, echo=False)

    async with engine.begin() as conn:
        print("Creating tables...")

        # Create tables
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                telegram_id VARCHAR(50) UNIQUE,
                email VARCHAR(255) UNIQUE,
                wallet_address VARCHAR(42) UNIQUE,
                username VARCHAR(50),
                display_name VARCHAR(100),
                avatar_url VARCHAR(500),
                tier VARCHAR(20) DEFAULT 'FREE',
                tier_expires_at TIMESTAMP WITH TIME ZONE,
                scans_this_month INTEGER DEFAULT 0,
                scans_limit INTEGER DEFAULT 10,
                last_scan_at TIMESTAMP WITH TIME ZONE,
                karma_score INTEGER DEFAULT 0,
                badges JSONB DEFAULT '[]',
                is_trader BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                last_active_at TIMESTAMP WITH TIME ZONE,
                joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                stripe_customer_id VARCHAR(100),
                stripe_subscription_id VARCHAR(100) UNIQUE,
                stripe_price_id VARCHAR(100),
                tier VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'trialing',
                amount_usd FLOAT NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                current_period_start TIMESTAMP WITH TIME ZONE,
                current_period_end TIMESTAMP WITH TIME ZONE,
                trial_end TIMESTAMP WITH TIME ZONE,
                cancelled_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alerts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                alert_type VARCHAR(50) NOT NULL,
                channel VARCHAR(20) NOT NULL,
                payload JSONB NOT NULL,
                delivery_status VARCHAR(20) DEFAULT 'pending',
                delivered_at TIMESTAMP WITH TIME ZONE,
                error_message VARCHAR(500),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS contracts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                address VARCHAR(42) NOT NULL,
                chain VARCHAR(20) NOT NULL,
                bytecode_hash VARCHAR(64),
                creator_address VARCHAR(42),
                creation_tx_hash VARCHAR(66),
                creation_block BIGINT,
                verified BOOLEAN DEFAULT FALSE,
                verified_source TEXT,
                contract_name VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))

        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_contracts_address_chain
            ON contracts(address, chain);
        """))

        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_contracts_creator
            ON contracts(creator_address);
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS scans (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
                status VARCHAR(20) DEFAULT 'pending',
                overall_score INTEGER,
                risk_level VARCHAR(20),
                honeypot_risk INTEGER,
                rugpull_risk INTEGER,
                ownership_risk INTEGER,
                liquidity_risk INTEGER,
                code_risk INTEGER,
                findings JSONB DEFAULT '{}',
                warnings JSONB DEFAULT '[]',
                indicators JSONB DEFAULT '[]',
                token_name VARCHAR(255),
                token_symbol VARCHAR(20),
                token_decimals INTEGER,
                total_supply VARCHAR(50),
                price_usd FLOAT,
                market_cap FLOAT,
                liquidity_usd FLOAT,
                holder_count INTEGER,
                requested_by VARCHAR(50),
                completed_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))

        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                key_hash VARCHAR(64) UNIQUE NOT NULL,
                key_preview VARCHAR(10),
                permissions JSONB DEFAULT '["read"]',
                is_active BOOLEAN DEFAULT TRUE,
                request_count INTEGER DEFAULT 0,
                last_used_at TIMESTAMP WITH TIME ZONE,
                expires_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))

        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
        """))

        print("✓ Tables created successfully")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
