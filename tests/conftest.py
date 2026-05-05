import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.auth.auth import get_hash_password, create_access_token
from app.db.database import UserDB, CardDB, UserCardDB, get_session
from app.main import app
from random import choice, randint
from string import ascii_letters

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(session: Session):
    admin: UserDB = UserDB(
        name = "Administrator",
        username = "Admin",
        password = get_hash_password("adm2026"),
        email = "admin@admin.com",
        money = 9999999,
        is_admin = True
    )

    session.add(admin)
    session.commit()

    return admin, create_access_token(admin)


@pytest.fixture
def test_user(session: Session):
    user: UserDB = UserDB(
        name = "User",
        username = ''.join(choice(ascii_letters) for _ in range(6)),
        password = get_hash_password("user"),
        email = f"{''.join(choice(ascii_letters) for _ in range(6))}@asd.com",
        money = 0,
        is_admin = True
    )

    session.add(user)
    session.commit()

    return user, create_access_token(user)


@pytest.fixture
def test_user_with_cards(session: Session, test_user):
    user, token = test_user

    cards: CardDB = [CardDB(id_expansion=1, name="MISSINGNO", rarity="", price=1, card_number=randint(0,251), frontcard="", backcard="") for _ in range(3)]
    [session.add(card) for card in cards]
    session.commit()

    [session.add(UserCardDB(id_card=card.id, id_user=user.id, price=2)) for card in cards]
    session.commit()

    return user, token
