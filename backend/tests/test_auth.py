from fastapi.testclient import TestClient
from app.models.user import User

def test_register_user(client, db):
    response = client.post(
        "/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "Password123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    
    # Check that the user was actually created in the database
    db_user = db.query(User).filter(User.username == "newuser").first()
    assert db_user is not None
    assert db_user.email == "newuser@example.com"

def test_register_duplicate_email(client, db):
    # Create a user first
    user = User(
        email="existing@example.com",
        username="existinguser",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Try to register with the same email
    response = client.post(
        "/register",
        json={
            "email": "existing@example.com",
            "username": "newuser",
            "password": "Password123!"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_duplicate_username(client, db):
    # Create a user first
    user = User(
        email="user1@example.com",
        username="existinguser",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Try to register with the same username
    response = client.post(
        "/register",
        json={
            "email": "user2@example.com",
            "username": "existinguser",
            "password": "Password123!"
        }
    )
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]

def test_login(client, db):
    # Create a user
    hashed_password = User.get_password_hash("Password123!")
    user = User(
        email="logintest@example.com",
        username="loginuser",
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    
    # Login with correct credentials
    response = client.post(
        "/token",
        data={
            "username": "loginuser",
            "password": "Password123!"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, db):
    # Create a user
    hashed_password = User.get_password_hash("Password123!")
    user = User(
        email="wrongpass@example.com",
        username="wrongpassuser",
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    
    # Try to login with wrong password
    response = client.post(
        "/token",
        data={
            "username": "wrongpassuser",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_get_current_user(client, db):
    # Create a user
    hashed_password = User.get_password_hash("Password123!")
    user = User(
        email="currentuser@example.com",
        username="currentuser",
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    
    # Login to get token
    response = client.post(
        "/token",
        data={
            "username": "currentuser",
            "password": "Password123!"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = response.json()["access_token"]
    
    # Get current user with token
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "currentuser@example.com"

def test_get_current_user_invalid_token(client):
    # Try to get current user with invalid token
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]
