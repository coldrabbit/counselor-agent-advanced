import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.main import create_app

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine):
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session, engine):
    # Override app.db.database.SessionLocal so MCP tools use the test database
    import app.db.database as db_module
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    original = db_module.SessionLocal
    db_module.SessionLocal = TestSessionLocal

    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    db_module.SessionLocal = original


@pytest.fixture
def counselor_profile(client):
    resp = client.put("/api/counselor/profile", json={
        "name": "张伟",
        "college": "计算机学院",
        "phone": "13800138000",
        "email": "zhangwei@university.edu.cn",
    })
    return resp.json()
