import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import create_database_and_tables

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    create_database_and_tables()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
