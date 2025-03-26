import os
import uuid
import shutil
from fastapi import UploadFile, HTTPException
from app.config import settings

ALLOWED_CONTENT_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/csv",
    "image/jpeg",
    "image/png",
    "image/gif"
]

def validate_file(file: UploadFile):
    """Validate file size and content type"""
    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )
    
    # We can't check file size directly with UploadFile
    # We'll check it when saving the file

def get_secure_filename(original_filename: str):
    """Generate a secure filename with UUID to prevent path traversal attacks"""
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate a UUID for the filename
    secure_filename = f"{uuid.uuid4()}{ext}"
    
    return secure_filename

def save_file(file: UploadFile, secure_filename: str):
    """Save file to disk with size validation"""
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    file_path = os.path.join(settings.UPLOAD_DIR, secure_filename)
    
    # Save file and check size
    file_size = 0
    with open(file_path, "wb") as buffer:
        # Read and write in chunks to avoid loading large files into memory
        chunk_size = 1024 * 1024  # 1MB chunks
        chunk = file.file.read(chunk_size)
        while chunk:
            file_size += len(chunk)
            
            # Check if file size exceeds limit
            if file_size > settings.MAX_FILE_SIZE:
                # Close and remove the partial file
                buffer.close()
                os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds the {settings.MAX_FILE_SIZE / (1024 * 1024)}MB limit"
                )
            
            buffer.write(chunk)
            chunk = file.file.read(chunk_size)
    
    return file_path, file_size

def delete_file(file_path: str):
    """Delete file from disk"""
    if os.path.exists(file_path):
        os.remove(file_path)
