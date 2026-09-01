import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db, get_current_active_user, RoleChecker
from app.models.base import Base
from app.models.user import User

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    from app.models.user import Role
    import uuid
    admin_role = Role(id=uuid.UUID("00000000-0000-0000-0000-000000000000"), name="ADMIN", description="Admin role")
    db.add(admin_role)
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
    del app.dependency_overrides[get_db]

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
    del app.dependency_overrides[get_current_active_user]

@pytest.fixture
def admin_client(client, admin_user):
    def override_get_current_active_user():
        return admin_user

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    yield client
    del app.dependency_overrides[get_current_active_user]
