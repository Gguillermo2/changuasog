# core/autenticacion.py
import os
import getpass
from typing import Tuple, Optional
from base64 import urlsafe_b64encode, urlsafe_b64decode

from Modelo.models import AdminUser
from core.seguridad import (
    hash_password_bcrypt, check_password_bcrypt, generate_2fa,
    generate_salt, generate_fernet_key_from_password
)
from core.almacenamiento import save_admin_data, load_admin_data, check_admin_exists

def generar_Admin():
    """
    Gestiona la creación inicial del usuario administrador
    """
    if check_admin_exists():
        print(f"Ya existe un usuario administrador.")
        return False
        
    print("Creando nuevo usuario administrador...")
    nombre_admin = input("Ingrese su nombre de usuario: ")
    password = getpass.getpass("Ingrese su contraseña maestra: ")
    
    # Validaciones
    if not nombre_admin or not password:
        print("❌ El nombre de usuario y la contraseña no pueden estar vacíos.")
        return False
    
    if len(password) < 8:
        print("❌ La contraseña debe tener al menos 8 caracteres.")
        return False
    
    # Hash de la contraseña maestra
    hashed_password = hash_password_bcrypt(password)
    
    # Generar salt para derivación de clave Fernet
    fernet_salt_bytes = generate_salt()
    fernet_salt_str = urlsafe_b64encode(fernet_salt_bytes).decode('utf-8')
    
    # Derivar clave Fernet para guardar el archivo
    fernet_key = generate_fernet_key_from_password(password, fernet_salt_bytes)
    
    print("\n--- Configuración de Doble Verificación (2FA) ---")
    print("Esta es una contraseña adicional para generar códigos de acceso.")
    password_2fa = getpass.getpass("Ingrese una contraseña para la doble verificación (2FA): ")
    
    if not password_2fa:
        print("❌ La contraseña 2FA no puede estar vacía.")
        return False
    
    hashed_password_2fa = hash_password_bcrypt(password_2fa)
    
    # Crear objeto AdminUser
    nuevo_admin = AdminUser(
        username=nombre_admin,
        password=hashed_password,
        password_2fa=hashed_password_2fa,
        fernet_key_salt=fernet_salt_str
    )
    
    try:
        # Guardar el salt por separado (no encriptado)
        save_admin_salt(fernet_salt_bytes)
        
        # Guardar datos encriptados
        save_admin_data(nuevo_admin.model_dump(), fernet_key)
        print(f"✅ Usuario administrador '{nombre_admin}' creado correctamente.")
        return True
    except Exception as e:
        print(f"❌ Error al guardar usuario administrador: {e}")
        return False

def autenticar_admin() -> Tuple[Optional[AdminUser], Optional[bytes]]:
    """
    Intenta autenticar al usuario administrador
    Retorna (AdminUser, fernet_key) si es exitoso, (None, None) si falla
    """
    if not check_admin_exists():
        print("❌ No se encontró un usuario administrador. Por favor, créelo primero.")
        return None, None
    
    nombre_ingresado = input("Ingrese su nombre de usuario: ")
    password_ingresada = getpass.getpass("Ingrese su contraseña maestra: ")
    
    if not nombre_ingresado or not password_ingresada:
        print("❌ Usuario y contraseña son requeridos.")
        return None, None
    
    # Necesitamos intentar cargar los datos del admin
    # Para esto, intentamos derivar la clave con diferentes usuarios
    # En un sistema real, podrías guardar el salt en un archivo separado no encriptado
    
    try:
        # Este es un problema: necesitamos el salt para derivar la clave,
        # pero el salt está dentro del archivo encriptado.
        # Solución: Guardar el salt en un archivo separado
        
        # Por ahora, intentamos con un archivo temporal de configuración
        salt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DBwroser", "admin.salt")
        
        if not os.path.exists(salt_file):
            print("❌ No se encontró la configuración del administrador.")
            return None, None
            
        with open(salt_file, 'rb') as f:
            fernet_salt_bytes = f.read()
        
        # Derivar clave Fernet
        fernet_key = generate_fernet_key_from_password(password_ingresada, fernet_salt_bytes)
        
        # Intentar cargar datos del admin
        admin_data = load_admin_data(fernet_key)
        if not admin_data:
            print("❌ Contraseña incorrecta o archivo corrupto.")
            return None, None
        
        admin_user = AdminUser(**admin_data)
        
        # Verificar usuario y contraseña
        if (nombre_ingresado == admin_user.username and 
            check_password_bcrypt(password_ingresada, admin_user.password)):
            print("✅ Autenticación exitosa!")
            return admin_user, fernet_key
        else:
            print("❌ Usuario o contraseña incorrectos.")
            return None, None
            
    except Exception as e:
        print(f"❌ Error durante la autenticación: {e}")
        return None, None

def verificar_2fa(admin_user: AdminUser) -> bool:
    """
    Verifica la contraseña 2FA
    """
    if not admin_user.password_2fa:
        print("❌ No se ha configurado 2FA para este usuario.")
        return False
    
    password_2fa_ingresada = getpass.getpass("Ingrese su contraseña para 2FA: ")
    
    if check_password_bcrypt(password_2fa_ingresada, admin_user.password_2fa):
        print("✅ Contraseña 2FA correcta.")
        return True
    else:
        print("❌ Contraseña 2FA incorrecta.")
        return False

def obtener_codigo_2fa() -> str:
    """
    Genera y retorna un código 2FA
    """
    code = generate_2fa()
    print(f"📱 Su código 2FA es: {code}")
    return code

# Función auxiliar para guardar el salt
def save_admin_salt(salt_bytes: bytes):
    """
    Guarda el salt del admin en un archivo separado
    """
    from core.seguridad import _ensure_db_directory_exists
    _ensure_db_directory_exists()
    
    salt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DBwroser", "admin.salt")
    with open(salt_file, 'wb') as f:
        f.write(salt_bytes)