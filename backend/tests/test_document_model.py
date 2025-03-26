import pytest
from app.models.user import User
from app.models.document import Document

def test_create_document(db):
    # Create a test user first
    user = User(
        email="docuser@example.com",
        username="docuser",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="test-file.pdf",
        original_filename="original-file.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/test-file.pdf",
        description="Test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Retrieve the document
    db_document = db.query(Document).filter(Document.filename == "test-file.pdf").first()
    
    # Check if document was created correctly
    assert db_document is not None
    assert db_document.original_filename == "original-file.pdf"
    assert db_document.content_type == "application/pdf"
    assert db_document.file_size == 1024
    assert db_document.description == "Test document"
    assert db_document.user_id == user.id

def test_user_document_relationship(db):
    # Create a test user
    user = User(
        email="relationuser@example.com",
        username="relationuser",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Create multiple documents for the user
    for i in range(3):
        document = Document(
            filename=f"test-file-{i}.pdf",
            original_filename=f"original-file-{i}.pdf",
            content_type="application/pdf",
            file_size=1024,
            file_path=f"/tmp/test-file-{i}.pdf",
            description=f"Test document {i}",
            user_id=user.id
        )
        db.add(document)
    
    db.commit()
    
    # Retrieve the user with documents
    db_user = db.query(User).filter(User.username == "relationuser").first()
    
    # Check if the relationship works
    assert len(db_user.documents) == 3
    assert db_user.documents[0].filename.startswith("test-file-")
    
    # Check if the document has a reference to the user
    document = db.query(Document).filter(Document.filename == "test-file-0.pdf").first()
    assert document.user.username == "relationuser"

def test_cascade_delete(db):
    # Create a test user
    user = User(
        email="cascadeuser@example.com",
        username="cascadeuser",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Create documents for the user
    for i in range(2):
        document = Document(
            filename=f"cascade-file-{i}.pdf",
            original_filename=f"original-cascade-{i}.pdf",
            content_type="application/pdf",
            file_size=1024,
            file_path=f"/tmp/cascade-file-{i}.pdf",
            description=f"Cascade test document {i}",
            user_id=user.id
        )
        db.add(document)
    
    db.commit()
    
    # Verify documents exist
    doc_count = db.query(Document).filter(Document.user_id == user.id).count()
    assert doc_count == 2
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    # Check that documents were also deleted (cascade)
    doc_count = db.query(Document).filter(Document.filename.like("cascade-file-%")).count()
    assert doc_count == 0
