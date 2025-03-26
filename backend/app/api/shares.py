from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.models.share import ShareLink
from app.schemas.share import ShareLink as ShareLinkSchema, ShareLinkCreate, SharedDocumentInfo
from app.utils.auth import get_current_active_user
from app.utils.share import generate_share_token, get_default_expiry
from app.utils.file import get_file_content

router = APIRouter(tags=["shares"])

@router.post("/shares/", response_model=ShareLinkSchema)
def create_share_link(
    share: ShareLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new share link for a document"""
    # Check if document exists and belongs to the user
    document = db.query(Document).filter(Document.id == share.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to share this document")
    
    # Generate a unique token
    token = generate_share_token()
    
    # Set expiry date if not provided
    expires_at = share.expires_at or get_default_expiry()
    
    # Create share link
    db_share = ShareLink(
        token=token,
        document_id=share.document_id,
        created_by=current_user.id,
        expires_at=expires_at
    )
    
    db.add(db_share)
    db.commit()
    db.refresh(db_share)
    
    return db_share

@router.get("/shares/", response_model=List[ShareLinkSchema])
def get_user_share_links(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all share links created by the current user"""
    shares = db.query(ShareLink).filter(
        ShareLink.created_by == current_user.id,
        ShareLink.is_active == True
    ).all()
    
    return shares

@router.delete("/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_share_link(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete (deactivate) a share link"""
    share = db.query(ShareLink).filter(ShareLink.id == share_id).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")
    
    if share.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this share link")
    
    # Deactivate the share link instead of deleting it
    share.is_active = False
    db.commit()
    
    return None

@router.get("/public/documents/{token}", response_model=SharedDocumentInfo)
def get_shared_document_info(token: str, db: Session = Depends(get_db)):
    """Get information about a shared document without authentication"""
    share = db.query(ShareLink).filter(
        ShareLink.token == token,
        ShareLink.is_active == True
    ).first()
    
    if not share or share.is_expired:
        raise HTTPException(status_code=404, detail="Share link not found or expired")
    
    document = share.document
    shared_by = db.query(User).filter(User.id == share.created_by).first()
    
    return {
        "id": document.id,
        "original_filename": document.original_filename,
        "content_type": document.content_type,
        "description": document.description,
        "shared_by": shared_by.username,
        "created_at": document.created_at
    }

@router.get("/public/documents/{token}/download")
def download_shared_document(token: str, db: Session = Depends(get_db)):
    """Download a shared document without authentication"""
    share = db.query(ShareLink).filter(
        ShareLink.token == token,
        ShareLink.is_active == True
    ).first()
    
    if not share or share.is_expired:
        raise HTTPException(status_code=404, detail="Share link not found or expired")
    
    document = share.document
    
    # Get file content and return as a response
    return get_file_content(document.file_path, document.original_filename, document.content_type)
