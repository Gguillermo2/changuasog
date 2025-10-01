# main.py
import sys
from PySide6.QtWidgets import QApplication
from Vista.login import LoginWindow
from Vista.home import HomeWindow


def main():
    app = QApplication(sys.argv)
    
    # Configurar estilo global
    app.setStyleSheet("""
        QApplication {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """)
    
    # Variable para mantener referencia a la ventana actual
    current_window = None
    
    def on_login_success(admin_user, fernet_key):
        """Callback cuando el login es exitoso"""
        nonlocal current_window
        
        try:
            print("✅ Iniciando ventana principal...")
            
            # Cerrar la ventana de login
            if login:
                login.close()
            
            # Crear y mostrar la ventana Home directamente
            home = HomeWindow(admin_user, fernet_key)
            home.show()
            
            # Actualizar la referencia a la ventana actual
            current_window = home
            
            print("✅ Ventana principal abierta exitosamente")
            
        except Exception as e:
            print(f"❌ Error al iniciar Home: {e}")
            import traceback
            traceback.print_exc()
            # Si hay error, cerrar la aplicación
            app.quit()

    login = LoginWindow(on_login_success)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()