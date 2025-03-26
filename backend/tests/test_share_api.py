import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.document import Document
from app.models.share import ShareLink
from app.utils.auth import create_access_token
from datetime import datetime, timedelta

def test_create_share_link(client, db):
    # Create a test user
    user = User(
        email="sharecreator@example.com",
        username="sharecreator",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="share-api-test.pdf",
        original_filename="share-api-original.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/share-api-test.pdf",
        description="Share API test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create access token for the user
    access_token = create_access_token(data={"sub": user.username})
    
    # Create a share link
    response = client.post(
        "/shares/",
        json={
            "document_id": document.id,
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == document.id
    assert data["created_by"] == user.id
    assert "token" in data
    assert data["is_active"] == True

def test_get_user_share_links(client, db):
    # Create a test user
    user = User(
        email="sharegetter@example.com",
        username="sharegetter",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="share-get-test.pdf",
        original_filename="share-get-original.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/share-get-test.pdf",
        description="Share get test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create some share links
    for i in range(3):
        share = ShareLink(
            token=f"test-token-{i}",
            document_id=document.id,
            created_by=user.id,
            expires_at=datetime.now() + timedelta(days=7)
        )
        db.add(share)
    
    db.commit()
    
    # Create access token for the user
    access_token = create_access_token(data={"sub": user.username})
    
    # Get the share links
    response = client.get(
        "/shares/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["token"].startswith("test-token-")

def test_delete_share_link(client, db):
    # Create a test user
    user = User(
        email="sharedeleter@example.com",
        username="sharedeleter",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="share-delete-test.pdf",
        original_filename="share-delete-original.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/share-delete-test.pdf",
        description="Share delete test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create a share link
    share = ShareLink(
        token="delete-test-token",
        document_id=document.id,
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=7)
    )
    db.add(share)
    db.commit()
    
    # Create access token for the user
    access_token = create_access_token(data={"sub": user.username})
    
    # Delete the share link
    response = client.delete(
        f"/shares/{share.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 204
    
    # Verify share link was deactivated
    db_share = db.query(ShareLink).filter(ShareLink.id == share.id).first()
    assert db_share is not None  # Still exists
    assert db_share.is_active == False  # But is deactivated

def test_get_shared_document_info(client, db):
    # Create a test user
    user = User(
        email="publicshare@example.com",
        username="publicshare",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="public-share-test.pdf",
        original_filename="public-share-original.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/public-share-test.pdf",
        description="Public share test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create a share link
    share = ShareLink(
        token="public-test-token",
        document_id=document.id,
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=7)
    )
    db.add(share)
    db.commit()
    
    # Get the shared document info
    response = client.get(f"/public/documents/public-test-token")
    
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "public-share-original.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["description"] == "Public share test document"
    assert data["shared_by"] == "publicshare"

def test_get_expired_shared_document(client, db):
    # Create a test user
    user = User(
        email="expiredshare@example.com",
        username="expiredshare",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="expired-share-test.pdf",
        original_filename="expired-share-original.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/expired-share-test.pdf",
        description="Expired share test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create an expired share link
    share = ShareLink(
        token="expired-test-token",
        document_id=document.id,
        created_by=user.id,
        expires_at=datetime.now() - timedelta(days=1)  # Expired 1 day ago
    )
    db.add(share)
    db.commit()
    
    # Try to get the expired shared document
    response = client.get(f"/public/documents/expired-test-token")
    
    assert response.status_code == 404
    assert "Share link not found or expired" in response.json()["detail"]
