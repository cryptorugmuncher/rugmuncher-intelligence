"""
================================================================================
DATABASE SETUP SCRIPT
Evidence Fortress v4.0

Creates database, user, and schema.
================================================================================
"""

import asyncio
import asyncpg
import sys


async def setup_database():
    """Set up the Evidence Fortress database."""
    
    # Connect to default postgres database
    print("Connecting to PostgreSQL...")
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        database='postgres'
    )
    
    try:
        # Create database
        print("Creating database 'evidence_fortress'...")
        await conn.execute("""
            DROP DATABASE IF EXISTS evidence_fortress
        """)
        await conn.execute("""
            CREATE DATABASE evidence_fortress
        """)
        
        # Create user
        print("Creating user 'evidence_user'...")
        await conn.execute("""
            DROP USER IF EXISTS evidence_user
        """)
        await conn.execute("""
            CREATE USER evidence_user WITH PASSWORD 'evidence_pass_2026'
        """)
        
        # Grant permissions
        await conn.execute("""
            GRANT ALL PRIVILEGES ON DATABASE evidence_fortress TO evidence_user
        """)
        
        print("✓ Database and user created")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()
    
    # Connect to new database and run schema
    print("\nRunning schema...")
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        database='evidence_fortress'
    )
    
    try:
        # Read and execute schema
        with open('backend/database/schema.sql', 'r') as f:
            schema = f.read()
        
        await conn.execute(schema)
        print("✓ Schema created successfully")
        
    except Exception as e:
        print(f"Schema error: {e}")
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(setup_database())
