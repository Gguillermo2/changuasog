# views/login.py - Versión PySide6 CORREGIDA
import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QFrame, QStackedWidget, QMessageBox, QSpacerItem,
                               QSizePolicy, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation, QRect
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QIcon

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.autenticacion import autenticar_admin, verificar_2fa, obtener_codigo_2fa
from core.almacenamiento import load_json_data
from core.seguridad import hash_password_bcrypt, generate_salt
from Modelo.models import AdminUser
from core.almacenamiento import save_jsonD
from base64 import urlsafe_b64encode


class ModernLineEdit(QLineEdit):
    """LineEdit personalizado con estilo moderno"""
    def __init__(self, placeholder="", is_password=False):
        super().__init__()
        self.setPlaceholderText(placeholder)
        if is_password:
            self.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit:focus {
                border-color: #0d7377;
                background-color: #333333;
            }
            QLineEdit:hover {
                border-color: #555555;
            }
        """)
        self.setMinimumHeight(45)


class ModernButton(QPushButton):
    """Botón personalizado con estilo moderno"""
    def __init__(self, text, style_type="primary"):
        super().__init__(text)
        
        if style_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QPushButton:hover {
                    background-color: #0a5d61;
                }
                QPushButton:pressed {
                    background-color: #084a4d;
                }
            """)
        elif style_type == "success":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #14ae5c;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QPushButton:hover {
                    background-color: #119950;
                }
                QPushButton:pressed {
                    background-color: #0e7d42;
                }
            """)
        
        self.setMinimumHeight(45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Agregar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class LoginWindow(QMainWindow):
    def __init__(self, on_success_callback):
        super().__init__()
        self.on_success_callback = on_success_callback  # CORREGIDO: nombre consistente
        self.current_user = None
        self.fernet_key = None
        
        self.setup_ui()
        self.setup_styles()
        
        # Verificar si existe usuario admin
        if not self.check_admin_exists():
            self.show_create_admin_screen()
        else:
            self.show_login_screen()
    
    def setup_ui(self):
        """Configura la interfaz básica"""
        self.setWindowTitle("Gestor de Contraseñas - Login")
        self.setFixedSize(450, 600)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        
        # Widget central con stack para múltiples pantallas
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
    
    def setup_styles(self):
        """Configura los estilos globales"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: white;
            }
        """)
    
    def check_admin_exists(self):
        """Verifica si existe un usuario administrador"""
        return load_json_data("DBusers.json") is not None
    
    def create_card_frame(self):
        """Crea un frame con estilo de tarjeta"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 1px solid #404040;
            }
        """)
        
        # Agregar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        frame.setGraphicsEffect(shadow)
        
        return frame
    
    def show_create_admin_screen(self):
        """Muestra la pantalla de creación de admin"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Spacer superior
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Título
        title = QLabel("🛡️ Crear Usuario Administrador")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #0d7377;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel("Configure su usuario administrador para comenzar")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #cccccc; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Tarjeta de formulario
        card = self.create_card_frame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)
        
        # Campos del formulario
        self.create_username_entry = ModernLineEdit("Ingrese su nombre de usuario")
        self.create_password_entry = ModernLineEdit("Contraseña maestra", True)
        self.create_password_2fa_entry = ModernLineEdit("Contraseña para 2FA", True)
        
        card_layout.addWidget(QLabel("Nombre de usuario:"))
        card_layout.addWidget(self.create_username_entry)
        card_layout.addWidget(QLabel("Contraseña maestra:"))
        card_layout.addWidget(self.create_password_entry)
        card_layout.addWidget(QLabel("Contraseña para 2FA:"))
        card_layout.addWidget(self.create_password_2fa_entry)
        
        # Botón crear
        create_btn = ModernButton("Crear Usuario Administrador")
        create_btn.clicked.connect(self.create_admin)
        card_layout.addWidget(create_btn)
        
        layout.addWidget(card)
        
        # Spacer inferior
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.stacked_widget.addWidget(widget)
        self.stacked_widget.setCurrentWidget(widget)
    
    def create_admin(self):
        """Crea el usuario administrador"""
        username = self.create_username_entry.text()
        password = self.create_password_entry.text()
        password_2fa = self.create_password_2fa_entry.text()
        
        if not all([username, password, password_2fa]):
            self.show_message("Error", "Todos los campos son obligatorios", "warning")
            return
        
        try:
            # Hash de contraseñas
            hashed_password = hash_password_bcrypt(password)
            hashed_password_2fa = hash_password_bcrypt(password_2fa)
            
            # Generar salt para Fernet
            fernet_salt_bytes = generate_salt()
            fernet_salt_str = urlsafe_b64encode(fernet_salt_bytes).decode('utf-8')
            
            # Crear usuario
            nuevo_admin = AdminUser(
                username=username,
                password=hashed_password,
                password_2fa=hashed_password_2fa,
                fernet_key_salt=fernet_salt_str
            )
            
            # Guardar
            save_jsonD("DBusers.json", nuevo_admin.model_dump())
            
            self.show_message("Éxito", "Usuario administrador creado correctamente", "info")
            self.show_login_screen()
            
        except Exception as e:
            self.show_message("Error", f"Error al crear usuario: {str(e)}", "critical")
    
    def show_login_screen(self):
        """Muestra la pantalla de login"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Spacer superior
        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Logo y título
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.setSpacing(15)
        
        # Emoji como logo
        logo = QLabel("🔐")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 64px;")
        logo_layout.addWidget(logo)
        
        # Título
        title = QLabel("Gestor de Contraseñas")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: white;
            }
        """)
        logo_layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel("Acceso seguro a sus credenciales")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #cccccc; font-size: 14px;")
        logo_layout.addWidget(subtitle)
        
        layout.addLayout(logo_layout)
        
        # Tarjeta de login
        card = self.create_card_frame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)
        
        # Campos de login
        self.login_username_entry = ModernLineEdit("Usuario")
        self.login_password_entry = ModernLineEdit("Contraseña", True)
        
        card_layout.addWidget(self.login_username_entry)
        card_layout.addWidget(self.login_password_entry)
        
        # Botón de login
        login_btn = ModernButton("Iniciar Sesión")
        login_btn.clicked.connect(self.attempt_login)
        card_layout.addWidget(login_btn)
        
        layout.addWidget(card)
        
        # Spacer inferior
        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Configurar Enter key
        self.login_username_entry.returnPressed.connect(self.attempt_login)
        self.login_password_entry.returnPressed.connect(self.attempt_login)
        
        self.stacked_widget.addWidget(widget)
        self.stacked_widget.setCurrentWidget(widget)
    
    def attempt_login(self):
        """Intenta hacer login con las credenciales"""
        username = self.login_username_entry.text()
        password = self.login_password_entry.text()
        
        if not username or not password:
            self.show_message("Error", "Por favor complete todos los campos", "warning")
            return
        
        try:
            # Simular entrada para autenticar_admin
            from unittest.mock import patch
            
            with patch('builtins.input', side_effect=[username]):
                with patch('getpass.getpass', return_value=password):
                    admin_user, fernet_key = autenticar_admin()
            
            if admin_user and fernet_key:
                self.current_user = admin_user
                self.fernet_key = fernet_key
                self.show_2fa_screen()
            else:
                self.show_message("Error", "Usuario o contraseña incorrectos", "warning")
                self.login_password_entry.clear()
                
        except Exception as e:
            self.show_message("Error", f"Error en la autenticación: {str(e)}", "critical")
    
    def show_2fa_screen(self):
        """Muestra la pantalla de verificación 2FA"""
        try:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(40, 40, 40, 40)
            layout.setSpacing(20)
            
            # Título
            title = QLabel("🔑 Verificación en Dos Pasos")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #0d7377;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(title)
            
            # Instrucciones
            instructions = QLabel("Por favor ingrese la contraseña 2FA para generar un código de verificación:")
            instructions.setWordWrap(True)
            instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
            instructions.setStyleSheet("color: #cccccc; font-size: 14px; margin-bottom: 20px;")
            layout.addWidget(instructions)
            
            # Campo para contraseña 2FA
            self.password_2fa_entry = ModernLineEdit("Contraseña 2FA", True)
            
            # Botón verificar
            verify_btn = ModernButton("Verificar y Generar Código")
            verify_btn.clicked.connect(self.verify_2fa)
            
            # Frame para el código (se mostrará después)
            self.code_frame = QFrame()
            self.code_layout = QVBoxLayout(self.code_frame)
            self.code_layout.setContentsMargins(0, 0, 0, 0)
            self.code_layout.setSpacing(15)
            self.code_frame.hide()
            
            # Agregar widgets al layout
            layout.addWidget(self.password_2fa_entry)
            layout.addWidget(verify_btn)
            layout.addSpacing(20)
            layout.addWidget(self.code_frame)
            
            # Configurar Enter key
            self.password_2fa_entry.returnPressed.connect(self.verify_2fa)
            
            # Agregar widget al stack
            self.stacked_widget.addWidget(widget)
            self.stacked_widget.setCurrentWidget(widget)
            
        except Exception as e:
            self.show_message("Error", f"Error al mostrar la pantalla 2FA: {str(e)}", "critical")
    
    def verify_2fa(self):
        """Verifica la contraseña 2FA y muestra el código"""
        password_2fa = self.password_2fa_entry.text()
        
        if not password_2fa:
            self.show_message("Error", "Por favor ingrese la contraseña 2FA", "warning")
            return
        
        try:
            # Verificar contraseña 2FA
            from unittest.mock import patch
            
            with patch('getpass.getpass', return_value=password_2fa):
                if verificar_2fa(self.current_user):
                    # Generar y mostrar código
                    code = obtener_codigo_2fa()
                    self.show_code_input(code)
                else:
                    self.show_message("Error", "Contraseña 2FA incorrecta", "warning")
                    self.password_2fa_entry.clear()
                    
        except Exception as e:
            self.show_message("Error", f"Error en la verificación 2FA: {str(e)}", "critical")
    
    def show_code_input(self, generated_code):
        """Muestra el campo para ingresar el código"""
        # Limpiar frame de código
        for i in reversed(range(self.code_layout.count())):
            widget = self.code_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Mostrar código generado
        code_display = QFrame()
        code_display.setStyleSheet("""
            QFrame {
                border-radius: 12px;
                border: 2px solid #0d7377;
                padding: 15px;
            }
        """)
        code_display_layout = QVBoxLayout(code_display)
        code_display_layout.setContentsMargins(20, 15, 20, 15)
        
        code_label = QLabel(f"{generated_code}")
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setStyleSheet("""
            QLabel {
                color: #0d7377;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
                background-color: rgba(13, 115, 119, 0.1);
                border-radius: 8px;
                padding: 15px;
                letter-spacing: 5px;
                border: 1px solid #0d7377;
            }
        """)
        code_display_layout.addWidget(code_label)
        
        self.code_layout.addWidget(code_display)
        
        # Campo para ingresar código
        instruction = QLabel("Ingrese el código mostrado arriba:")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet("color: #cccccc; font-size: 14px;")
        self.code_layout.addWidget(instruction)
        
        self.code_entry = ModernLineEdit("Código de verificación")
        self.code_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.code_layout.addWidget(self.code_entry)
        
        # Botón confirmar
        confirm_btn = ModernButton("Confirmar Código", "success")
        confirm_btn.clicked.connect(lambda: self.confirm_code(generated_code))
        self.code_layout.addWidget(confirm_btn)
        
        # Mostrar el frame y enfocar
        self.code_frame.show()
        self.code_entry.setFocus()
        
        # Configurar Enter key
        self.code_entry.returnPressed.connect(lambda: self.confirm_code(generated_code))
    
    def confirm_code(self, correct_code):
        """Confirma el código ingresado"""
        entered_code = self.code_entry.text()
        
        if entered_code == correct_code:
            self.show_message("Éxito", "¡Autenticación completada exitosamente!", "info")
            
            # Programar cierre y callback
            QTimer.singleShot(500, self.close_and_callback)
        else:
            self.show_message("Error", "Código incorrecto, intente nuevamente", "warning")
            self.code_entry.clear()
            self.code_entry.setFocus()
    
    def close_and_callback(self):
        """Cierra la ventana y ejecuta el callback"""
        try:
            if self.on_success_callback and self.current_user and self.fernet_key:
                # Ocultar primero
                self.hide()
                # Llamar al callback
                self.on_success_callback(self.current_user, self.fernet_key)
                # Luego cerrar
                self.close()
            else:
                self.show_message("Error", "Faltan datos para continuar", "critical")
        except Exception as e:
            print(f"Error en close_and_callback: {e}")
            import traceback
            traceback.print_exc()
    
    def show_message(self, title, message, icon_type="info"):
        """Muestra un mensaje con estilo moderno"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        
        # Configurar icono
        if icon_type == "info":
            msg.setIcon(QMessageBox.Icon.Information)
        elif icon_type == "warning":
            msg.setIcon(QMessageBox.Icon.Warning)
        elif icon_type == "critical":
            msg.setIcon(QMessageBox.Icon.Critical)
    
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #0a5d61;
            }
        """)
        msg.exec()