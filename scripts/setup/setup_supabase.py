import sys
sys.path.insert(0, '/root/rmi')
sys.path.insert(0, '/root/rmi/backend')

# Use the database connection manager which handles local PostgreSQL fallback
from database.connection import supabase

# Test connection
try:
    result = supabase.table('badges').select('*').limit(1).execute()
    print(f"✅ Database connected - {len(result.data)} records")
except Exception as e:
    print(f"⚠️ Database issue: {e}")
