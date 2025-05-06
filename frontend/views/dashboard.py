from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
import datetime
from .graficos import GraficosWidget
import requests

class KPICard(QFrame):
    def __init__(self, title, value, unit="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout()
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: #666666;")
        # Valor
        self.value_label = QLabel(f"{value} {unit}")
        self.value_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)
    def update_value(self, value, unit=""):
        self.value_label.setText(f"{value} {unit}")

class Dashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        # Timer para actualización automática
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_kpis)
        self.timer.start(30000)  # Actualizar cada 30 segundos
    def init_ui(self):
        # Crear scroll area para contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Widget contenedor
        container = QWidget()
        layout = QVBoxLayout(container)
        # Título del dashboard
        title = QLabel("Panel de Control")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        # Grid para las tarjetas KPI
        grid = QGridLayout()
        # Crear tarjetas KPI
        self.utilidad_card = KPICard("Utilidad Neta", "$0", "")
        self.ventas_card = KPICard("Volumen de Ventas", "$0", "")
        self.margen_card = KPICard("Margen por Lote", "0", "%")
        # Agregar tarjetas al grid
        grid.addWidget(self.utilidad_card, 0, 0)
        grid.addWidget(self.ventas_card, 0, 1)
        grid.addWidget(self.margen_card, 0, 2)
        layout.addLayout(grid)
        # Agregar gráficos
        self.graficos = GraficosWidget()
        layout.addWidget(self.graficos)
        # Establecer el widget contenedor en el scroll area
        scroll.setWidget(container)
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        # Actualizar KPIs iniciales
        self.update_kpis()
    def update_kpis(self):
        try:
            response = requests.get("http://localhost:8000/dashboard/kpis")
            if response.status_code == 200:
                data = response.json()
                self.utilidad_card.update_value(f"${data['utilidad_neta']:,.2f}")
                self.ventas_card.update_value(f"${data['volumen_ventas']:,.2f}")
                self.margen_card.update_value(f"{data['margen_lote']}", "%")
            else:
                print(f"[ERROR] No se pudo obtener KPIs. Código: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Error al obtener KPIs: {e}") 