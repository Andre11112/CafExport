from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QLabel, QLineEdit, QComboBox, QMessageBox,
                            QDialog, QFormLayout, QDoubleSpinBox, QTextEdit)
from PyQt6.QtCore import Qt
from backend.facturacionback import FacturacionBackend

class NuevaFacturaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Factura")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        # Campos del formulario
        self.cliente_combo = QComboBox()
        self.cantidad_input = QDoubleSpinBox()
        self.cantidad_input.setMaximum(10000)
        self.cantidad_input.setDecimals(2)
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setMaximum(1000000)
        self.precio_input.setDecimals(2)
        self.notas_input = QTextEdit()
        
        layout.addRow("Cliente:", self.cliente_combo)
        layout.addRow("Cantidad (kg):", self.cantidad_input)
        layout.addRow("Precio por kg:", self.precio_input)
        layout.addRow("Notas:", self.notas_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        self.guardar_btn = QPushButton("Guardar")
        self.cancelar_btn = QPushButton("Cancelar")
        
        buttons_layout.addWidget(self.guardar_btn)
        buttons_layout.addWidget(self.cancelar_btn)
        
        layout.addRow(buttons_layout)
        
        # Conectar señales
        self.guardar_btn.clicked.connect(self.accept)
        self.cancelar_btn.clicked.connect(self.reject)

class PagoDialog(QDialog):
    def __init__(self, factura_id, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Pago")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        # Campos del formulario
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setMaximum(total)
        self.monto_input.setDecimals(2)
        self.metodo_combo = QComboBox()
        self.metodo_combo.addItems(["Efectivo", "Transferencia", "Cheque", "Otro"])
        self.referencia_input = QLineEdit()
        
        layout.addRow("Monto:", self.monto_input)
        layout.addRow("Método de pago:", self.metodo_combo)
        layout.addRow("Referencia:", self.referencia_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        self.guardar_btn = QPushButton("Guardar")
        self.cancelar_btn = QPushButton("Cancelar")
        
        buttons_layout.addWidget(self.guardar_btn)
        buttons_layout.addWidget(self.cancelar_btn)
        
        layout.addRow(buttons_layout)
        
        # Conectar señales
        self.guardar_btn.clicked.connect(self.accept)
        self.cancelar_btn.clicked.connect(self.reject)

class FacturacionWindow(QMainWindow):
    def __init__(self, usuario_id):
        super().__init__()
        self.setWindowTitle("Módulo de Facturación")
        self.setMinimumSize(800, 600)
        
        self.usuario_id = usuario_id
        self.backend = FacturacionBackend()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Barra de búsqueda y filtros
        filtros_layout = QHBoxLayout()
        self.busqueda_input = QLineEdit()
        self.busqueda_input.setPlaceholderText("Buscar facturas...")
        self.busqueda_input.textChanged.connect(self.filtrar_facturas)
        
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Todos", "pendiente", "parcial", "pagado"])
        self.estado_combo.currentTextChanged.connect(self.filtrar_facturas)
        
        filtros_layout.addWidget(QLabel("Buscar:"))
        filtros_layout.addWidget(self.busqueda_input)
        filtros_layout.addWidget(QLabel("Estado:"))
        filtros_layout.addWidget(self.estado_combo)
        
        # Tabla de facturas
        self.tabla_facturas = QTableWidget()
        self.tabla_facturas.setColumnCount(7)
        self.tabla_facturas.setHorizontalHeaderLabels([
            "ID", "Cliente", "Fecha", "Total", "Estado", "Usuario", "Notas"
        ])
        self.tabla_facturas.itemDoubleClicked.connect(self.mostrar_detalles)
        
        # Botones
        botones_layout = QHBoxLayout()
        self.nueva_factura_btn = QPushButton("Nueva Factura")
        self.nueva_factura_btn.clicked.connect(self.crear_nueva_factura)
        self.registrar_pago_btn = QPushButton("Registrar Pago")
        self.registrar_pago_btn.clicked.connect(self.registrar_pago)
        self.imprimir_btn = QPushButton("Imprimir Factura")
        self.imprimir_btn.clicked.connect(self.imprimir_factura)
        
        botones_layout.addWidget(self.nueva_factura_btn)
        botones_layout.addWidget(self.registrar_pago_btn)
        botones_layout.addWidget(self.imprimir_btn)
        
        # Agregar widgets al layout principal
        layout.addLayout(filtros_layout)
        layout.addWidget(self.tabla_facturas)
        layout.addLayout(botones_layout)
        
        # Cargar datos iniciales
        self.cargar_facturas()
        
    def cargar_facturas(self):
        """Carga todas las facturas en la tabla"""
        facturas = self.backend.obtener_facturas()
        self.tabla_facturas.setRowCount(len(facturas))
        
        for i, factura in enumerate(facturas):
            self.tabla_facturas.setItem(i, 0, QTableWidgetItem(str(factura['id'])))
            self.tabla_facturas.setItem(i, 1, QTableWidgetItem(factura['cliente_nombre']))
            self.tabla_facturas.setItem(i, 2, QTableWidgetItem(factura['fecha']))
            self.tabla_facturas.setItem(i, 3, QTableWidgetItem(str(factura['total'])))
            self.tabla_facturas.setItem(i, 4, QTableWidgetItem(factura['estado_pago']))
            self.tabla_facturas.setItem(i, 5, QTableWidgetItem(factura['usuario_nombre']))
            self.tabla_facturas.setItem(i, 6, QTableWidgetItem(factura['notas'] or ''))
            
    def filtrar_facturas(self):
        """Filtra las facturas según los criterios de búsqueda"""
        busqueda = self.busqueda_input.text()
        estado = self.estado_combo.currentText()
        
        filtro = []
        if busqueda:
            filtro.append(f"(c.nombre_empresa LIKE '%{busqueda}%' OR f.id LIKE '%{busqueda}%')")
        if estado != "Todos":
            filtro.append(f"f.estado_pago = '{estado}'")
            
        filtro_str = " AND ".join(filtro) if filtro else None
        facturas = self.backend.obtener_facturas(filtro_str)
        
        self.tabla_facturas.setRowCount(len(facturas))
        for i, factura in enumerate(facturas):
            self.tabla_facturas.setItem(i, 0, QTableWidgetItem(str(factura['id'])))
            self.tabla_facturas.setItem(i, 1, QTableWidgetItem(factura['cliente_nombre']))
            self.tabla_facturas.setItem(i, 2, QTableWidgetItem(factura['fecha']))
            self.tabla_facturas.setItem(i, 3, QTableWidgetItem(str(factura['total'])))
            self.tabla_facturas.setItem(i, 4, QTableWidgetItem(factura['estado_pago']))
            self.tabla_facturas.setItem(i, 5, QTableWidgetItem(factura['usuario_nombre']))
            self.tabla_facturas.setItem(i, 6, QTableWidgetItem(factura['notas'] or ''))
            
    def mostrar_detalles(self, item):
        """Muestra los detalles de una factura seleccionada"""
        factura_id = self.tabla_facturas.item(item.row(), 0).text()
        detalles = self.backend.obtener_detalles_factura(factura_id)
        pagos = self.backend.obtener_pagos_factura(factura_id)
        
        mensaje = f"Detalles de la factura {factura_id}:\n\n"
        mensaje += "Detalles:\n"
        for detalle in detalles:
            mensaje += f"- {detalle['cantidad_kg']} kg a ${detalle['precio_kg']} = ${detalle['subtotal']}\n"
            
        mensaje += "\nPagos:\n"
        for pago in pagos:
            mensaje += f"- ${pago['monto']} ({pago['metodo_pago']}) - {pago['fecha_pago']}\n"
            
        QMessageBox.information(self, "Detalles de Factura", mensaje)
        
    def crear_nueva_factura(self):
        """Abre el diálogo para crear una nueva factura"""
        dialog = NuevaFacturaDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Aquí se implementaría la lógica para crear la factura
            detalles = [{
                'cantidad_kg': dialog.cantidad_input.value(),
                'precio_kg': dialog.precio_input.value()
            }]
            
            factura_id = self.backend.crear_factura(
                cliente_id=1,  # Aquí se debería obtener el ID del cliente seleccionado
                usuario_id=self.usuario_id,
                detalles=detalles,
                notas=dialog.notas_input.toPlainText()
            )
            
            if factura_id:
                QMessageBox.information(self, "Éxito", "Factura creada correctamente")
                self.cargar_facturas()
            else:
                QMessageBox.critical(self, "Error", "No se pudo crear la factura")
                
    def registrar_pago(self):
        """Abre el diálogo para registrar un pago"""
        selected_row = self.tabla_facturas.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una factura")
            return
            
        factura_id = self.tabla_facturas.item(selected_row, 0).text()
        total = float(self.tabla_facturas.item(selected_row, 3).text())
        
        dialog = PagoDialog(factura_id, total, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if self.backend.registrar_pago(
                factura_id=factura_id,
                monto=dialog.monto_input.value(),
                usuario_id=self.usuario_id,
                metodo_pago=dialog.metodo_combo.currentText(),
                referencia_pago=dialog.referencia_input.text()
            ):
                QMessageBox.information(self, "Éxito", "Pago registrado correctamente")
                self.cargar_facturas()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el pago")
                
    def imprimir_factura(self):
        """Imprime la factura seleccionada"""
        selected_row = self.tabla_facturas.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una factura")
            return
            
        factura_id = self.tabla_facturas.item(selected_row, 0).text()
        # Aquí se implementaría la lógica para imprimir la factura
        QMessageBox.information(self, "Imprimir Factura",
                              f"Imprimiendo factura {factura_id}...") 