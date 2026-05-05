import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import UserDB


# =============== REGISTER ===============

def test_singup(client):
    response = client.post(
        "/users/singup", 
        json={
            "username": "string",
            "password": "string",
            "name": "string",
            "email": "string@string.com"
        }
    )
    assert response.status_code == 201


def test_singup_already_pickup_username(client, test_user):
    user, token = test_user
    response = client.post(
        "/users/singup",
        json={
            "username": user.username,
            "password": "user",
            "name": "Name",
            "email": "asd@asd.com"
        }
    )
    assert response.status_code == 409

def test_singup_already_pickup_email(client, test_user):
    user, token = test_user
    response = client.post(
        "/users/singup",
        json={
            "username": "nachos",
            "password": "user",
            "name": "Name",
            "email": user.email
        }
    )
    assert response.status_code == 400


def test_singup_bad_request(client):
    response = client.post(
        "/users/singup", 
        json={
            "username": "string",
            "cacahuetes": "assembly",
            "wayland": "lechuga",
            "name": "string",
            "email": "string@string.com"
        }
    )
    assert response.status_code == 422

# =============== LOGIN ===============

def test_login(admin_user, client):
    user, token = admin_user
    response = client.post(
        "/users/login", 
        data={
            "username": user.username,
            "password": "adm2026"
        }
    )
    data = response.json()
    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_credentials(client):
    response = client.post(
        "/users/login", 
        data={
            "username": "keyboard",
            "password": "almendras_pistachos_y_cacahuetes"
        }
    )
    assert response.status_code == 401


def test_login_bad_request(client):
    response = client.post(
        "/users/login", 
        data={
            "password": "almendras_pistachos_y_cacahuetes",
            "status": "3735928559",
            "ttl": "64"
        }
    )
    assert response.status_code == 422

# =============== READ USERS ===============

def test_read_all_users(admin_user, client):
    user, token = admin_user
    response = client.get("/users/", headers={"Authorization": f"Bearer {token.access_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_all_users_unauthorized(client):
    response = client.get("/users/")
    assert response.status_code == 401

# =============== READ USER ===============

def test_read_user(admin_user, client):
    user, token = admin_user
    response = client.get(f"/users/{user.id}", headers={"Authorization": f"Bearer {token.access_token}"})
    assert response.status_code == 200


def test_read_user_unauthorized(client):
    response = client.get("/users/57005")#HEX
    assert response.status_code == 401


def test_read_user_dosent_exists(admin_user, client):
    user, token = admin_user

    response = client.get("/users/2026", headers={"Authorization": f"Bearer {token.access_token}"})
    assert response.status_code == 404

# =============== DELETE USER ===============

def test_delete_user(session, admin_user, test_user, client):
    admin, token_admin = admin_user
    user, token_user = test_user

    response = client.delete(f"/users/{user.id}", headers={"Authorization": f"Bearer {token_admin.access_token}"})

    user_in_db = session.get(UserDB, user.id)

    assert user_in_db is None
    assert response.status_code == 200


def test_delete_user_unauthorized(client):
    response = client.delete(f"/users/47")

    assert response.status_code == 401

# =============== USER CARDS ===============

def test_read_user_cards(session, test_user_with_cards, client):
    user, token = test_user_with_cards
    response = client.get(f"/users/{user.id}/inventory?expansion=1", headers={"Authorization": f"Bearer {token.access_token}"})

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 3

def test_read_user_cards_admin(admin_user, test_user_with_cards, client):
    user, token = test_user_with_cards
    admin, token_admin = admin_user

    response = client.get(f"/users/{user.id}/inventory?expansion=1", headers={"Authorization": f"Bearer {token_admin.access_token}"})
    
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 3


def test_read_other_user_card(admin_user, test_user_with_cards, client):
    user, token_user = test_user_with_cards
    admin, token_admin = admin_user

    response = client.get(f"/users/{admin.id}/inventory?expansion=1", headers={"Authorization": f"Bearer {token_user.access_token}"})
    
    data = response.json()

    assert response.status_code == 403
