import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.audit import AuditLog
from app.utils.auth import create_access_token

def test_get_audit_logs(client, db):
    # Create a test user
    user = User(
        email="auditapi@example.com",
        username="auditapi",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(user)
    db.commit()
    
    # Create some audit logs for the user
    for i in range(3):
        audit_log = AuditLog(
            user_id=user.id,
            action=f"test_action_{i}",
            resource_type="test_resource",
            resource_id=str(i),
            details={"test_key": f"test_value_{i}"}
        )
        db.add(audit_log)
    
    # Create an audit log for another user
    other_user = User(
        email="otheraudit@example.com",
        username="otheraudit",
        hashed_password=User.get_password_hash("Password123!")
    )
    db.add(other_user)
    db.commit()
    
    other_audit_log = AuditLog(
        user_id=other_user.id,
        action="other_action",
        resource_type="test_resource",
        resource_id="999",
        details={"other": True}
    )
    db.add(other_audit_log)
    db.commit()
    
    # Create access token for the first user
    access_token = create_access_token(data={"sub": user.username})
    
    # Get the audit logs
    response = client.get(
        "/audit-logs/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # User should only see their own logs
    assert len(data) == 3
    assert all(log["user_id"] == user.id for log in data)
    assert all(log["username"] == user.username for log in data)
    
    # Test filtering by action
    response = client.get(
        "/audit-logs/?action=test_action_1",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["action"] == "test_action_1"
    
    # Test filtering by resource type
    response = client.get(
        "/audit-logs/?resource_type=test_resource",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(log["resource_type"] == "test_resource" for log in data)

def test_audit_logs_unauthorized(client):
    # Try to get audit logs without authentication
    response = client.get("/audit-logs/")
    
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
