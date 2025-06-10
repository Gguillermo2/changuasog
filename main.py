from core.autenticacion import autenticar_admin, generar_Admin,verificar_2fa

def iniciar_aplicacion():
    # 1. Asegurarse de que el directorio DBwroser exista (se puede mover a un inicio global)
    # seguridad._ensure_db_directory_exists() # Llamar una vez al inicio de la app

    # 2. Gestionar el usuario administrador
    generar_Admin() # Se encargará de crearlo si no existe

    # 3. Intentar autenticar al usuario maestro
    admin_user, session_fernet_key = autenticar_admin()

    if admin_user and session_fernet_key:
        print("Acceso concedido al gestor de contraseñas.")
        # Aquí la `session_fernet_key` es tu "llave" para la sesión.
        # Pásala a las funciones de almacenamiento/gestión de cuentas.

        # Opcional: Proceso de 2FA
        if admin_user.password_2fa: # Solo si tiene 2FA configurado
            if verificar_2fa(admin_user):
                print("Verificación 2FA exitosa. Puedes acceder a funciones sensibles.")
                # Puedes generar el código 2FA aquí si lo necesitas
                # code_2fa = autenticacion.obtener_codigo_2fa()
            else:
                print("Verificación 2FA fallida. Acceso restringido a funciones sensibles.")
                # Podrías salir o limitar funcionalidades
                return

        # A partir de aquí, puedes cargar y mostrar las cuentas
        # (pasando `session_fernet_key` a las funciones de `almacenamiento`)
        # from core.almacenamiento import load_accounts_encrypted # Suponiendo que la crees
        # cuentas = load_accounts_encrypted("cuentas.json", session_fernet_key)
        # ... lógica de la GUI ...

    else:
        print("Fallo en la autenticación. Saliendo.")

if __name__ == "__main__":
    iniciar_aplicacion()