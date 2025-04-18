from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from frontend.main_window import MainWindow
from backend.database import DatabaseConnection
import bcrypt

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CafExport - Login")
        self.setFixedSize(400, 300)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título
        title = QLabel("CafExport")
        title.setFont(QFont('Arial', 20))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Campos de entrada
        self.username = QLineEdit()
        self.username.setPlaceholderText("Email")
        self.username.setMaximumWidth(250)
        layout.addWidget(self.username)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Contraseña")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setMaximumWidth(250)
        layout.addWidget(self.password)
        
        # Botón de login
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setMaximumWidth(250)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)
        
        # Mensaje de error
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)
        
    def handle_login(self):
        email = self.username.text()
        password = self.password.text()
        
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, password_hash, tipo_usuario 
                        FROM usuarios 
                        WHERE email = %s AND activo = true
                    """, (email,))
                    
                    user = cur.fetchone()
                    
                    if user and bcrypt.checkpw(
                        password.encode('utf-8'), 
                        user['password_hash'].encode('utf-8')
                    ):
                        self.main_window = MainWindow(user['id'])
                        self.main_window.show()
                        self.close()
                    else:
                        self.error_label.setText("Email o contraseña incorrectos")
                        
        except Exception as e:
            self.error_label.setText(f"Error al iniciar sesión: {str(e)}") 