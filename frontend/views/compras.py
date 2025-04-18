from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QSpinBox, QDoubleSpinBox, QFormLayout,
                            QMessageBox, QGroupBox, QComboBox, QTabWidget)
from backend.api.coffee_price import CoffeePriceAPI
from backend.database import DatabaseConnection

class ComprasView(QWidget):
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.coffee_api = CoffeePriceAPI()
        self.campesinos = []  # Lista para almacenar todos los campesinos
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Crear pestañas
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: #f5f5f5;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                border-bottom: none;
            }
        """)
        
        # Pestaña de Registro de Compras
        tab_compras = QWidget()
        self.init_tab_compras(tab_compras)
        tabs.addTab(tab_compras, "Registro de Compras")
        
        # Pestaña de Registro de Campesinos
        tab_campesinos = QWidget()
        self.init_tab_campesinos(tab_campesinos)
        tabs.addTab(tab_campesinos, "Registro de Campesinos")
        
        layout.addWidget(tabs)
        
    def init_tab_compras(self, tab):
        layout = QVBoxLayout(tab)
        
        # Label para mostrar el precio del mercado
        self.label_precio_mercado = QLabel("Cargando precio del mercado...")
        self.label_precio_mercado.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: #2c3e50;
                padding: 10px;
                background-color: white;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.label_precio_mercado)
        
        # Formulario de compra
        form_group = QGroupBox("Registro de Compra")
        form_layout = QFormLayout()
        
        # Búsqueda y selección del campesino
        busqueda_layout = QHBoxLayout()
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText("🔍 Buscar por nombre o cédula...")
        self.busqueda.textChanged.connect(self.filtrar_campesinos)
        busqueda_layout.addWidget(self.busqueda)
        
        self.combo_campesino = QComboBox()
        self.combo_campesino.setMinimumWidth(300)
        busqueda_layout.addWidget(self.combo_campesino)
        
        form_layout.addRow("Campesino:", busqueda_layout)
        
        # Datos de la compra
        self.cantidad = QDoubleSpinBox()
        self.cantidad.setMaximum(10000)
        self.precio_kg = QDoubleSpinBox()
        self.precio_kg.setMaximum(100000)
        self.total = QLineEdit()
        self.total.setReadOnly(True)
        
        form_layout.addRow("Cantidad (kg):", self.cantidad)
        form_layout.addRow("Precio por kg:", self.precio_kg)
        form_layout.addRow("Total:", self.total)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_registrar = QPushButton("💾 Registrar Compra")
        self.btn_cancelar = QPushButton("❌ Cancelar")
        btn_layout.addWidget(self.btn_registrar)
        btn_layout.addWidget(self.btn_cancelar)
        
        # Tabla de compras recientes
        self.tabla_compras = QTableWidget()
        self.tabla_compras.setColumnCount(7)
        self.tabla_compras.setHorizontalHeaderLabels([
            "ID", "Campesino", "Cantidad (kg)", "Precio/kg", 
            "Total", "Fecha", "Estado"
        ])
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Últimas Compras"))
        layout.addWidget(self.tabla_compras)
        
        # Conectar señales
        self.btn_registrar.clicked.connect(self.registrar_compra)
        self.btn_cancelar.clicked.connect(self.limpiar_formulario)
        self.cantidad.valueChanged.connect(self.calcular_total)
        self.precio_kg.valueChanged.connect(self.calcular_total)
        
        # Cargar datos iniciales
        self.cargar_campesinos()
        self.actualizar_precio_mercado()
        self.cargar_compras()
        
    def init_tab_campesinos(self, tab):
        layout = QVBoxLayout(tab)
        
        # Formulario de registro de campesino
        form_group = QGroupBox("Registro de Campesino")
        form_layout = QFormLayout()
        
        # Campos del formulario
        self.nombre = QLineEdit()
        self.apellido = QLineEdit()
        self.cedula = QLineEdit()
        self.telefono = QLineEdit()
        self.direccion = QLineEdit()
        
        form_layout.addRow("Nombre:", self.nombre)
        form_layout.addRow("Apellido:", self.apellido)
        form_layout.addRow("Cédula:", self.cedula)
        form_layout.addRow("Teléfono:", self.telefono)
        form_layout.addRow("Dirección:", self.direccion)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("💾 Guardar Campesino")
        self.btn_limpiar = QPushButton("🔄 Limpiar")
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_limpiar)
        form_layout.addRow("", btn_layout)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Tabla de campesinos
        self.tabla_campesinos = QTableWidget()
        self.tabla_campesinos.setColumnCount(6)
        self.tabla_campesinos.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "Cédula", "Teléfono", "Dirección"
        ])
        layout.addWidget(QLabel("Lista de Campesinos"))
        layout.addWidget(self.tabla_campesinos)
        
        # Conectar señales de los botones
        self.btn_guardar.clicked.connect(self.guardar_campesino)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario_campesino)
        
        # Cargar datos iniciales
        self.cargar_tabla_campesinos()
        
    def cargar_campesinos(self):
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, nombre, apellido, documento_identidad 
                        FROM proveedores 
                        ORDER BY nombre, apellido
                    """)
                    self.campesinos = cur.fetchall()
                    self.actualizar_combo_campesinos(self.campesinos)
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar campesinos: {str(e)}")
            
    def actualizar_combo_campesinos(self, campesinos):
        self.combo_campesino.clear()
        for campesino in campesinos:
            self.combo_campesino.addItem(
                f"{campesino['nombre']} {campesino['apellido']} - {campesino['documento_identidad']}",
                campesino['id']
            )
            
    def filtrar_campesinos(self):
        texto_busqueda = self.busqueda.text().lower()
        if not texto_busqueda:
            self.actualizar_combo_campesinos(self.campesinos)
            return
            
        campesinos_filtrados = [
            c for c in self.campesinos
            if texto_busqueda in c['nombre'].lower() or
               texto_busqueda in c['apellido'].lower() or
               texto_busqueda in c['documento_identidad'].lower()
        ]
        self.actualizar_combo_campesinos(campesinos_filtrados)
            
    def registrar_compra(self):
        try:
            # Obtener los datos del formulario
            campesino_id = self.combo_campesino.currentData()
            cantidad = self.cantidad.value()
            precio = self.precio_kg.value()
            total = cantidad * precio
            
            if not campesino_id or cantidad <= 0 or precio <= 0:
                self.mostrar_mensaje("Error", "Todos los campos son obligatorios")
                return
            
            # Conectar con la base de datos
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    # Insertar la compra
                    cur.execute("""
                        INSERT INTO compras (proveedor_id, usuario_id, cantidad_kg,
                                           precio_kg, total, estado_pago)
                        VALUES (%s, %s, %s, %s, %s, 'pendiente')
                        RETURNING id, fecha_compra
                    """, (campesino_id, self.user_id, cantidad, precio, total))
                    
                    result = cur.fetchone()
                    compra_id = result['id']
                    
                    # Actualizar inventario
                    cur.execute("""
                        INSERT INTO inventario_cafe (cantidad_kg, tipo_movimiento,
                                                   referencia_id, tipo_referencia, usuario_id)
                        VALUES (%s, 'entrada', %s, 'compra', %s)
                    """, (cantidad, compra_id, self.user_id))
                    
                    conn.commit()
                    
                    self.mostrar_mensaje("Éxito", "Compra registrada correctamente")
                    self.limpiar_formulario()
                    self.cargar_compras()
                    
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al registrar la compra: {str(e)}")

    def limpiar_formulario(self):
        self.busqueda.clear()
        self.cantidad.setValue(0)
        self.precio_kg.setValue(0)
        self.total.clear()
        
    def calcular_total(self):
        cantidad = self.cantidad.value()
        precio = self.precio_kg.value()
        total = cantidad * precio
        self.total.setText(f"{total:.2f}")
        
    def actualizar_precio_mercado(self):
        precio_actual = self.coffee_api.get_current_price()
        if precio_actual and not precio_actual.get('error', False):
            self.precio_kg.setValue(precio_actual['precio'])
            self.label_precio_mercado.setText(
                f"Precio del mercado: ${precio_actual['precio']:.2f}/kg\n"
                f"Actualizado: {precio_actual['fecha'].strftime('%Y-%m-%d %H:%M')}"
            )
        else:
            self.label_precio_mercado.setText("Error al obtener el precio del mercado")

    def cargar_compras(self):
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT c.*, p.nombre as proveedor_nombre, 
                               p.apellido as proveedor_apellido
                        FROM compras c
                        JOIN proveedores p ON c.proveedor_id = p.id
                        ORDER BY c.fecha_compra DESC
                        LIMIT 10
                    """)
                    compras = cur.fetchall()
                    
                    self.tabla_compras.setRowCount(len(compras))
                    for i, compra in enumerate(compras):
                        self.tabla_compras.setItem(i, 0, QTableWidgetItem(str(compra['id'])))
                        self.tabla_compras.setItem(i, 1, QTableWidgetItem(f"{compra['proveedor_nombre']} {compra['proveedor_apellido']}"))
                        self.tabla_compras.setItem(i, 2, QTableWidgetItem(f"{compra['cantidad_kg']:.2f}"))
                        self.tabla_compras.setItem(i, 3, QTableWidgetItem(f"{compra['precio_kg']:.2f}"))
                        self.tabla_compras.setItem(i, 4, QTableWidgetItem(f"{compra['total']:.2f}"))
                        self.tabla_compras.setItem(i, 5, QTableWidgetItem(str(compra['fecha_compra'])))
                        self.tabla_compras.setItem(i, 6, QTableWidgetItem(compra['estado_pago']))
                        
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar compras: {str(e)}")

    def mostrar_mensaje(self, titulo, mensaje):
        QMessageBox.information(self, titulo, mensaje)

    def guardar_campesino(self):
        try:
            # Obtener datos del formulario
            nombre = self.nombre.text()
            apellido = self.apellido.text()
            cedula = self.cedula.text()
            telefono = self.telefono.text()
            direccion = self.direccion.text()
            
            if not all([nombre, apellido, cedula, telefono, direccion]):
                self.mostrar_mensaje("Error", "Todos los campos son obligatorios")
                return
            
            # Conectar con la base de datos
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    # Verificar si ya existe el campesino
                    cur.execute("""
                        SELECT id FROM proveedores 
                        WHERE documento_identidad = %s
                    """, (cedula,))
                    
                    if cur.fetchone():
                        self.mostrar_mensaje("Error", "Ya existe un campesino con esta cédula")
                        return
                    
                    # Insertar nuevo campesino
                    cur.execute("""
                        INSERT INTO proveedores (nombre, apellido, documento_identidad,
                                               telefono, direccion, creado_por)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (nombre, apellido, cedula, telefono, direccion, self.user_id))
                    
                    conn.commit()
                    
                    self.mostrar_mensaje("Éxito", "Campesino registrado correctamente")
                    self.limpiar_formulario_campesino()
                    self.cargar_campesinos()
                    
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al registrar campesino: {str(e)}")

    def limpiar_formulario_campesino(self):
        self.nombre.clear()
        self.apellido.clear()
        self.cedula.clear()
        self.telefono.clear()
        self.direccion.clear()

    def cargar_tabla_campesinos(self):
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, nombre, apellido, documento_identidad, telefono, direccion
                        FROM proveedores
                        ORDER BY nombre, apellido
                    """)
                    campesinos = cur.fetchall()
                    
                    self.tabla_campesinos.setRowCount(len(campesinos))
                    for i, campesino in enumerate(campesinos):
                        self.tabla_campesinos.setItem(i, 0, QTableWidgetItem(str(campesino['id'])))
                        self.tabla_campesinos.setItem(i, 1, QTableWidgetItem(campesino['nombre']))
                        self.tabla_campesinos.setItem(i, 2, QTableWidgetItem(campesino['apellido']))
                        self.tabla_campesinos.setItem(i, 3, QTableWidgetItem(campesino['documento_identidad']))
                        self.tabla_campesinos.setItem(i, 4, QTableWidgetItem(campesino['telefono']))
                        self.tabla_campesinos.setItem(i, 5, QTableWidgetItem(campesino['direccion']))
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar campesinos: {str(e)}")