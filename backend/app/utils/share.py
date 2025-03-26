import secrets
import string
from datetime import datetime, timedelta

def generate_share_token(length=32):
    """Generate a secure random token for share links"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_default_expiry():
    """Get default expiry time (7 days from now)"""
    return datetime.now() + timedelta(days=7)
