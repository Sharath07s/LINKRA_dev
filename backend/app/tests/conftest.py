import os
import sqlite3
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Determine database URL: use PostgreSQL if configured via environment, else SQLite
TEST_DB_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DB_URL and os.getenv("POSTGRES_SERVER") and os.getenv("POSTGRES_PASSWORD"):
    TEST_DB_URL = settings.SQLALCHEMY_DATABASE_URI

if not TEST_DB_URL:
    TEST_DB_URL = "sqlite:///:memory:"

IS_SQLITE = TEST_DB_URL.startswith("sqlite")

if IS_SQLITE:
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # SpatiaLite no-op stubs for plain SQLite test runs
    @event.listens_for(Engine, "connect")
    def _set_sqlite_spatialite_stubs(dbapi_conn, connection_record):
        if isinstance(dbapi_conn, sqlite3.Connection):
            dbapi_conn.create_function("RecoverGeometryColumn", 5, lambda *a: 1)
            dbapi_conn.create_function("CreateSpatialIndex", 2, lambda *a: 1)
            dbapi_conn.create_function("DiscardGeometryColumn", 2, lambda *a: 1)
            dbapi_conn.create_function("CheckSpatialIndex", 2, lambda *a: 1)
            dbapi_conn.create_function("DisableSpatialIndex", 2, lambda *a: 1)
else:
    engine = create_engine(TEST_DB_URL, pool_pre_ping=True)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.main import app
from app.api.deps import get_db, get_current_active_user
from app.models.base import Base
from app.models.user import User, Role


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    if not IS_SQLITE:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    for role_name, role_id in [
        ("ADMIN", "00000000-0000-0000-0000-000000000000"),
        ("OFFICER", "00000000-0000-0000-0000-000000000003"),
        ("EXECUTIVE", "00000000-0000-0000-0000-000000000004"),
    ]:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            db.add(Role(id=uuid.UUID(role_id), name=role_name, description=f"{role_name} role"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def normal_user(db):
    user = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        badge_number="TEST1234",
        email="test@example.com",
        is_active=True
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def admin_user(db):
    user = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        badge_number="ADMIN123",
        email="admin@example.com",
        is_active=True,
        role_id=uuid.UUID("00000000-0000-0000-0000-000000000000")
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def auth_client(client, normal_user):
    def override_get_current_active_user():
        return normal_user

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    yield client
    app.dependency_overrides.pop(get_current_active_user, None)


@pytest.fixture
def admin_client(client, admin_user):
    def override_get_current_active_user():
        return admin_user

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    yield client
    app.dependency_overrides.pop(get_current_active_user, None)
