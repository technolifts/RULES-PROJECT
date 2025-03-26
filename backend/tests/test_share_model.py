import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.document import Document
from app.models.share import ShareLink
from app.utils.share import generate_share_token

def test_create_share_link(db):
    # Create a test user
    user = User(
        email="shareuser@example.com",
        username="shareuser",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="share-test.pdf",
        original_filename="share-original.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/share-test.pdf",
        description="Share test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create a share link
    token = generate_share_token()
    expires_at = datetime.now() + timedelta(days=7)
    
    share_link = ShareLink(
        token=token,
        document_id=document.id,
        created_by=user.id,
        expires_at=expires_at
    )
    db.add(share_link)
    db.commit()
    
    # Retrieve the share link
    db_share = db.query(ShareLink).filter(ShareLink.token == token).first()
    
    # Check if share link was created correctly
    assert db_share is not None
    assert db_share.document_id == document.id
    assert db_share.created_by == user.id
    assert db_share.is_active == True
    assert db_share.is_expired == False

def test_share_link_relationships(db):
    # Create a test user
    user = User(
        email="relationshare@example.com",
        username="relationshare",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="relation-test.pdf",
        original_filename="relation-original.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/relation-test.pdf",
        description="Relation test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create a share link
    token = generate_share_token()
    
    share_link = ShareLink(
        token=token,
        document_id=document.id,
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=7)
    )
    db.add(share_link)
    db.commit()
    
    # Test relationships
    db_share = db.query(ShareLink).filter(ShareLink.token == token).first()
    
    # Check document relationship
    assert db_share.document.id == document.id
    assert db_share.document.original_filename == "relation-original.pdf"
    
    # Check user relationship
    assert db_share.user.id == user.id
    assert db_share.user.username == "relationshare"
    
    # Check from document side
    db_document = db.query(Document).filter(Document.id == document.id).first()
    assert len(db_document.share_links) == 1
    assert db_document.share_links[0].token == token

def test_share_link_expiry(db):
    # Create a test user
    user = User(
        email="expiryuser@example.com",
        username="expiryuser",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="expiry-test.pdf",
        original_filename="expiry-original.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/expiry-test.pdf",
        description="Expiry test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create an expired share link
    expired_token = generate_share_token()
    expired_share = ShareLink(
        token=expired_token,
        document_id=document.id,
        created_by=user.id,
        expires_at=datetime.now() - timedelta(days=1)  # Expired 1 day ago
    )
    db.add(expired_share)
    
    # Create a valid share link
    valid_token = generate_share_token()
    valid_share = ShareLink(
        token=valid_token,
        document_id=document.id,
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=1)  # Valid for 1 more day
    )
    db.add(valid_share)
    
    db.commit()
    
    # Test expiry
    expired = db.query(ShareLink).filter(ShareLink.token == expired_token).first()
    valid = db.query(ShareLink).filter(ShareLink.token == valid_token).first()
    
    assert expired.is_expired == True
    assert valid.is_expired == False

def test_cascade_delete_document(db):
    # Create a test user
    user = User(
        email="cascadeshare@example.com",
        username="cascadeshare",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Create a test document
    document = Document(
        filename="cascade-share-test.pdf",
        original_filename="cascade-share-original.pdf",
        content_type="application/pdf",
        file_size=1024,
        file_path="/tmp/cascade-share-test.pdf",
        description="Cascade share test document",
        user_id=user.id
    )
    db.add(document)
    db.commit()
    
    # Create a share link
    token = generate_share_token()
    share_link = ShareLink(
        token=token,
        document_id=document.id,
        created_by=user.id,
        expires_at=datetime.now() + timedelta(days=7)
    )
    db.add(share_link)
    db.commit()
    
    # Verify share link exists
    share_count = db.query(ShareLink).filter(ShareLink.token == token).count()
    assert share_count == 1
    
    # Delete the document
    db.delete(document)
    db.commit()
    
    # Check that share link was also deleted (cascade)
    share_count = db.query(ShareLink).filter(ShareLink.token == token).count()
    assert share_count == 0
