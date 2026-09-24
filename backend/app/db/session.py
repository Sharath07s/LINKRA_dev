import ssl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

connect_args = {}
if "supabase.com" in settings.POSTGRES_SERVER or "pooler" in settings.POSTGRES_SERVER:
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl_context"] = ssl_ctx

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
