import pytest
from app.models.user import User
from app.models.audit import AuditLog

def test_create_audit_log(db):
    # Create a test user first
    user = User(
        email="audituser@example.com",
        username="audituser",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Create a test audit log
    audit_log = AuditLog(
        user_id=user.id,
        action="test_action",
        resource_type="test_resource",
        resource_id="123",
        details={"test_key": "test_value"},
        ip_address="127.0.0.1",
        user_agent="Test User Agent"
    )
    db.add(audit_log)
    db.commit()
    
    # Retrieve the audit log
    db_audit_log = db.query(AuditLog).filter(AuditLog.action == "test_action").first()
    
    # Check if audit log was created correctly
    assert db_audit_log is not None
    assert db_audit_log.user_id == user.id
    assert db_audit_log.resource_type == "test_resource"
    assert db_audit_log.resource_id == "123"
    assert db_audit_log.details == {"test_key": "test_value"}
    assert db_audit_log.ip_address == "127.0.0.1"
    assert db_audit_log.user_agent == "Test User Agent"

def test_user_audit_log_relationship(db):
    # Create a test user
    user = User(
        email="auditrelation@example.com",
        username="auditrelation",
        hashed_password=User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    
    # Create multiple audit logs for the user
    for i in range(3):
        audit_log = AuditLog(
            user_id=user.id,
            action=f"test_action_{i}",
            resource_type="test_resource",
            resource_id=str(i),
            details={"test_key": f"test_value_{i}"}
        )
        db.add(audit_log)
    
    db.commit()
    
    # Retrieve the user with audit logs
    db_user = db.query(User).filter(User.username == "auditrelation").first()
    
    # Check if the relationship works
    assert len(db_user.audit_logs) == 3
    assert db_user.audit_logs[0].action.startswith("test_action_")
    
    # Check if the audit log has a reference to the user
    audit_log = db.query(AuditLog).filter(AuditLog.action == "test_action_0").first()
    assert audit_log.user.username == "auditrelation"

def test_audit_log_without_user(db):
    # Create an audit log without a user (for anonymous actions)
    audit_log = AuditLog(
        action="anonymous_action",
        resource_type="test_resource",
        resource_id="456",
        details={"anonymous": True},
        ip_address="192.168.1.1"
    )
    db.add(audit_log)
    db.commit()
    
    # Retrieve the audit log
    db_audit_log = db.query(AuditLog).filter(AuditLog.action == "anonymous_action").first()
    
    # Check if audit log was created correctly
    assert db_audit_log is not None
    assert db_audit_log.user_id is None
    assert db_audit_log.resource_type == "test_resource"
    assert db_audit_log.resource_id == "456"
    assert db_audit_log.details == {"anonymous": True}
    assert db_audit_log.ip_address == "192.168.1.1"
    assert db_audit_log.user is None
