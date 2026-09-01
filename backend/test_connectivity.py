import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import psycopg2
import socket
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dns():
    try:
        host = settings.POSTGRES_SERVER
        ip = socket.gethostbyname(host)
        logger.info(f"DNS Resolution successful: {host} -> {ip}")
        return True
    except socket.gaierror as e:
        logger.error(f"DNS Resolution failed for {host}: {e}")
        return False

def test_db_connectivity():
    # Hide password from URI string for logging
    uri = settings.SQLALCHEMY_DATABASE_URI
    safe_uri = uri.replace(settings.POSTGRES_PASSWORD, "****")
    
    logger.info("Testing SQLAlchemy connection to Supabase...")
    try:
        # We need to add connect_args={'sslmode': 'require'} for Supabase usually, 
        # but let's test what the app actually does.
        engine = create_engine(uri, pool_pre_ping=True)
        with engine.connect() as connection:
            logger.info("Successfully connected to the PostgreSQL database.")
            from sqlalchemy import text
            result = connection.execute(text("SELECT version();")).scalar()
            logger.info(f"Database version: {result}")
        return True
    except OperationalError as e:
        logger.error(f"Failed to connect to the database. Error: {str(e).replace(settings.POSTGRES_PASSWORD, '****')}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e).replace(settings.POSTGRES_PASSWORD, '****')}")
        return False

if __name__ == "__main__":
    logger.info("Starting Phase B: Supabase Connectivity Test")
    dns_ok = test_dns()
    if not dns_ok:
        sys.exit(1)
        
    db_ok = test_db_connectivity()
    if not db_ok:
        sys.exit(1)
        
    logger.info("Connectivity Test Passed.")
    sys.exit(0)
