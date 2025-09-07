# core/session.py
from datetime import datetime, timedelta
from typing import Optional

from Modelo.models import AdminUser

class SessionManager:
    def __init__(self):
        self.current_user: Optional[AdminUser] = None
        self.fernet_key: Optional[bytes] = None
        self.session_start: Optional[datetime] = None
        self.session_timeout: timedelta = timedelta(minutes=30)
        
    def start_session(self, user: AdminUser, fernet_key: bytes):
        self.current_user = user
        self.fernet_key = fernet_key
        self.session_start = datetime.now()
        
    def is_session_valid(self) -> bool:
        if not self.session_start:
            return False
        return datetime.now() - self.session_start < self.session_timeout
        
    def end_session(self):
        self.current_user = None
        self.fernet_key = None
        self.session_start = None