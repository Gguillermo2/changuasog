# main.py
import sys
from PySide6.QtWidgets import QApplication
from Vista.login import start_login
from Vista.home import HomeWindow

def main():
    app = QApplication(sys.argv)
    
    # Configurar estilo global
    app.setStyleSheet("""
        QApplication {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """)
    
    def on_login_success(admin_user, fernet_key):
        """Callback cuando el login es exitoso"""
        # Cerrar ventana de login y abrir home
        home = HomeWindow(admin_user, fernet_key)
        home.show()
    
    # Iniciar con la ventana de login
    login = start_login(on_login_success)
    login.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()