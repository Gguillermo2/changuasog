# core/almacenamiento.py
import os
import json
from typing import List, Dict, Optional
from core.seguridad import encrypt_data_fernet, decrypt_data_fernet, _ensure_db_directory_exists as ensure_db_directory_E
from Modelo.models import Account

RUTA_DBWROSER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DBwroser")
PASSWORDS_DATA_FILE = "passwords_data.enc"  # .enc para indicar que está encriptado
ADMIN_DATA_FILE = "DBusers.enc"  # También encriptado

def save_encrypted_json(filename: str, data: dict, fernet_key: bytes):
    """
    Guarda datos en un archivo completamente encriptado
    """
    ensure_db_directory_E()
    full_path = os.path.join(RUTA_DBWROSER, filename)
    try:
        # Convertir datos a JSON string
        json_str = json.dumps(data, indent=4, ensure_ascii=False)
        
        # Encriptar todo el contenido
        encrypted_data = encrypt_data_fernet(json_str, fernet_key)
        
        # Guardar como archivo binario encriptado
        with open(full_path, "w", encoding='utf-8') as file:
            file.write(encrypted_data)
            
        print(f"✅ Archivo completamente encriptado guardado: {filename}") 
    except Exception as e:
        print(f"❌ Error al guardar/encriptar datos en {full_path}: {e}")
        raise

def load_encrypted_json(filename: str, fernet_key: bytes) -> Optional[Dict]:
    """
    Carga y desencripta un archivo JSON completamente encriptado
    """
    full_path = os.path.join(RUTA_DBWROSER, filename)
    if not os.path.exists(full_path):
        return None
        
    try:
        # Leer el archivo encriptado
        with open(full_path, "r", encoding='utf-8') as file:
            encrypted_data = file.read()
        
        # Desencriptar
        decrypted_json = decrypt_data_fernet(encrypted_data, fernet_key)
        
        # Convertir de JSON string a diccionario
        return json.loads(decrypted_json)
    except Exception as e:
        print(f"❌ Error al desencriptar/decodificar {full_path}: {e}")
        return None

# Funciones específicas para cuentas
def save_accounts_data(accounts: List[Account], fernet_key: bytes):
    """
    Guarda todas las cuentas en un archivo completamente encriptado
    """
    accounts_data = []
    for account in accounts:
        try:
            account_dict = account.model_dump()
            accounts_data.append(account_dict)
        except Exception as e:
            print(f"❌ Error al procesar la cuenta {account.platform}: {e}")
            continue

    save_encrypted_json(PASSWORDS_DATA_FILE, {"accounts": accounts_data}, fernet_key)
    print(f"✅ {len(accounts_data)} cuenta(s) guardadas en archivo encriptado.")

def load_accounts_data(fernet_key: bytes) -> List[Account]:
    """
    Carga todas las cuentas desde el archivo encriptado
    """
    data = load_encrypted_json(PASSWORDS_DATA_FILE, fernet_key)
    if not data or "accounts" not in data:
        print("ℹ️  No se encontraron datos de cuentas.")
        return []

    accounts = []
    for account_dict in data.get("accounts", []):
        try:
            accounts.append(Account(**account_dict))
        except Exception as e:
            print(f"❌ Error al cargar cuenta: {e}")
            continue
            
    print(f"✅ {len(accounts)} cuenta(s) cargadas desde archivo encriptado.")
    return accounts

# Funciones para el usuario administrador
def save_admin_data(admin_data: dict, fernet_key: bytes):
    """
    Guarda los datos del administrador encriptados
    """
    save_encrypted_json(ADMIN_DATA_FILE, admin_data, fernet_key)

def load_admin_data(fernet_key: bytes) -> Optional[Dict]:
    """
    Carga los datos del administrador
    """
    return load_encrypted_json(ADMIN_DATA_FILE, fernet_key)

def check_admin_exists() -> bool:
    """
    Verifica si existe un archivo de administrador (sin necesidad de desencriptar)
    """
    full_path = os.path.join(RUTA_DBWROSER, ADMIN_DATA_FILE)
    return os.path.exists(full_path)