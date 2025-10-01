# views/home.py - Versión PySide6 CORREGIDA
import sys
import os
from datetime import datetime
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                               QStackedWidget, QMessageBox, QSpacerItem, QComboBox,
                               QSizePolicy, QGraphicsDropShadowEffect, QTextEdit,
                               QDialog, QDialogButtonBox, QGridLayout, QMenu,
                               QAbstractItemView, QStyledItemDelegate)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, Signal, QSize
from PySide6.QtGui import QFont, QColor, QIcon, QPainter, QPen, QBrush, QAction

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.account_manager import AccountManager
from Modelo.models import Account


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


class ModernTextEdit(QTextEdit):
    """TextEdit personalizado con estilo moderno"""
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit:focus {
                border-color: #0d7377;
                background-color: #333333;
            }
            QTextEdit:hover {
                border-color: #555555;
            }
        """)
        self.setMaximumHeight(100)


class ModernComboBox(QComboBox):
    """ComboBox personalizado con estilo moderno"""
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 45px;
            }
            QComboBox:hover {
                border-color: #555555;
            }
            QComboBox:focus {
                border-color: #0d7377;
                background-color: #333333;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #0d7377;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #0d7377;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 5px;
            }
        """)


class ModernButton(QPushButton):
    """Botón personalizado con estilo moderno"""
    def __init__(self, text, style_type="primary", icon_text=""):
        super().__init__()
        
        if icon_text:
            self.setText(f"{icon_text} {text}")
        else:
            self.setText(text)
        
        base_style = """
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """
        
        if style_type == "primary":
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #0a5d61;
                }
                QPushButton:pressed {
                    background-color: #084a4d;
                }
            """)
        elif style_type == "success":
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #14ae5c;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #119950;
                }
                QPushButton:pressed {
                    background-color: #0e7d42;
                }
            """)
        elif style_type == "danger":
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
        elif style_type == "secondary":
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #404040;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
                QPushButton:pressed {
                    background-color: #333333;
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


class CategoryDelegate(QStyledItemDelegate):
    """Delegado personalizado para mostrar categorías con colores"""
    
    CATEGORY_COLORS = {
        "Personal": "#0d7377",
        "Trabajo": "#14ae5c",
        "Redes Sociales": "#3b82f6",
        "Entretenimiento": "#8b5cf6",
        "Finanzas": "#f59e0b",
        "Educación": "#ec4899",
        "Otros": "#6b7280"
    }
    
    def paint(self, painter, option, index):
        if index.column() == 3:  # Columna de categoría (ahora es la 3)
            painter.save()
            
            # Obtener el texto de la categoría
            category = index.data()
            color = self.CATEGORY_COLORS.get(category, "#6b7280")
            
            # Dibujar fondo de la celda
            if option.state & option.State_Selected:
                painter.fillRect(option.rect, QColor("#0d7377"))
            
            # Crear rectángulo para el badge
            badge_rect = QRect(
                option.rect.x() + 10,
                option.rect.y() + 10,
                option.rect.width() - 20,
                option.rect.height() - 20
            )
            
            # Dibujar el badge
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRoundedRect(badge_rect, 4, 4)
            
            # Dibujar el texto
            painter.setPen(QPen(QColor("white")))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, category)
            
            painter.restore()
        else:
            super().paint(painter, option, index)


