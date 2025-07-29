# core/almacenamiento.py
import os
import json
from typing import List, Dict, Optional
from core.seguridad import encrypt_data_fernet, decrypt_data_fernet 
from Modelo.models import Account  # Cambiado de Cuentas
from core.seguridad import _ensure_db_directory_exists as ensure_db_directory_E

RUTA_DBWROSER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DBwroser")
PASSWORDS_DATA_FILE = "passwords_data.json"

def save_jsonD(filename: str, data: dict):
    """
    Guarda datos en un archivo JSON en el directorio DBwroser.
    """
    ensure_db_directory_E()
    full_path = os.path.join(RUTA_DBWROSER, filename)
    try:
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"✅ Datos guardados correctamente en {filename}") 
    except IOError as e:
        print(f"❌ Error al guardar datos en {full_path}: {e}")

def load_json_data(filename: str) -> Optional[Dict]:
    """Carga datos de un archivo JSON desde DBwroser."""
    full_path = os.path.join(RUTA_DBWROSER, filename)
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON de {full_path}: {e}")
            return None
        except IOError as e:
            print(f"❌ Error al cargar datos de {full_path}: {e}")
            return None
    return None   

def save_accounts_data(accounts: List[Account], fernet_key: bytes):
    """
    Cifra y guarda los datos de las cuentas en el archivo JSON.
    Requiere la clave Fernet activa de la sesión.
    """
    ensure_db_directory_E()
    
    encrypted_data = []
    for account in accounts:
        try:
            # Cifrar la contraseña
            encrypted_password = encrypt_data_fernet(account.password, fernet_key)
            
            # Crear diccionario con todos los campos
            account_dict = account.model_dump()
            account_dict['password'] = encrypted_password
            
            encrypted_data.append(account_dict)
            
        except Exception as e:
            print(f"❌ Error al cifrar la cuenta {account.platform}: {e}")
            continue

    save_jsonD(PASSWORDS_DATA_FILE, {"accounts": encrypted_data})
    print("✅ Cuentas guardadas y cifradas exitosamente.")

def load_accounts_data(fernet_key: bytes) -> List[Account]:
    """
    Carga y descifra los datos de las cuentas desde el archivo JSON.
    Requiere la clave Fernet activa de la sesión.
    """
    ensure_db_directory_E()

    data = load_json_data(PASSWORDS_DATA_FILE)
    if not data or "accounts" not in data:
        print("ℹ️  No se encontraron datos de cuentas.")
        return []

    decrypted_accounts = []
    for encrypted_account_dict in data.get("accounts", []):
        try:
            # Descifrar la contraseña
            encrypted_password = encrypted_account_dict.get('password')
            if encrypted_password:
                decrypted_password = decrypt_data_fernet(encrypted_password, fernet_key)
                
                # Reconstruir el diccionario para el modelo
                account_data = encrypted_account_dict.copy()
                account_data['password'] = decrypted_password
                
                decrypted_accounts.append(Account(**account_data))
            else:
                print(f"⚠️  Contraseña vacía para: {encrypted_account_dict.get('platform', 'Desconocida')}")
                
        except Exception as e:
            print(f"❌ Error al descifrar cuenta {encrypted_account_dict.get('platform', 'Desconocida')}: {e}")
            continue
            
    print(f"✅ {len(decrypted_accounts)} cuenta(s) cargadas exitosamente.")
    return decrypted_accounts