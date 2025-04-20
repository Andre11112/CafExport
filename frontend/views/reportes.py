from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QDateEdit, QMessageBox, QFileDialog)
from PyQt6.QtCore import QDate
from backend.reportes import ReporteFacturas
import os

class ReportesView(QWidget):
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.reporte_manager = ReporteFacturas()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Sección de fechas
        fecha_layout = QHBoxLayout()
        fecha_layout.addWidget(QLabel("Fecha Inicio:"))
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        fecha_layout.addWidget(self.fecha_inicio)
        
        fecha_layout.addWidget(QLabel("Fecha Fin:"))
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        fecha_layout.addWidget(self.fecha_fin)
        
        layout.addLayout(fecha_layout)
        
        # Botones de reportes
        btn_layout = QHBoxLayout()
        
        self.btn_reporte_ventas = QPushButton("Generar Reporte de Ventas")
        self.btn_reporte_ventas.clicked.connect(self.generar_reporte_ventas)
        btn_layout.addWidget(self.btn_reporte_ventas)
        
        self.btn_reporte_compras = QPushButton("Generar Reporte de Compras")
        self.btn_reporte_compras.clicked.connect(self.generar_reporte_compras)
        btn_layout.addWidget(self.btn_reporte_compras)
        
        layout.addLayout(btn_layout)
        
    def generar_reporte_ventas(self):
        try:
            fecha_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
            
            # Obtener la ruta donde guardar el archivo
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte de Ventas",
                os.path.expanduser("~/Desktop"),
                "PDF Files (*.pdf)"
            )
            
            if filename:
                # Generar el reporte
                pdf_path = self.reporte_manager.generar_reporte_ventas(fecha_inicio, fecha_fin)
                if pdf_path:
                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"Reporte de ventas generado correctamente en:\n{pdf_path}"
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "No se pudo generar el reporte de ventas"
                    )
                    
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al generar reporte de ventas: {str(e)}"
            )
            
    def generar_reporte_compras(self):
        try:
            fecha_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
            
            # Obtener la ruta donde guardar el archivo
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte de Compras",
                os.path.expanduser("~/Desktop"),
                "PDF Files (*.pdf)"
            )
            
            if filename:
                # Generar el reporte
                pdf_path = self.reporte_manager.generar_reporte_compras(fecha_inicio, fecha_fin)
                if pdf_path:
                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"Reporte de compras generado correctamente en:\n{pdf_path}"
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "No se pudo generar el reporte de compras"
                    )
                    
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al generar reporte de compras: {str(e)}"
            ) 