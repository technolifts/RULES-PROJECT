import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User

def test_create_user(db):
    # Create a test user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Retrieve the user
    db_user = db.query(User).filter(User.username == "testuser").first()
    
    # Check if user was created correctly
    assert db_user is not None
    assert db_user.email == "test@example.com"
    assert db_user.username == "testuser"
    assert db_user.is_active == True

def test_password_hashing():
    password = "securepassword123"
    hashed = User.get_password_hash(password)
    
    # Check that the hash is not the original password
    assert hashed != password
    
    # Check that verification works
    assert User.verify_password(password, hashed) == True
    assert User.verify_password("wrongpassword", hashed) == False

def test_unique_email_constraint(db):
    # Create first user
    user1 = User(
        email="duplicate@example.com",
        username="user1",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user1)
    db.commit()
    
    # Try to create second user with same email
    user2 = User(
        email="duplicate@example.com",
        username="user2",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user2)
    
    # Should raise an integrity error
    with pytest.raises(IntegrityError):
        db.commit()
    
    # Rollback the failed transaction
    db.rollback()

def test_unique_username_constraint(db):
    # Create first user
    user1 = User(
        email="user1@example.com",
        username="duplicate",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user1)
    db.commit()
    
    # Try to create second user with same username
    user2 = User(
        email="user2@example.com",
        username="duplicate",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user2)
    
    # Should raise an integrity error
    with pytest.raises(IntegrityError):
        db.commit()
    
    # Rollback the failed transaction
    db.rollback()
