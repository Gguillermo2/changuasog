from typing import List, Optional
from datetime import datetime
from Modelo.models import Account
from core.almacenamiento import save_accounts_data, load_accounts_data
from core.seguridad import generate_strong_password
#Modificaciones
class AccountManager:
    """Gestor CRUD para las cuentas de usuario"""
    
    def __init__(self, fernet_key: bytes):
        self.fernet_key = fernet_key
        self.accounts: List[Account] = []
        self.load_accounts()
    
    def load_accounts(self):
        """Carga todas las cuentas desde el almacenamiento"""
        self.accounts = load_accounts_data(self.fernet_key)
    
    def save_all_accounts(self):
        """Guarda todas las cuentas en el almacenamiento"""
        save_accounts_data(self.accounts, self.fernet_key)
    
    def create_account(self, platform: str, email_or_username: str, 
                      password: str, category: str, notes: str = "") -> Account:
        """Crea una nueva cuenta"""
        new_account = Account(
            platform=platform,
            email_or_username=email_or_username,
            password=password,
            category=category,
            notes=notes,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        self.accounts.append(new_account)
        self.save_all_accounts()
        return new_account
    
    def get_account_by_platform(self, platform: str) -> Optional[Account]:
        """Busca una cuenta por plataforma"""
        for account in self.accounts:
            if account.platform.lower() == platform.lower():
                return account
        return None
    
    def get_accounts_by_category(self, category: str) -> List[Account]:
        """Obtiene todas las cuentas de una categoría"""
        return [acc for acc in self.accounts 
                if acc.category.lower() == category.lower()]
    
    def update_account(self, platform: str, **kwargs) -> bool:
        """Actualiza una cuenta existente"""
        account = self.get_account_by_platform(platform)
        if not account:
            return False
        
        # Actualizar campos permitidos
        updatable_fields = ['email_or_username', 'password', 'category', 'notes']
        for field, value in kwargs.items():
            if field in updatable_fields and value is not None:
                setattr(account, field, value)
        
        account.updated_at = datetime.now().isoformat()
        self.save_all_accounts()
        return True
    
    def delete_account(self, platform: str) -> bool:
        """Elimina una cuenta"""
        account = self.get_account_by_platform(platform)
        if not account:
            return False
        
        self.accounts.remove(account)
        self.save_all_accounts()
        return True
    
    def search_accounts(self, query: str) -> List[Account]:
        """Busca cuentas por texto en plataforma o usuario/email"""
        query = query.lower()
        return [acc for acc in self.accounts 
                if query in acc.platform.lower() or 
                   query in acc.email_or_username.lower()]
    
    def suggest_strong_password(self, length: int = 16) -> str:
        """Sugiere una contraseña fuerte"""
        return generate_strong_password(
            length=length,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_symbols=True
        )
    
    def get_all_categories(self) -> List[str]:
        """Obtiene todas las categorías únicas"""
        categories = set(acc.category for acc in self.accounts)
        return sorted(list(categories))
    
    def get_all_accounts(self) -> list:
        """Obtiene todas las cuentas"""
        return self.accounts
        
    def get_accounts_summary(self) -> dict:
        """Obtiene un resumen de las cuentas"""
        summary = {
            'total': len(self.accounts),
            'by_category': {}
        }
        
        for category in self.get_all_categories():
            summary['by_category'][category] = len(
                self.get_accounts_by_category(category)
            )
        
        return summary
    
"""    def get_all_accounts(self) -> List[Account]:
        return self.accounts"""