class AccountDialog(QDialog):
    """Diálogo para agregar/editar cuentas"""
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle("Editar Cuenta" if account else "Nueva Cuenta")
        self.setFixedSize(500, 550)
        self.setModal(True)
        
        self.setup_ui()
        
        if account:
            self.load_account_data()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("🔐 " + ("Editar Cuenta" if self.account else "Nueva Cuenta"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #0d7377;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Campos del formulario
        layout.addWidget(QLabel("Plataforma/Servicio:"))
        self.platform_entry = ModernLineEdit("Ej: Gmail, Netflix, etc.")
        layout.addWidget(self.platform_entry)
        
        layout.addWidget(QLabel("Email o Usuario:"))
        self.email_entry = ModernLineEdit("Ej: usuario@gmail.com")
        layout.addWidget(self.email_entry)
        
        layout.addWidget(QLabel("Contraseña:"))
        password_layout = QHBoxLayout()
        self.password_entry = ModernLineEdit("Contraseña segura", True)
        self.toggle_password_btn = ModernButton("👁", "secondary")
        self.toggle_password_btn.setMaximumWidth(50)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.password_entry)
        password_layout.addWidget(self.toggle_password_btn)
        layout.addLayout(password_layout)
        
        layout.addWidget(QLabel("Categoría:"))
        self.category_combo = ModernComboBox()
        self.category_combo.addItems([
            "Personal", "Trabajo", "Redes Sociales", 
            "Entretenimiento", "Finanzas", "Educación", "Otros"
        ])
        layout.addWidget(self.category_combo)
        
        layout.addWidget(QLabel("Notas (opcional):"))
        self.notes_entry = ModernTextEdit("Notas adicionales...")
        layout.addWidget(self.notes_entry)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = ModernButton("Cancelar", "secondary")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = ModernButton("Guardar", "success", "💾")
        save_btn.clicked.connect(self.save_account)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_password_visibility(self):
        """Alterna la visibilidad de la contraseña"""
        if self.password_entry.echoMode() == QLineEdit.EchoMode.Password:
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("🙈")
        else:
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("👁")
    
    def load_account_data(self):
        """Carga los datos de la cuenta en el formulario"""
        self.platform_entry.setText(self.account.platform)
        self.email_entry.setText(self.account.email_or_username)
        self.password_entry.setText(self.account.password)
        self.category_combo.setCurrentText(self.account.category)
        self.notes_entry.setText(self.account.notes or "")
    
    def save_account(self):
        """Valida y guarda la cuenta"""
        # Validar campos requeridos
        if not all([self.platform_entry.text(), self.email_entry.text(), self.password_entry.text()]):
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos obligatorios")
            return
        
        # Crear o actualizar cuenta usando los nombres correctos del modelo
        account_data = {
            "platform": self.platform_entry.text(),
            "email_or_username": self.email_entry.text(),
            "password": self.password_entry.text(),
            "category": self.category_combo.currentText(),
            "notes": self.notes_entry.toPlainText() or None,
            "updated_at": datetime.now().isoformat()
        }
        
        if self.account:
            # Si es edición, preservar created_at
            account_data["created_at"] = self.account.created_at
        else:
            # Si es nueva, agregar created_at
            account_data["created_at"] = datetime.now().isoformat()
        
        self.account_data = account_data
        self.accept()


class HomeWindow(QMainWindow):
    def __init__(self, admin_user, fernet_key):
        super().__init__()
        self.admin_user = admin_user
        self.fernet_key = fernet_key
        self.account_manager = AccountManager(fernet_key)
        self.accounts_list = []  # Lista para mantener las cuentas con IDs
        
        self.setup_ui()
        self.load_accounts()
    
    def setup_ui(self):
        """Configura la interfaz principal"""
        self.setWindowTitle("Gestor de Contraseñas - Home")
        self.setGeometry(100, 100, 1200, 800)
        
        # Estilo global
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header(main_layout)
        
        # Contenido
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1e1e1e; padding: 20px;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Barra de herramientas
        self.create_toolbar(content_layout)
        
        # Tabla de cuentas
        self.create_accounts_table(content_layout)
        
        # Estadísticas
        self.create_stats_bar(content_layout)
        
        main_layout.addWidget(content_widget)
    
    def create_header(self, parent_layout):
        """Crea el header de la aplicación"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background-color: #0d7377;
                border-bottom: 2px solid #0a5d61;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Logo y título
        logo_section = QHBoxLayout()
        logo_section.setSpacing(15)
        
        logo = QLabel("🔐")
        logo.setStyleSheet("font-size: 36px;")
        logo_section.addWidget(logo)
        
        title_section = QVBoxLayout()
        title_section.setSpacing(5)
        
        app_title = QLabel("Gestor de Contraseñas")
        app_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
        """)
        title_section.addWidget(app_title)
        
        welcome_label = QLabel(f"Bienvenido, {self.admin_user.username}")
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #cccccc;
            }
        """)
        title_section.addWidget(welcome_label)
        
        logo_section.addLayout(title_section)
        header_layout.addLayout(logo_section)
        
        header_layout.addStretch()
        
        # Botón de cerrar sesión
        logout_btn = QPushButton("🚪 Cerrar Sesión")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 2px solid white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        
        parent_layout.addWidget(header)
    
    def create_toolbar(self, parent_layout):
        """Crea la barra de herramientas"""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Búsqueda
        self.search_entry = ModernLineEdit("🔍 Buscar cuentas...")
        self.search_entry.textChanged.connect(self.filter_accounts)
        toolbar_layout.addWidget(self.search_entry, 2)
        
        # Filtro de categoría
        self.category_filter = ModernComboBox()
        self.category_filter.addItem("Todas las categorías")
        self.category_filter.addItems([
            "Personal", "Trabajo", "Redes Sociales", 
            "Entretenimiento", "Finanzas", "Educación", "Otros"
        ])
        self.category_filter.currentTextChanged.connect(self.filter_accounts)
        toolbar_layout.addWidget(self.category_filter, 1)
        
        toolbar_layout.addStretch()
        
        # Botones de acción
        add_btn = ModernButton("Nueva Cuenta", "success", "➕")
        add_btn.clicked.connect(self.add_account)
        toolbar_layout.addWidget(add_btn)
        
        parent_layout.addWidget(toolbar_widget)
    
    def create_accounts_table(self, parent_layout):
        """Crea la tabla de cuentas"""
        # Frame contenedor
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 1px solid #404040;
            }
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabla con 5 columnas ahora
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(5)
        self.accounts_table.setHorizontalHeaderLabels([
            "Plataforma", "Usuario/Email", "Contraseña", "Categoría", "Acciones"
        ])
        
        # Estilo de la tabla
        self.accounts_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #404040;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #404040;
            }
            QTableWidget::item:selected {
                background-color: #0d7377;
            }
            QHeaderView::section {
                background-color: #252525;
                color: white;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #404040;
                font-weight: bold;
                font-size: 14px;
            }
            QTableCornerButton::section {
                background-color: #252525;
                border: none;
            }
        """)
        
        # Configuración de la tabla
        self.accounts_table.setAlternatingRowColors(False)
        self.accounts_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.accounts_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.accounts_table.horizontalHeader().setStretchLastSection(True)
        self.accounts_table.verticalHeader().setVisible(False)
        
        # Configurar ancho de columnas
        self.accounts_table.setColumnWidth(0, 200)  # Plataforma
        self.accounts_table.setColumnWidth(1, 250)  # Usuario/Email
        self.accounts_table.setColumnWidth(2, 200)  # Contraseña
        self.accounts_table.setColumnWidth(3, 150)  # Categoría
        
        # Aplicar delegado personalizado para categorías (ahora columna 3)
        self.accounts_table.setItemDelegateForColumn(3, CategoryDelegate())
        
        table_layout.addWidget(self.accounts_table)
        
        parent_layout.addWidget(table_frame)
    
    def create_stats_bar(self, parent_layout):
        """Crea la barra de estadísticas"""
        stats_frame = QFrame()
        stats_frame.setFixedHeight(80)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 1px solid #404040;
            }
        """)
        
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(30, 0, 30, 0)
        
        # Total de cuentas
        self.total_accounts_label = self.create_stat_widget("📊", "Total de Cuentas", "0")
        stats_layout.addWidget(self.total_accounts_label)
        
        # Separador
        separator = QFrame()
        separator.setFixedWidth(2)
        separator.setStyleSheet("background-color: #404040;")
        stats_layout.addWidget(separator)
        
        # Última actualización
        self.last_update_label = self.create_stat_widget("🕐", "Última Actualización", "Nunca")
        stats_layout.addWidget(self.last_update_label)
        
        # Separador
        separator2 = QFrame()
        separator2.setFixedWidth(2)
        separator2.setStyleSheet("background-color: #404040;")
        stats_layout.addWidget(separator2)
        
        # Categoría más usada
        self.top_category_label = self.create_stat_widget("🏆", "Categoría Principal", "N/A")
        stats_layout.addWidget(self.top_category_label)
        
        parent_layout.addWidget(stats_frame)
    
    def create_stat_widget(self, icon, title, value):
        """Crea un widget de estadística"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        layout.addWidget(icon_label)
        
        # Textos
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #999999;
            }
        """)
        text_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #0d7377;
            }
        """)
        value_label.setObjectName(f"{title.lower().replace(' ', '_')}_value")
        text_layout.addWidget(value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return widget
    
    def load_accounts(self):
        """Carga todas las cuentas en la tabla"""
        try:
            accounts = self.account_manager.get_all_accounts()
            # Asignar IDs a las cuentas para poder identificarlas
            self.accounts_list = []
            for i, account in enumerate(accounts):
                # Agregar un ID temporal si no existe
                if not hasattr(account, 'id'):
                    account.id = i
                self.accounts_list.append(account)
            
            self.display_accounts(self.accounts_list)
            self.update_stats(self.accounts_list)
        except Exception as e:
            print(f"Error cargando cuentas: {e}")
            self.accounts_list = []
            self.display_accounts([])
            self.update_stats([])
    
    def display_accounts(self, accounts):
        """Muestra las cuentas en la tabla"""
        self.accounts_table.setRowCount(0)
        
        for account in accounts:
            row = self.accounts_table.rowCount()
            self.accounts_table.insertRow(row)
            
            # Plataforma
            self.accounts_table.setItem(row, 0, QTableWidgetItem(account.platform))
            
            # Usuario/Email
            self.accounts_table.setItem(row, 1, QTableWidgetItem(account.email_or_username))
            
            # Contraseña (oculta)
            password_item = QTableWidgetItem("••••••••")
            password_item.setData(Qt.ItemDataRole.UserRole, account.password)
            self.accounts_table.setItem(row, 2, password_item)
            
            # Categoría
            self.accounts_table.setItem(row, 3, QTableWidgetItem(account.category))
            
            # Acciones
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(5)
            
            # Botón ver/ocultar contraseña
            view_btn = QPushButton("👁")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.clicked.connect(lambda checked, r=row: self.toggle_password(r))
            
            # Botón editar
            edit_btn = QPushButton("✏️")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #0a5d61;
                }
            """)
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked, acc=account: self.edit_account(acc))
            
            # Botón eliminar
            delete_btn = QPushButton("🗑️")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(lambda checked, acc=account: self.delete_account(acc))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.accounts_table.setCellWidget(row, 4, actions_widget)
            
            # Ajustar altura de la fila
            self.accounts_table.setRowHeight(row, 60)
    
    def update_stats(self, accounts):
        """Actualiza las estadísticas"""
        # Total de cuentas
        total_label = self.total_accounts_label.findChild(QLabel, "total_de_cuentas_value")
        if total_label:
            total_label.setText(str(len(accounts)))
        
        # Última actualización
        if accounts:
            last_updates = []
            for acc in accounts:
                if acc.updated_at:
                    last_updates.append(datetime.fromisoformat(acc.updated_at))
                elif acc.created_at:
                    last_updates.append(datetime.fromisoformat(acc.created_at))
            
            if last_updates:
                last_update = max(last_updates)
                last_update_str = last_update.strftime("%d/%m/%Y %H:%M")
            else:
                last_update_str = "Nunca"
        else:
            last_update_str = "Nunca"
        
        last_label = self.last_update_label.findChild(QLabel, "última_actualización_value")
        if last_label:
            last_label.setText(last_update_str)
        
        # Categoría más usada
        if accounts:
            categories = [acc.category for acc in accounts]
            most_common = max(set(categories), key=categories.count)
            count = categories.count(most_common)
            category_str = f"{most_common} ({count})"
        else:
            category_str = "N/A"
        
        category_label = self.top_category_label.findChild(QLabel, "categoría_principal_value")
        if category_label:
            category_label.setText(category_str)
    
    def filter_accounts(self):
        """Filtra las cuentas según búsqueda y categoría"""
        search_text = self.search_entry.text().lower()
        category_filter = self.category_filter.currentText()
        
        filtered_accounts = []
        
        for account in self.accounts_list:
            # Filtro de búsqueda
            if search_text:
                if not any([
                    search_text in account.platform.lower(),
                    search_text in account.email_or_username.lower(),
                    search_text in (account.notes or "").lower()
                ]):
                    continue
            
            # Filtro de categoría
            if category_filter != "Todas las categorías":
                if account.category != category_filter:
                    continue
            
            filtered_accounts.append(account)
        
        self.display_accounts(filtered_accounts)
    
    def toggle_password(self, row):
        """Muestra/oculta la contraseña en una fila"""
        password_item = self.accounts_table.item(row, 2)
        current_text = password_item.text()
        
        if current_text == "••••••••":
            # Mostrar contraseña
            real_password = password_item.data(Qt.ItemDataRole.UserRole)
            password_item.setText(real_password)
            
            # Cambiar icono del botón
            actions_widget = self.accounts_table.cellWidget(row, 4)
            view_btn = actions_widget.findChildren(QPushButton)[0]
            view_btn.setText("🙈")
        else:
            # Ocultar contraseña
            password_item.setText("••••••••")
            
            # Cambiar icono del botón
            actions_widget = self.accounts_table.cellWidget(row, 4)
            view_btn = actions_widget.findChildren(QPushButton)[0]
            view_btn.setText("👁")
    
    def add_account(self):
        """Muestra el diálogo para agregar una cuenta"""
        dialog = AccountDialog(self)
        if dialog.exec():
            try:
                # Crear nueva cuenta
                new_account = Account(**dialog.account_data)
                self.account_manager.add_account(new_account)
                
                # Recargar tabla
                self.load_accounts()
                
                # Mostrar mensaje de éxito
                self.show_message("Éxito", "Cuenta agregada correctamente", "info")
            except Exception as e:
                self.show_message("Error", f"Error al agregar cuenta: {str(e)}", "critical")
    
    def edit_account(self, account):
        """Muestra el diálogo para editar una cuenta"""
        dialog = AccountDialog(self, account)
        if dialog.exec():
            try:
                # Actualizar cuenta - usar el índice para actualizar
                updated_account = Account(**dialog.account_data)
                
                # Encontrar el índice de la cuenta en la lista
                account_index = None
                for i, acc in enumerate(self.accounts_list):
                    if acc.id == account.id:
                        account_index = i
                        break
                
                if account_index is not None:
                    self.account_manager.update_account(account_index, updated_account)
                
                # Recargar tabla
                self.load_accounts()
                
                # Mostrar mensaje de éxito
                self.show_message("Éxito", "Cuenta actualizada correctamente", "info")
            except Exception as e:
                self.show_message("Error", f"Error al actualizar cuenta: {str(e)}", "critical")
    
    def delete_account(self, account):
        """Elimina una cuenta con confirmación"""
        # Diálogo de confirmación
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar Eliminación")
        msg.setText(f"¿Está seguro de que desea eliminar la cuenta '{account.platform}'?")
        msg.setInformativeText("Esta acción no se puede deshacer.")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        # Estilo del mensaje
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
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0a5d61;
            }
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            try:
                # Encontrar el índice de la cuenta
                account_index = None
                for i, acc in enumerate(self.accounts_list):
                    if acc.id == account.id:
                        account_index = i
                        break
                
                if account_index is not None:
                    self.account_manager.delete_account(account_index)
                
                self.load_accounts()
                self.show_message("Éxito", "Cuenta eliminada correctamente", "info")
            except Exception as e:
                self.show_message("Error", f"Error al eliminar cuenta: {str(e)}", "critical")
    
    def logout(self):
        """Cierra sesión y vuelve al login"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Cerrar Sesión")
        msg.setText("¿Está seguro de que desea cerrar sesión?")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
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
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0a5d61;
            }
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.close()
            # Aquí podrías reiniciar la aplicación o mostrar el login nuevamente
            QApplication.quit()
    
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
        
        # Estilo moderno para el message box
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
    
    def closeEvent(self, event):
        """Evento al cerrar la ventana"""
        # Guardar cualquier cambio pendiente
        event.accept()


def start_home(admin_user, fernet_key):
    """
    Inicia la ventana principal del gestor
    admin_user: usuario autenticado
    fernet_key: clave Fernet para encriptación
    """
    # NO crear una nueva aplicación, usar la existente
    app = QApplication.instance()
    
    # Solo aplicar estilos si no se han aplicado antes
    if app:
        app.setStyleSheet("""
            QApplication {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QToolTip {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #404040;
                padding: 5px;
                border-radius: 4px;
            }
        """)
    
    # Crear y mostrar la ventana Home
    home = HomeWindow(admin_user, fernet_key)
    home.show()
    

    return home 


if __name__ == "__main__":
    from Modelo.models import AdminUser
    from cryptography.fernet import Fernet
    
    test_user = AdminUser(
        username="admin",
        password="hashed_password",
        password_2fa="hashed_2fa",
        fernet_key_salt="salt"
    )
    
    test_key = Fernet.generate_key()
    
    app = QApplication(sys.argv)
    home = HomeWindow(test_user, test_key)
    home.show()
    sys.exit(app.exec())