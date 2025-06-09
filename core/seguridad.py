import random
import os
import bcrypt
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

#-- CONFIGURACION DE RUTAS

RUTA_DBWROSER =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DBwroser" )
KEY_FILE_NAME =  "fernet_key.key"
KEY_FILE_PATH = os.path.join(RUTA_DBWROSER, KEY_FILE_NAME)

def hash_pasword_bcrypt(password: str) -> str:
    hashhed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashhed.decode('utf-8')

def check_password_bcrypt(password: str,  hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def _ensure_db_directory_exists():
    if not os.path.exists(RUTA_DBWROSER):
        os.makedirs(RUTA_DBWROSER)

def generate_and_save_fernet_key():
    """Genera una nueva clave Fernet y la guarda en un archivo."""
    _ensure_db_directory_exists()
    if not os.path.exists(KEY_FILE_PATH):
        key = Fernet.generate_key()
        with open(KEY_FILE_PATH, "wb") as keyfile:
            keyfile.write(key)
        print(f"Clave Fernet generada y guardada en: {KEY_FILE_PATH}")
    else:
        print(f"El archivo de clave Fernet ya existe en: {KEY_FILE_PATH}")

def load_fernet_key() -> bytes:
    """Carga la clave Fernet desde el archivo."""
    _ensure_db_directory_exists() # Asegurar que el directorio exista antes de intentar leer
    if not os.path.exists(KEY_FILE_PATH):
        # Opcional: Generar y guardar si no existe, o lanzar un error si se espera que exista
        generate_and_save_fernet_key()
    
    with open(KEY_FILE_PATH, "rb") as keyfile:
        return keyfile.read()
try:
    _loaded_fernet_key = load_fernet_key()
    cipher = Fernet(_loaded_fernet_key)
except FileNotFoundError:
    print("Advertencia: Clave Fernet no encontrada al iniciar seguridad.py. Asegúrate de generarla.")
    cipher = None # O manejar el error de otra forma

def encrypt_data_fernet(data: str) -> str:
    """Cifra una cadena de texto usando Fernet y retorna la cadena cifrada (base64)."""
    if cipher is None:
        raise ValueError("El objeto Fernet no está inicializado. Asegúrate de que la clave exista.")
    return cipher.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_data_fernet(encrypted_data: str) -> str:
    """Descifra una cadena cifrada con Fernet y retorna la cadena original."""
    if cipher is None:
        raise ValueError("El objeto Fernet no está inicializado. Asegúrate de que la clave exista.")
    return cipher.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')

def generate_strong_password(length: int = 12,
                             use_uppercase: bool = True,
                             use_lowercase: bool = True,
                             use_digits: bool = True,
                             use_symbols: bool = True) -> str:
    """
    Genera una contraseña fuerte con caracteres seleccionados.
    """
    characters = ""
    if use_lowercase:
        characters += "abcdefghijklmnopqrstuvwxyz"
    if use_uppercase:
        characters += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if use_digits:
        characters += "0123456789"
    if use_symbols:
        characters += "!@#$%^&*()-_+=[]{}|;:,.<>?"

    if not characters:
        raise ValueError("Debe seleccionar al menos un tipo de caracter para la contraseña.")

    password = ''.join(random.choice(characters) for i in range(length))
    return password










