from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QTableWidget, QTableWidgetItem,
                            QMessageBox, QGroupBox, QComboBox, QTabWidget)
from backend.database import DatabaseConnection
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
        
        # Crear pestañas
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 2px solid #ddd; border-radius: 8px; background-color: #f5f5f5; }
            QTabBar::tab { background-color: #e0e0e0; padding: 8px 20px; margin-right: 2px; 
                          border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background-color: #f5f5f5; border: 2px solid #ddd; border-bottom: none; }
        """)
        
        # Pestaña de Facturas de Ventas
        tab_ventas = QWidget()
        self.init_tab_ventas(tab_ventas)
        tabs.addTab(tab_ventas, "Facturas de Ventas")
        
        # Pestaña de Facturas de Compras
        tab_compras = QWidget()
        self.init_tab_compras(tab_compras)
        tabs.addTab(tab_compras, "Facturas de Compras")
        
        layout.addWidget(tabs)
        
    def init_tab_ventas(self, tab):
        layout = QVBoxLayout(tab)
        
        # Tabla de ventas
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(8)
        self.tabla_ventas.setHorizontalHeaderLabels([
            "ID", "Cliente", "Cantidad (kg)", "Precio/kg", 
            "Total", "Fecha", "Estado", "Factura"
        ])
        
        # Botón para generar factura
        btn_layout = QHBoxLayout()
        self.btn_generar_factura = QPushButton("📄 Generar Factura")
        self.btn_generar_factura.clicked.connect(self.generar_factura_venta)
        btn_layout.addWidget(self.btn_generar_factura)
        
        layout.addWidget(self.tabla_ventas)
        layout.addLayout(btn_layout)
        
        # Cargar datos iniciales
        self.cargar_ventas()
        
    def init_tab_compras(self, tab):
        layout = QVBoxLayout(tab)
        
        # Tabla de compras
        self.tabla_compras = QTableWidget()
        self.tabla_compras.setColumnCount(8)
        self.tabla_compras.setHorizontalHeaderLabels([
            "ID", "Proveedor", "Cantidad (kg)", "Precio/kg", 
            "Total", "Fecha", "Estado", "Factura"
        ])
        
        # Botón para generar factura
        btn_layout = QHBoxLayout()
        self.btn_generar_factura_compra = QPushButton("📄 Generar Factura")
        self.btn_generar_factura_compra.clicked.connect(self.generar_factura_compra)
        btn_layout.addWidget(self.btn_generar_factura_compra)
        
        layout.addWidget(self.tabla_compras)
        layout.addLayout(btn_layout)
        
        # Cargar datos iniciales
        self.cargar_compras()
        
    def cargar_ventas(self):
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT v.*, c.nombre_empresa
                        FROM ventas v
                        JOIN clientes c ON v.cliente_id = c.id
                        ORDER BY v.fecha_venta DESC
                    """)
                    ventas = cur.fetchall()
                    
                    self.tabla_ventas.setRowCount(len(ventas))
                    for i, venta in enumerate(ventas):
                        self.tabla_ventas.setItem(i, 0, QTableWidgetItem(str(venta['id'])))
                        self.tabla_ventas.setItem(i, 1, QTableWidgetItem(venta['nombre_empresa']))
                        self.tabla_ventas.setItem(i, 2, QTableWidgetItem(f"{venta['cantidad_kg']:.2f}"))
                        self.tabla_ventas.setItem(i, 3, QTableWidgetItem(f"{venta['precio_kg']:.2f}"))
                        self.tabla_ventas.setItem(i, 4, QTableWidgetItem(f"{venta['total']:.2f}"))
                        self.tabla_ventas.setItem(i, 5, QTableWidgetItem(str(venta['fecha_venta'])))
                        self.tabla_ventas.setItem(i, 6, QTableWidgetItem(venta['estado_cobro']))
                        
                        # Verificar si existe la factura
                        fecha = venta['fecha_venta'].strftime('%Y%m%d')
                        factura_path = f'facturas/factura_venta_{venta["id"]}_{fecha}.pdf'
                        if os.path.exists(factura_path):
                            self.tabla_ventas.setItem(i, 7, QTableWidgetItem("✅ Generada"))
                        else:
                            self.tabla_ventas.setItem(i, 7, QTableWidgetItem("❌ No generada"))
                            
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar ventas: {str(e)}")
            
    def cargar_compras(self):
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT c.*, p.nombre, p.apellido
                        FROM compras c
                        JOIN proveedores p ON c.proveedor_id = p.id
                        ORDER BY c.fecha_compra DESC
                    """)
                    compras = cur.fetchall()
                    
                    self.tabla_compras.setRowCount(len(compras))
                    for i, compra in enumerate(compras):
                        self.tabla_compras.setItem(i, 0, QTableWidgetItem(str(compra['id'])))
                        self.tabla_compras.setItem(i, 1, QTableWidgetItem(f"{compra['nombre']} {compra['apellido']}"))
                        self.tabla_compras.setItem(i, 2, QTableWidgetItem(f"{compra['cantidad_kg']:.2f}"))
                        self.tabla_compras.setItem(i, 3, QTableWidgetItem(f"{compra['precio_kg']:.2f}"))
                        self.tabla_compras.setItem(i, 4, QTableWidgetItem(f"{compra['total']:.2f}"))
                        self.tabla_compras.setItem(i, 5, QTableWidgetItem(str(compra['fecha_compra'])))
                        self.tabla_compras.setItem(i, 6, QTableWidgetItem(compra['estado_pago']))
                        
                        # Verificar si existe la factura
                        fecha = compra['fecha_compra'].strftime('%Y%m%d')
                        factura_path = f'facturas/factura_compra_{compra["id"]}_{fecha}.pdf'
                        if os.path.exists(factura_path):
                            self.tabla_compras.setItem(i, 7, QTableWidgetItem("✅ Generada"))
                        else:
                            self.tabla_compras.setItem(i, 7, QTableWidgetItem("❌ No generada"))
                            
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar compras: {str(e)}")
            
    def generar_factura_venta(self):
        try:
            # Obtener la fila seleccionada
            fila = self.tabla_ventas.currentRow()
            if fila < 0:
                self.mostrar_mensaje("Error", "Debe seleccionar una venta")
                return
                
            # Obtener el ID de la venta
            venta_id = int(self.tabla_ventas.item(fila, 0).text())
            
            # Generar la factura
            factura_path = self.reporte_manager.generar_factura_venta(venta_id)
            
            if factura_path:
                self.mostrar_mensaje("Éxito", f"Factura generada correctamente en:\n{factura_path}")
                self.cargar_ventas()
            else:
                self.mostrar_mensaje("Error", "No se pudo generar la factura")
                
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al generar factura: {str(e)}")
            
    def generar_factura_compra(self):
        try:
            # Obtener la fila seleccionada
            fila = self.tabla_compras.currentRow()
            if fila < 0:
                self.mostrar_mensaje("Error", "Debe seleccionar una compra")
                return
                
            # Obtener el ID de la compra
            compra_id = int(self.tabla_compras.item(fila, 0).text())
            
            # Generar la factura
            factura_path = self.reporte_manager.generar_factura_compra(compra_id)
            
            if factura_path:
                self.mostrar_mensaje("Éxito", f"Factura generada correctamente en:\n{factura_path}")
                self.cargar_compras()
            else:
                self.mostrar_mensaje("Error", "No se pudo generar la factura")
                
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al generar factura: {str(e)}")
            
    def mostrar_mensaje(self, titulo, mensaje):
        QMessageBox.information(self, titulo, mensaje)