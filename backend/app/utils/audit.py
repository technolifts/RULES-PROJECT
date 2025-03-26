from fastapi import Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit import AuditLog
from typing import Optional, Dict, Any, Union
import json


async def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"]
    elif hasattr(request, "client") and request.client.host:
        return request.client.host
    return "unknown"


def create_audit_log(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Union[str, Dict[str, Any]]] = None,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
):
    """Create an audit log entry in the database"""
    # Convert dict details to JSON string
    if isinstance(details, dict):
        details = json.dumps(details)
        
    audit_log = AuditLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        user_id=user_id,
        ip_address=ip_address,
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


async def log_activity(
    db: Session,
    action: str,
    resource_type: str,
    user_id: Optional[int] = None,
    resource_id: Optional[str] = None,
    details: Optional[Union[str, Dict[str, Any]]] = None,
    request: Optional[Request] = None,
):
    """Helper function to log user activity with request info"""
    ip_address = None
    if request:
        ip_address = await get_client_ip(request)
    
    return create_audit_log(
        db=db,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        user_id=user_id,
        ip_address=ip_address
    )


class AuditMiddleware:
    """Middleware to log API requests"""
    
    async def __call__(self, request: Request, call_next):
        # Process the request and get the response
        response = await call_next(request)
        
        # Don't log static files or health checks
        if request.url.path.startswith(("/static/", "/docs", "/redoc", "/openapi.json", "/favicon.ico")):
            return response
            
        # We'll add the actual audit logging in the endpoints
        # This middleware is mainly for setup and could be expanded
        # to log all requests if needed
        
        return response
