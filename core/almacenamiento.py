import os
import json
from core.seguridad import encrypt_data_fernet, decrypt_data_fernet,load_fernet_key
from Modelo.models import Cuentas

RUTA_DBWROSER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DBwroser")
PASSWORDS_DATA_FILE = "passwords_data.json"


def  ensure_db_directoryE():
    if not os.path.exists(RUTA_DBWROSER):
        os.makedirs(RUTA_DBWROSER)
        print(f"Directorio Creado   {RUTA_DBWROSER}")

def save_jsonD(filename: str, data: dict):
    ensure_db_directoryE()
    full_path = os.path.join(RUTA_DBWROSER, filename)
    try:
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent= 4)
        print(f"DATOS GUARDADOS cORRECTAMENTE EN {full_path}: {e}")
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
    # print(f"El archivo {filename} no existe en: {full_path}") # Se comentó para no saturar la consola
    return None   

def save_accounts_data(accounts: list[Cuentas]):
    ensure_db_directoryE()
    
    try:
       
        pass
    except Exception as e:
        print(f"Error: No se pudo cargar la clave Fernet para cifrar datos: {e}")
        return

    encrypted_data = []
    for account in accounts:
        # Cifrar solo el campo sensible (la contraseña)
        # Asegúrate de que account.password exista y sea una cadena
        try:
            encrypted_password = encrypt_data_fernet(account.password)
            # Crear un diccionario del modelo sin la contraseña en texto claro,
            # y luego añadir la contraseña cifrada.
            account_dict = account.model_dump() # Pydantic v2 usa model_dump()
            account_dict['password'] = encrypted_password # Sobrescribir con la versión cifrada
            encrypted_data.append(account_dict)
        except ValueError as e:
            print(f"Error al cifrar la contraseña de la cuenta {account.platform}: {e}")
            continue
        except AttributeError:
             print(f"Error: El objeto Cuenta no tiene un atributo 'password' o no es una cadena.")
             continue


    save_jsonD(PASSWORDS_DATA_FILE, {"accounts": encrypted_data})
    print("Contraseñas de cuentas guardadas (cifradas) exitosamente.")


def load_accounts_data() -> list[Cuentas]:
    """
    Carga y descifra los datos de las cuentas desde el archivo JSON.
    """
    ensure_db_directoryE()

    try:
        
        pass
    except Exception as e:
        print(f"Error: No se pudo cargar la clave Fernet para descifrar datos: {e}")
        return []

    data = load_json_data(PASSWORDS_DATA_FILE)
    if not data or "accounts" not in data:
        return []

    decrypted_accounts = []
    for encrypted_account_dict in data.get("accounts", []):
        try:
            encrypted_password = encrypted_account_dict.get('password')
            if encrypted_password:
                decrypted_password = decrypt_data_fernet(encrypted_password)
                # Reconstruir el diccionario para el modelo Pydantic
                account_data_for_model = encrypted_account_dict.copy()
                account_data_for_model['password'] = decrypted_password
                decrypted_accounts.append(Cuentas(**account_data_for_model))
            else:
                print(f"Advertencia: Contraseña no encontrada o vacía para la cuenta: {encrypted_account_dict.get('platform', 'Desconocida')}")
                # Si no hay contraseña, se podría cargar el resto del objeto sin ella o omitir
                decrypted_accounts.append(Cuentas(**encrypted_account_dict)) # Cargar sin contraseña
        except ValueError as e:
            print(f"Error al descifrar la contraseña de la cuenta {encrypted_account_dict.get('platform', 'Desconocida')}: {e}")
            continue
        except Exception as e: # Captura otros errores de Pydantic o datos faltantes
            print(f"Error al procesar la cuenta {encrypted_account_dict.get('platform', 'Desconocida')}: {e}")
            continue
            
    print("Contraseñas de cuentas cargadas y descifradas exitosamente.")
    return decrypted_accounts


