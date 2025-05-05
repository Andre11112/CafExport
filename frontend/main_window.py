from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QStackedWidget, QTableWidget,
                            QTableWidgetItem)
from PyQt6.QtCore import Qt
from frontend.views.proveedores import ProveedoresView
from frontend.views.ventas import VentasView
from frontend.views.compras import ComprasView
from frontend.views.reportes import ReportesView
from frontend.views.dashboard import Dashboard
from frontend.views.cierres import CierreContableWidget

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
            ("Panel de Control", self.show_dashboard),
            ("Compras", self.show_compras),
            ("Ventas", self.show_ventas),
            ("Reportes", self.show_reportes),
            ("Cierre Mensual", self.show_cierres),
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
        # Crear las vistas
        self.dashboard_view = Dashboard()
        self.compras_view = ComprasView(self.user_id)
        self.ventas_view = VentasView(self.user_id)
        self.reportes_view = ReportesView(self.user_id)
        self.cierres_view = CierreContableWidget()
        
        # Agregar las vistas al stack
        self.stack_widget.addWidget(self.dashboard_view)
        self.stack_widget.addWidget(self.compras_view)
        self.stack_widget.addWidget(self.ventas_view)
        self.stack_widget.addWidget(self.reportes_view)
        self.stack_widget.addWidget(self.cierres_view)
        
        # Mostrar el dashboard por defecto
        self.show_dashboard()
        
    def show_dashboard(self):
        self.stack_widget.setCurrentWidget(self.dashboard_view)
        
    def show_compras(self):
        self.stack_widget.setCurrentWidget(self.compras_view)
        
    def show_ventas(self):
        self.stack_widget.setCurrentWidget(self.ventas_view)
        
    def show_reportes(self):
        self.stack_widget.setCurrentWidget(self.reportes_view)
        
    def show_cierres(self):
        self.stack_widget.setCurrentWidget(self.cierres_view)
        
    def handle_logout(self):
        self.close() 