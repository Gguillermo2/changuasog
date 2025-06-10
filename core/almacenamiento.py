import os
import json
# Importar las funciones de cifrado/descifrado que AHORA RECIBEN LA CLAVE
from core.seguridad import encrypt_data_fernet, decrypt_data_fernet 
from Modelo.models import Cuentas
# Importar la función de utilidad para el directorio (si la movemos aquí o la centralizamos)
from core.seguridad import _ensure_db_directory_exists as ensure_db_directory_E # Renombrar para evitar conflictos

RUTA_DBWROSER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DBwroser")
PASSWORDS_DATA_FILE = "passwords_data.json"

# --- Se elimina la función local ensure_db_directoryE()
# --- y se usa la que ya existe en seguridad.py (con un alias)

def save_jsonD(filename: str, data: dict):
    """
    Guarda datos en un archivo JSON en el directorio DBwroser.
    """
    ensure_db_directory_E() # Usar la función centralizada
    full_path = os.path.join(RUTA_DBWROSER, filename)
    try:
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        # Corregir el mensaje de éxito
        print(f"DATOS GUARDADOS CORRECTAMENTE EN {full_path}") 
    except IOError as e:
        print(f"Error al guardar datos en {full_path}: {e}")

def load_json_data(filename: str) -> dict | None:
    """Carga datos de un archivo JSON desde DBwroser."""
    full_path = os.path.join(RUTA_DBWROSER, filename)
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON de {full_path}: {e}")
            return None
        except IOError as e:
            print(f"Error al cargar datos de {full_path}: {e}")
            return None
    # print(f"El archivo {filename} no existe en: {full_path}") 
    return None   

# --- FUNCIONES DE ALMACENAMIENTO DE CUENTAS (AHORA RECIBEN FERNAT_KEY) ---

def save_accounts_data(accounts: list[Cuentas], fernet_key: bytes):
    """
    Cifra y guarda los datos de las cuentas en el archivo JSON.
    Requiere la clave Fernet activa de la sesión.
    """
    ensure_db_directory_E() # Usar la función centralizada
    
    encrypted_data = []
    for account in accounts:
        try:
            # Asegúrate de que account.password exista y sea una cadena
            if account.password: # Solo cifrar si hay una contraseña
                encrypted_password = encrypt_data_fernet(account.password, fernet_key) # ¡Pasar fernet_key!
                account_dict = account.model_dump() 
                account_dict['password'] = encrypted_password # Sobrescribir con la versión cifrada
                encrypted_data.append(account_dict)
            else:
                # Si no hay contraseña, guardar el resto de los datos tal cual
                encrypted_data.append(account.model_dump())
        except ValueError as e:
            print(f"Error al cifrar la contraseña de la cuenta {account.platform}: {e}")
            continue
        except AttributeError:
             print(f"Error: El objeto Cuenta no tiene un atributo 'password' o no es una cadena.")
             continue
        except Exception as e:
            print(f"Error inesperado al procesar la cuenta {account.platform}: {e}")
            continue

    save_jsonD(PASSWORDS_DATA_FILE, {"accounts": encrypted_data})
    print("Contraseñas de cuentas guardadas (cifradas) exitosamente.")


def load_accounts_data(fernet_key: bytes) -> list[Cuentas]:
    """
    Carga y descifra los datos de las cuentas desde el archivo JSON.
    Requiere la clave Fernet activa de la sesión.
    """
    ensure_db_directory_E() # Usar la función centralizada

    data = load_json_data(PASSWORDS_DATA_FILE)
    if not data or "accounts" not in data:
        print("No se encontraron datos de cuentas o el archivo está vacío.")
        return []

    decrypted_accounts = []
    for encrypted_account_dict in data.get("accounts", []):
        try:
            encrypted_password = encrypted_account_dict.get('password')
            if encrypted_password:
                # ¡Pasar fernet_key a decrypt_data_fernet!
                decrypted_password = decrypt_data_fernet(encrypted_password, fernet_key) 
                # Reconstruir el diccionario para el modelo Pydantic
                account_data_for_model = encrypted_account_dict.copy()
                account_data_for_model['password'] = decrypted_password
                decrypted_accounts.append(Cuentas(**account_data_for_model))
            else:
                print(f"Advertencia: Contraseña no encontrada o vacía para la cuenta: {encrypted_account_dict.get('platform', 'Desconocida')}")
                # Si no hay contraseña, se carga el resto del objeto sin ella
                decrypted_accounts.append(Cuentas(**encrypted_account_dict)) 
        except ValueError as e:
            print(f"Error al descifrar la contraseña de la cuenta {encrypted_account_dict.get('platform', 'Desconocida')}: {e}")
            # Si el descifrado falla, no añadimos esta cuenta a la lista de descifradas.
            continue
        except Exception as e: 
            print(f"Error al procesar la cuenta {encrypted_account_dict.get('platform', 'Desconocida')}: {e}")
            continue
            
    print("Contraseñas de cuentas cargadas y descifradas exitosamente.")
    return decrypted_accounts