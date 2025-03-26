import io
import os
import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.document import Document
from app.utils.auth import create_access_token

def test_upload_document(client, db, monkeypatch):
    # Create a test user
    user = User(
        email="uploader@example.com",
        username="uploader",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create access token for the user
    access_token = create_access_token(data={"sub": user.username})
    
    # Mock file saving to avoid actual file operations
    def mock_save_file(file, secure_filename):
        return f"/tmp/{secure_filename}", 1024
    
    monkeypatch.setattr("app.api.documents.save_file", mock_save_file)
    
    # Create a test file
    file_content = b"test file content"
    file = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    
    # Upload the document
    response = client.post(
        "/documents/",
        files=file,
        data={"description": "Test document upload"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "test.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["description"] == "Test document upload"
    assert data["user_id"] == user.id

def test_get_documents(client, db):
    # Create a test user
    user = User(
        email="docgetter@example.com",
        username="docgetter",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create some documents for the user
    for i in range(3):
        document = Document(
            filename=f"get-test-{i}.pdf",
            original_filename=f"original-get-{i}.pdf",
            content_type="application/pdf",
            file_size=1024,
            file_path=f"/tmp/get-test-{i}.pdf",
            description=f"Get test document {i}",
            user_id=user.id
        )
        db.add(document)
    
    db.commit()
    
    # Create access token for the user
    access_token = create_access_token(data={"sub": user.username})
    
    # Get the documents
    response = client.get(
        "/documents/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["original_filename"].startswith("original-get-")

def test_get_document_by_id(client, db):
    # Create a test user
    user = User(
        email="singleget@example.com",
        username="singleget",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create a document for the user
    document = Document(
        filename="single-test.pdf",
        original_filename="original-single.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/single-test.pdf",
        description="Single get test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create access token for the user
    access_token = create_access_token(data={"sub": user.username})
    
    # Get the document by ID
    response = client.get(
        f"/documents/{document.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document.id
    assert data["original_filename"] == "original-single.pdf"
    assert data["description"] == "Single get test document"

def test_get_document_unauthorized(client, db):
    # Create two test users
    user1 = User(
        email="owner@example.com",
        username="owner",
        hashed_password=User.get_password_hash("Password123!")
    )
    user2 = User(
        email="unauthorized@example.com",
        username="unauthorized",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user1)
    db.add(user2)
    db.commit()
    
    # Create a document for user1
    document = Document(
        filename="auth-test.pdf",
        original_filename="original-auth.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/auth-test.pdf",
        description="Auth test document",
        user_id=user1.id
    )
    db.add(document)
    db.commit()
    
    # Create access token for user2
    access_token = create_access_token(data={"sub": user2.username})
    
    # Try to get user1's document with user2's token
    response = client.get(
        f"/documents/{document.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 403
    assert "Not authorized to access this document" in response.json()["detail"]

def test_delete_document(client, db, monkeypatch):
    # Create a test user
    user = User(
        email="deleter@example.com",
        username="deleter",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create a document for the user
    document = Document(
        filename="delete-test.pdf",
        original_filename="original-delete.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/delete-test.pdf",
        description="Delete test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Mock file deletion to avoid actual file operations
    def mock_delete_file(file_path):
        pass
    
    monkeypatch.setattr("app.api.documents.delete_file", mock_delete_file)
    
    # Create access token for the user
    access_token = create_access_token(data={"sub": user.username})
    
    # Delete the document
    response = client.delete(
        f"/documents/{document.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 204
    
    # Verify document was deleted from database
    db_document = db.query(Document).filter(Document.id == document.id).first()
    assert db_document is None
