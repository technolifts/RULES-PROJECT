from fastapi import APIRouter, Depends, HTTPException, status, Request
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
from app.utils.audit import log_activity

router = APIRouter(tags=["shares"])

@router.post("/shares/", response_model=ShareLinkSchema)
async def create_share_link(
    share: ShareLinkCreate,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new share link for a document"""
    # Check if document exists and belongs to the user
    document = db.query(Document).filter(Document.id == share.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.user_id != current_user.id:
        # Log unauthorized share attempt
        await log_activity(
            db=db,
            action="unauthorized_share",
            resource_type="document",
            user_id=current_user.id,
            resource_id=str(share.document_id),
            details={"document_owner": document.user_id if document else None},
            request=request
        )
        
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
    
    # Log share creation
    await log_activity(
        db=db,
        action="create",
        resource_type="share",
        user_id=current_user.id,
        resource_id=str(db_share.id),
        details={
            "document_id": share.document_id,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "token": token[:8] + "..." # Only log part of the token for security
        },
        request=request
    )
    
    return db_share

@router.get("/shares/", response_model=List[ShareLinkSchema])
async def get_user_share_links(
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all share links created by the current user"""
    shares = db.query(ShareLink).filter(
        ShareLink.created_by == current_user.id,
        ShareLink.is_active == True
    ).all()
    
    # Log share list access
    await log_activity(
        db=db,
        action="list",
        resource_type="share",
        user_id=current_user.id,
        details={"count": len(shares)},
        request=request
    )
    
    return shares

@router.delete("/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_share_link(
    share_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete (deactivate) a share link"""
    share = db.query(ShareLink).filter(ShareLink.id == share_id).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")
    
    if share.created_by != current_user.id:
        # Log unauthorized delete attempt
        await log_activity(
            db=db,
            action="unauthorized_delete",
            resource_type="share",
            user_id=current_user.id,
            resource_id=str(share_id),
            details={"share_owner": share.created_by},
            request=request
        )
        
        raise HTTPException(status_code=403, detail="Not authorized to delete this share link")
    
    # Store share info for logging
    share_info = {
        "document_id": share.document_id,
        "token": share.token[:8] + "..." # Only log part of the token for security
    }
    
    # Deactivate the share link instead of deleting it
    share.is_active = False
    db.commit()
    
    # Log share deletion
    await log_activity(
        db=db,
        action="delete",
        resource_type="share",
        user_id=current_user.id,
        resource_id=str(share_id),
        details=share_info,
        request=request
    )
    
    return None

@router.get("/public/documents/{token}", response_model=SharedDocumentInfo)
async def get_shared_document_info(token: str, request: Request = None, db: Session = Depends(get_db)):
    """Get information about a shared document without authentication"""
    share = db.query(ShareLink).filter(
        ShareLink.token == token,
        ShareLink.is_active == True
    ).first()
    
    if not share or share.is_expired:
        # Log invalid or expired share access attempt
        await log_activity(
            db=db,
            action="invalid_share_access",
            resource_type="share",
            resource_id=token[:8] + "...",
            details={"reason": "not found or expired"},
            request=request
        )
        
        raise HTTPException(status_code=404, detail="Share link not found or expired")
    
    document = share.document
    shared_by = db.query(User).filter(User.id == share.created_by).first()
    
    # Log successful share access
    await log_activity(
        db=db,
        action="access",
        resource_type="share",
        user_id=share.created_by,
        resource_id=str(share.id),
        details={
            "document_id": document.id,
            "document_name": document.original_filename
        },
        request=request
    )
    
    return {
        "id": document.id,
        "original_filename": document.original_filename,
        "content_type": document.content_type,
        "description": document.description,
        "shared_by": shared_by.username,
        "created_at": document.created_at
    }

@router.get("/public/documents/{token}/download")
async def download_shared_document(token: str, request: Request = None, db: Session = Depends(get_db)):
    """Download a shared document without authentication"""
    share = db.query(ShareLink).filter(
        ShareLink.token == token,
        ShareLink.is_active == True
    ).first()
    
    if not share or share.is_expired:
        # Log invalid or expired share download attempt
        await log_activity(
            db=db,
            action="invalid_share_download",
            resource_type="share",
            resource_id=token[:8] + "...",
            details={"reason": "not found or expired"},
            request=request
        )
        
        raise HTTPException(status_code=404, detail="Share link not found or expired")
    
    document = share.document
    
    # Log successful share download
    await log_activity(
        db=db,
        action="download",
        resource_type="share",
        user_id=share.created_by,
        resource_id=str(share.id),
        details={
            "document_id": document.id,
            "document_name": document.original_filename
        },
        request=request
    )
    
    # Get file content and return as a response
    return get_file_content(document.file_path, document.original_filename, document.content_type)
