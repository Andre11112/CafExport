from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QStackedWidget, QTableWidget,
                            QTableWidgetItem)
from PyQt6.QtCore import Qt
from frontend.views.proveedores import ProveedoresView
from frontend.views.ventas import VentasView
from frontend.views.compras import ComprasView

class MainWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("CafeExport")
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QHBoxLayout(central_widget)
        
        # Menú lateral
        sidebar = QWidget()
        sidebar.setMaximumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Botones del menú
        self.create_menu_buttons(sidebar_layout)
        layout.addWidget(sidebar)
        
        # Contenedor principal para las diferentes vistas
        self.stack_widget = QStackedWidget()
        layout.addWidget(self.stack_widget)
        
        # Crear las diferentes vistas
        self.create_views()
        
    def create_menu_buttons(self, layout):
        buttons = [
            ("Compras", self.show_compras),
            ("Ventas", self.show_ventas),
            ("Reportes", self.show_reportes),
        ]
        
        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            layout.addWidget(button)
            
        layout.addStretch()
        
        # Botón de cerrar sesión
        logout_button = QPushButton("Cerrar Sesión")
        logout_button.clicked.connect(self.handle_logout)
        layout.addWidget(logout_button)
        
    def create_views(self):
        # Vista de Compras
        self.compras_view = ComprasView(self.user_id)
        self.stack_widget.addWidget(self.compras_view)
        
        # Vista de Proveedores
        self.proveedores_view = ProveedoresView(self.user_id)
        self.stack_widget.addWidget(self.proveedores_view)
        
        # Vista de Ventas
        self.ventas_view = VentasView(self.user_id)
        self.stack_widget.addWidget(self.ventas_view)
        
    def show_compras(self):
        self.stack_widget.setCurrentWidget(self.compras_view)
        
    def show_ventas(self):
        self.stack_widget.setCurrentWidget(self.ventas_view)
        
    def show_proveedores(self):
        self.stack_widget.setCurrentWidget(self.proveedores_view)
        
    def show_clientes(self):
        # Implementar vista de clientes
        pass
        
    def show_reportes(self):
        # Implementar vista de reportes
        pass
        
    def handle_logout(self):
        self.close() 