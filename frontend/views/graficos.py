from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                            QPushButton, QLabel, QDateEdit, QFileDialog)
from PyQt6.QtCore import Qt, QDate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class GraficosWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controles superiores
        controls_layout = QHBoxLayout()
        
        # Filtro de fechas
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        
        # Filtro de tipo de venta
        self.tipo_venta = QComboBox()
        self.tipo_venta.addItems(["Todas", "Local", "Exportación"])
        
        # Botón de actualizar
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_graficos)
        
        # Botón de exportar
        self.btn_exportar = QPushButton("Exportar Gráfico")
        self.btn_exportar.clicked.connect(self.exportar_grafico)
        
        # Agregar controles al layout
        controls_layout.addWidget(QLabel("Desde:"))
        controls_layout.addWidget(self.fecha_inicio)
        controls_layout.addWidget(QLabel("Hasta:"))
        controls_layout.addWidget(self.fecha_fin)
        controls_layout.addWidget(QLabel("Tipo:"))
        controls_layout.addWidget(self.tipo_venta)
        controls_layout.addWidget(self.btn_actualizar)
        controls_layout.addWidget(self.btn_exportar)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Crear figura de matplotlib
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
        # Crear gráficos iniciales
        self.actualizar_graficos()
        
    def actualizar_graficos(self):
        self.figure.clear()
        
        # Crear subplots
        ax1 = self.figure.add_subplot(211)  # Gráfico de precios
        ax2 = self.figure.add_subplot(212)  # Gráfico de ventas
        
        # Obtener fechas seleccionadas
        fecha_inicio = self.fecha_inicio.date().toPyDate()
        fecha_fin = self.fecha_fin.date().toPyDate()
        
        # Generar datos de ejemplo (reemplazar con datos reales de la base de datos)
        fechas = pd.date_range(fecha_inicio, fecha_fin)
        precios = np.random.normal(100, 5, len(fechas))
        ventas = np.random.normal(50, 10, len(fechas))
        
        # Gráfico de precios
        ax1.plot(fechas, precios, 'b-', label='Precio')
        ax1.set_title('Evolución de Precios')
        ax1.set_ylabel('Precio ($)')
        ax1.grid(True)
        ax1.legend()
        
        # Gráfico de ventas
        ax2.bar(fechas, ventas, label='Ventas')
        ax2.set_title('Volumen de Ventas')
        ax2.set_ylabel('Cantidad')
        ax2.grid(True)
        ax2.legend()
        
        # Ajustar layout
        self.figure.tight_layout()
        self.canvas.draw()
        
    def exportar_grafico(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Gráfico",
            "",
            "Imágenes PNG (*.png);;Todos los archivos (*.*)"
        )
        
        if file_name:
            self.figure.savefig(file_name, dpi=300, bbox_inches='tight') 