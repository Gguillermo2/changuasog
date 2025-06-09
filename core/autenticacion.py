import getpass
from Modelo.models import AdminUser
from core.seguridad import hash_pasword_bcrypt, check_password_bcrypt, generate_2fa
from core.almacenamiento import save_jsonD , load_json_data

UserPrincipal = "DBusers.json"


# Funcionn  generar usuario y Contraseña Principal
def generar_Admin():
    """
    Gestiona la creación inicial del usuario administrador y su contraseña 2FA.
    """
    user_data = load_json_data(UserPrincipal)

    if user_data is None:
        print("Creando nuevo usuario administrador...")
        nombre_admin = input("Ingrese su nombre de usuario: ")
        password = getpass.getpass("Ingrese su contraseña maestra: ")
        
        hashed_password = hash_pasword_bcrypt(password)

        print("\n--- Configuración de Doble Verificación (2FA) ---")
        print("Esta es una contraseña adicional para generar códigos de acceso a sus contraseñas.")
        password_2fa = getpass.getpass("Ingrese una contraseña para la doble verificación (2FA): ")
        
        hashed_password_2fa = hash_pasword_bcrypt(password_2fa)

        nuevo_admin = AdminUser(
            username=nombre_admin,
            ContresañUser=hashed_password,
            password_2fa=hashed_password_2fa # Guardamos la contraseña 2FA hasheada
        )

        save_jsonD(UserPrincipal, nuevo_admin.model_dump())
        print(f"Usuario administrador '{nombre_admin}' creado correctamente con 2FA.")
    else:
        print(f"El archivo de usuario maestro ya existe.")

def autenticar_admin() -> AdminUser | None:
    """
    Intenta autenticar al usuario administrador (primera fase: Contraseña Maestra).
    Retorna el objeto AdminUser si la autenticación es exitosa, None en caso contrario.
    """
    user_data = load_json_data(UserPrincipal)

    if user_data is None:
        print("No se encontró un usuario administrador. Por favor, créelo primero.")
        return None
    
    admin_user = AdminUser(**user_data)

    nombre_ingresado = input("Ingrese su nombre de usuario: ")
    password_ingresada = getpass.getpass("Ingrese su contraseña maestra: ")

    if nombre_ingresado == admin_user.username and \
       check_password_bcrypt(password_ingresada, admin_user.ContresañUser):
        print("¡Autenticación de contraseña maestra exitosa!")
        return admin_user
    else:
        print("Usuario o contraseña maestra incorrectos.")
        return None

def verificar_2fa(admin_user: AdminUser) -> bool:
    """
    Verifica la contraseña 2FA para permitir la generación del código.
    Retorna True si la contraseña 2FA es correcta, False en caso contrario.
    """
    if admin_user.password_2fa is None:
        print("No se ha configurado una contraseña 2FA para este usuario.")
        return False # O podrías forzar la configuración si es obligatoria

    password_2fa_ingresada = getpass.getpass("Ingrese su contraseña para Doble Verificación (2FA): ")
    
    if check_password_bcrypt(password_2fa_ingresada, admin_user.password_2fa):
        print("Contraseña 2FA correcta.")
        return True
    else:
        print("Contraseña 2FA incorrecta.")
        return False

# --- Esta función sería llamada desde la GUI después de verifiscar_2fa ---
def obtener_codigo_2fa() -> str:
    """
    Genera y retorna un código 2FA.
    Idealmente, se llamaría solo después de una verificación 2FA exitosa.
    """
    code = generate_2fa()
    print(f"Su código de Doble Verificación (2FA) es: {code}")
    # En una GUI, este código se mostraría y se podría copiar.
    # Podrías añadir un temporizador aquí para invalidar el código después de X segundos.
    return code