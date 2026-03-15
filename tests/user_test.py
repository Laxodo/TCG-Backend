import pytest
from fastapi.testclient import TestClient
from app.main import app


USER_DATA = {
    "username": "test user",
    "password": "test_user_password",
    "name": "Test user",
    "email": "test@example.com"
}

LOGIN_USER_DATA = {
    "username": USER_DATA["username"],
    "password": USER_DATA["password"]
}

# =============== REGISTER ===============

def test_singup(client):
    response = client.post("/users/singup", json=USER_DATA)
    assert response.status_code == 201


def test_singup_already_exists(client):
    response = client.post("/users/singup", json=USER_DATA)
    assert response.status_code == 409

# =============== LOGIN ===============

def test_login(client):
    response = client.post("/users/login", data=LOGIN_USER_DATA)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_incorrect(client):
    response = client.post("/users/login", data={
        "username": USER_DATA["username"],
        "password": "almendras_pistachos_y_cacahuetes"
    })
    assert response.status_code == 401

# =============== READ USERS ===============

def test_read_all_users_unauthorized(client):
    response = client.get("/users/")
    assert response.status_code == 401


def test_read_all_users(client):
    login_response = client.post("/users/login", data=USER_DATA)
    token = login_response.json()["access_token"]
    
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# =============== READ USER ===============

def test_read_user_unauthorized(client):
    response = client.get("/users/1")
    assert response.status_code == 401


def test_read_user(client):
    login_response = client.post("/users/login", data=USER_DATA)
    token = login_response.json()["access_token"]
    
    response = client.get("/users/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

# =============== DELETE USER ===============

def test_delete_user_unauthorized(client):
    response = client.delete("/users/1")
    assert response.status_code == 401


def test_delete_user(client):
    login_response = client.post("/users/login", data=USER_DATA)
    token = login_response.json()["access_token"]
    
    response = client.delete("/users/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
