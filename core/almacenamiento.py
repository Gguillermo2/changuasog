import os
import json
from typing import List, Dict, Optional
from core.seguridad import encrypt_data_fernet, decrypt_data_fernet 
from Modelo.models import Account 
from core.seguridad import _ensure_db_directory_exists as ensure_db_directory_E

RUTA_DBWROSER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DBwroser")
PASSWORDS_DATA_FILE = "passwords_data.json"

def save_json_encrypted(filename: str, data: dict, fernet_key: bytes):
    """
    Guarda datos en un archivo JSON encriptado completamente
    """
    ensure_db_directory_E()
    full_path = os.path.join(RUTA_DBWROSER, filename)
    try:
        # Convertir datos a JSON string y luego a bytes
        json_str = json.dumps(data, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        
        # Encriptar todo el contenido
        encrypted_data = encrypt_data_fernet(json_bytes, fernet_key)
        
        # Guardar los bytes encriptados (no como JSON)
        with open(full_path, "wb") as file:
            file.write(encrypted_data)
        print(f"✅ Datos encriptados guardados correctamente en {filename}") 
    except Exception as e:
        print(f"❌ Error al guardar/encriptar datos en {full_path}: {e}")

def load_json_encrypted(filename: str, fernet_key: bytes) -> Optional[Dict]:
    """Carga y desencripta un archivo JSON encriptado"""
    full_path = os.path.join(RUTA_DBWROSER, filename)
    if os.path.exists(full_path):
        try:
            # Leer datos encriptados como bytes
            with open(full_path, "rb") as file:
                encrypted_data = file.read()
            
            # Desencriptar
            decrypted_data = decrypt_data_fernet(encrypted_data, fernet_key)
            
            # Convertir de bytes a JSON
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            print(f"❌ Error al desencriptar/decodificar {full_path}: {e}")
            return None
    return None

def save_accounts_data(accounts: List[Account], fernet_key: bytes):
    """
    Cifra y guarda los datos de las cuentas en el archivo JSON completamente encriptado
    """
    ensure_db_directory_E()
    
    accounts_data = []
    for account in accounts:
        try:
            # Crear diccionario con todos los campos
            account_dict = account.model_dump()
            accounts_data.append(account_dict)
        except Exception as e:
            print(f"❌ Error al procesar la cuenta {account.platform}: {e}")
            continue

    # Guardar todo el JSON encriptado
    save_json_encrypted(PASSWORDS_DATA_FILE, {"accounts": accounts_data}, fernet_key)
    print("✅ Cuentas guardadas en archivo completamente encriptado.")

def load_accounts_data(fernet_key: bytes) -> List[Account]:
    """
    Carga y descifra los datos de las cuentas desde el archivo JSON encriptado
    """
    ensure_db_directory_E()

    data = load_json_encrypted(PASSWORDS_DATA_FILE, fernet_key)
    if not data or "accounts" not in data:
        print("ℹ️  No se encontraron datos de cuentas.")
        return []

    accounts = []
    for account_dict in data.get("accounts", []):
        try:
            accounts.append(Account(**account_dict))
        except Exception as e:
            print(f"❌ Error al procesar cuenta {account_dict.get('platform', 'Desconocida')}: {e}")
            continue
            
    print(f"✅ {len(accounts)} cuenta(s) cargadas exitosamente.")
    return accounts