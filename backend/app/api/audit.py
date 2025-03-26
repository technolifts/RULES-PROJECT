from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLog as AuditLogSchema
from app.utils.auth import get_current_active_user
from app.models.user import User
from app.utils.audit import get_client_ip, create_audit_log
from datetime import datetime, timedelta

router = APIRouter(tags=["audit"])


@router.get("/audit-logs/", response_model=List[AuditLogSchema])
async def get_audit_logs(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get audit logs with optional filtering.
    Only administrators should have access to all logs.
    Regular users can only see their own logs.
    """
    # Check if user is admin (you may need to implement this check)
    is_admin = getattr(current_user, "is_admin", False)
    
    # Build query
    query = db.query(AuditLog)
    
    # If not admin, restrict to user's own logs
    if not is_admin:
        query = query.filter(AuditLog.user_id == current_user.id)
    
    # Apply filters
    if user_id and is_admin:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if resource_id:
        query = query.filter(AuditLog.resource_id == resource_id)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    # Order by timestamp descending (newest first)
    query = query.order_by(AuditLog.timestamp.desc())
    
    # Paginate results
    logs = query.offset(skip).limit(limit).all()
    
    # Log this audit log request
    create_audit_log(
        db=db,
        action="read",
        resource_type="audit_log",
        details=f"Retrieved {len(logs)} audit logs",
        user_id=current_user.id,
        ip_address=await get_client_ip(request)
    )
    
    # Add username to each log
    result = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp,
            "username": log.user.username if log.user else None
        }
        result.append(log_dict)
    
    return result
