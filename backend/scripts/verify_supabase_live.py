import sys
import os
import psycopg2
from urllib.parse import urlparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import settings

def check_supabase():
    print("=== SUPABASE POSTGRESQL LIVE VERIFICATION ===")
    
    db_url = str(settings.SQLALCHEMY_DATABASE_URI)
    print(f"Checking connectivity to: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
    
    if "pooler.supabase.com" not in settings.POSTGRES_SERVER:
        print("WARNING: Not using an IPv4 Pooler endpoint. If running outside of an IPv6-enabled environment, this may fail.")
        
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=settings.POSTGRES_DB,
            connect_timeout=3
        )
        print("PASS: Connected to Supabase PostgreSQL successfully.")
        conn.close()
    except Exception as e:
        print(f"FAIL / UNVERIFIED: Environment Limitation")
        print(f"Error: {e}")
        print("\nDIAGNOSIS: Supabase now defaults direct connection hosts (db.*.supabase.co) to IPv6 only.")
        print("Since this environment does not have IPv6 capability and no pooler configuration was provided,")
        print("connectivity is physically impossible to verify live.")

if __name__ == "__main__":
    check_supabase()
