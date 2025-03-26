from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import Document as DocumentSchema, DocumentCreate
from app.utils.auth import get_current_active_user
from app.utils.file import validate_file, get_secure_filename, save_file, delete_file

router = APIRouter(tags=["documents"])

@router.post("/documents/", response_model=DocumentSchema)
async def create_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a new document"""
    # Validate file
    validate_file(file)
    
    # Generate secure filename
    secure_filename = get_secure_filename(file.filename)
    
    # Save file to disk
    file_path, file_size = save_file(file, secure_filename)
    
    # Create document record in database
    db_document = Document(
        filename=secure_filename,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=file_size,
        file_path=file_path,
        description=description,
        user_id=current_user.id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.get("/documents/", response_model=List[DocumentSchema])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all documents for the current user"""
    documents = db.query(Document).filter(Document.user_id == current_user.id).offset(skip).limit(limit).all()
    return documents

@router.get("/documents/{document_id}", response_model=DocumentSchema)
def read_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has access to this document
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    return document

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has access to this document
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")
    
    # Delete the file from disk
    delete_file(document.file_path)
    
    # Delete the document record
    db.delete(document)
    db.commit()
    
    return None
